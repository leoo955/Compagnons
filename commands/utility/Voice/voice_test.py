import discord
from discord.ext import commands
from discord import app_commands
from gtts import gTTS
import os
import yt_dlp
from discord import Activity, ActivityType
from discord import FFmpegPCMAudio, PCMVolumeTransformer
import asyncio
import json

BLACKLIST_FILE = "blacklist.json"

def load_blacklist():
    if os.path.exists(BLACKLIST_FILE):
        with open(BLACKLIST_FILE, "r") as f:
            return set(json.load(f))
    return set()

def save_blacklist(banned_users):
    with open(BLACKLIST_FILE, "w") as f:
        json.dump(list(banned_users), f, indent=4)

class Voice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.loop = False
        self.queue = []
        self.current_audio_url = None
        self.current_title = None
        self.volume = 0.5
        self.is_playing = False
        self.banned_users = load_blacklist()

    # --- Check globale ---
      # --- Check globale pour le cog ---
    async def check_commands(self, ctx):
        # TTS toujours autorisé
        if ctx.command.name == "tts":
            return True
        if ctx.author.id in self.banned_users:
            await ctx.send("🚫 Tu es banni du bot, cette commande est bloquée.")
            return False
        return True

    # Discord.py appelle automatiquement `cog_check` interne
    def cog_check(self, ctx):
        return self.check_commands(ctx)

    # --- Rejoindre ---
    @commands.hybrid_command(name="tjoin", description="Fait rejoindre un salon vocal au bot avec l'ID du salon.")
    async def tjoin(self, ctx, channel_id: int):
        """Fait rejoindre un salon vocal au bot avec l'ID du salon."""
        channel = ctx.guild.get_channel(channel_id)

        if channel is None or not isinstance(channel, discord.VoiceChannel):
            return await ctx.send("❌ Salon introuvable ou ce n'est pas un salon vocal.")

        if ctx.voice_client is not None:
            await ctx.voice_client.move_to(channel)
            await ctx.send(f"🔄 Le bot a été déplacé dans {channel.mention}")
        else:
            await channel.connect()
            await ctx.send(f"✅ Le bot a rejoint {channel.mention}")
    # --- Quitter ---
    @commands.hybrid_command(name="tleave", description="Fait quitter le salon")
    async def tleave(self, ctx):
        if ctx.voice_client:
            await ctx.voice_client.disconnect()
            await ctx.send("✅ Je quitte le canal vocal.")
            self.queue.clear()
            self.is_playing = False
        else:
            await ctx.send("❌ Je ne suis pas dans un canal vocal.")

    # --- TTS ---
    @commands.hybrid_command(name="tts", description="Parler dans le salon vocal")
    async def tts(self, ctx, *, message):
        if ctx.voice_client is None:
            await ctx.invoke(self.bot.get_command("tjoin"))

        tts_file = "tts.mp3"
        gTTS(message, lang="fr").save(tts_file)

        def after_playing(error):
            if os.path.exists(tts_file):
                os.remove(tts_file)

        vc = ctx.voice_client
        if vc.is_playing():
            vc.stop()
        vc.play(PCMVolumeTransformer(FFmpegPCMAudio(tts_file), volume=self.volume), after=after_playing)
        await ctx.send(f"🗣️ Joue : {message}")

    # --- Ajouter à la queue ---
    @commands.hybrid_command()
    async def play(self, ctx, url: str):
        if ctx.voice_client is None:
            await ctx.invoke(self.bot.get_command("tjoin"))

        ydl_opts = {'format': 'bestaudio/best', 'quiet': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            duration = info.get("duration", 0)
            title = info.get("title", "Unknown")

        if duration > 3600:
            await ctx.message.add_reaction("🖕")
            await ctx.send(f"❌ La vidéo **{title}** dépasse 1h et ne sera pas jouée.")
            return

        self.queue.append({"url": url, "title": title})
        await ctx.send(f"✅ Ajouté à la file : **{title}**")

        if not self.is_playing:
            asyncio.create_task(self.start_queue(ctx))

    # --- Lecture queue ---
    async def start_queue(self, ctx):
        if not self.queue:
            self.is_playing = False
            await self.bot.change_presence(activity=None)
            return

        self.is_playing = True
        song = self.queue.pop(0)
        self.current_title = song["title"]

        ydl_opts = {'format': 'bestaudio/best', 'quiet': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(song["url"], download=False)
            self.current_audio_url = info['url']

        vc = ctx.voice_client

        def after_playing(error):
            if self.loop:
                self.queue.insert(0, song)
            asyncio.run_coroutine_threadsafe(self.start_queue(ctx), self.bot.loop)

        vc.play(PCMVolumeTransformer(FFmpegPCMAudio(self.current_audio_url), volume=self.volume), after=after_playing)
        await self.bot.change_presence(activity=Activity(type=ActivityType.listening, name=self.current_title))
        await ctx.send(f"🎵 Lecture : {self.current_title}")

    # --- Boucle ---
    @commands.hybrid_command()
    async def loop(self, ctx):
        self.loop = not self.loop
        await ctx.send(f"🔁 Boucle {'activée' if self.loop else 'désactivée'}.")

    # --- Stop ---
    @commands.hybrid_command()
    async def stop(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.stop()
            self.queue.clear()
            self.is_playing = False
            await ctx.send("⏹️ Musique arrêtée et file vidée.")
        else:
            await ctx.send("❌ Rien n'est en lecture.")

    # --- Pause ---
    @commands.hybrid_command()
    async def pause(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.pause()
            await ctx.send("⏸️ Musique en pause.")
        else:
            await ctx.send("❌ Rien n'est en lecture.")

    # --- Resume ---
    @commands.hybrid_command()
    async def resume(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_paused():
            ctx.voice_client.resume()
            await ctx.send("▶️ Musique reprise.")
        else:
            await ctx.send("❌ Rien n'est en pause.")

    # --- Volume ---
    @commands.hybrid_command()
    async def volume(self, ctx, level: int):
        if 0 <= level <= 100:
            self.volume = level / 100
            vc = ctx.voice_client
            if vc and vc.source and isinstance(vc.source, PCMVolumeTransformer):
                vc.source.volume = self.volume
            await ctx.send(f"🔊 Volume réglé à {level}%")
        else:
            await ctx.send("❌ Le volume doit être entre 0 et 100.")

async def setup(bot):
    await bot.add_cog(Voice(bot))