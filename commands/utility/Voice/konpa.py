import discord
from discord.ext import commands
import os

class Konpa(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="konpa")
    async def play_konpa(self, ctx):
        """Joue un fichier Konpa local dans le salon vocal"""
        if ctx.author.voice is None:
            await ctx.send("Tu dois être dans un salon vocal pour écouter Konpa !")
            return

        channel = ctx.author.voice.channel

        # Connecte le bot au salon si nécessaire
        voice_client = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        if not voice_client:
            voice_client = await channel.connect()
        elif voice_client.channel != channel:
            await voice_client.move_to(channel)

        # Chemin du fichier local (ex: dans un dossier 'music' à côté du bot)
        file_path = os.path.join("music", "audio [music].mp3")
        if not os.path.exists(file_path):
            await ctx.send("Le fichier Konpa n'existe pas !")
            return

        # Joue le fichier
        if not voice_client.is_playing():
            voice_client.play(discord.FFmpegPCMAudio(file_path), after=lambda e: print(f"Fin de la musique : {e}"))
            await ctx.send("🎵 Lecture de Konpa !")
        else:
            await ctx.send("Le bot est déjà en train de jouer de la musique !")

    @commands.command(name="stopkonpa")
    async def stop_konpa(self, ctx):
        """Arrête la musique et déconnecte le bot"""
        voice_client = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        if voice_client and voice_client.is_connected():
            await voice_client.disconnect()
            await ctx.send("⏹ Musique arrêtée et déconnecté du salon vocal.")
        else:
            await ctx.send("Le bot n'est pas connecté à un salon vocal.")

async def setup(bot):
    await bot.add_cog(Konpa(bot))

