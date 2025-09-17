import discord
from discord.ext import commands
import os
import asyncio
import wave
import numpy as np
import whisper
from gtts import gTTS

# Charge Whisper (modèle "small" pour rapidité, tu peux mettre "base", "medium", "large")
whisper_model = whisper.load_model("small")

class VoiceAI(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.listening = False

    # Commande pour rejoindre un salon vocal
    @commands.command(name="join")
    async def join_ai(self, ctx):
        if ctx.author.voice is None:
            return await ctx.send("❌ Tu dois être dans un salon vocal.")
        
        channel = ctx.author.voice.channel
        if ctx.voice_client is not None:
            await ctx.voice_client.move_to(channel)
        else:
            await channel.connect()

        await ctx.send(f"✅ Connecté à {channel.mention} et prêt à écouter.")
        self.listening = True

        # Lancer la boucle d’écoute
        asyncio.create_task(self.listen_loop(ctx))

    # Commande pour quitter
    @commands.command(name="leave")
    async def leave_ai(self, ctx):
        if ctx.voice_client:
            await ctx.voice_client.disconnect()
            self.listening = False
            await ctx.send("👋 Déconnecté.")
        else:
            await ctx.send("❌ Je ne suis pas dans un salon vocal.")

    # Boucle d’écoute vocale
    async def listen_loop(self, ctx):
        vc: discord.VoiceClient = ctx.voice_client
        if not vc:
            return

        while self.listening and vc.is_connected():
            try:
                # Pycord permet d’écouter → récupère le flux brut d’un utilisateur
                audio = await vc.recv()  # bloc d’audio brut

                # Sauvegarde en fichier wav
                pcm_data = np.frombuffer(audio, dtype=np.int16)
                with wave.open("input.wav", "wb") as f:
                    f.setnchannels(2)
                    f.setsampwidth(2)
                    f.setframerate(48000)
                    f.writeframes(pcm_data.tobytes())

                # Transcription avec Whisper
                result = whisper_model.transcribe("input.wav", language="fr")
                text = result["text"].strip()
                if text:
                    await ctx.send(f"🗣️ **Transcrit** : {text}")

                    # Réponse en TTS
                    reply = f"Tu as dit : {text}"
                    tts_file = "reply.mp3"
                    gTTS(reply, lang="fr").save(tts_file)

                    if vc.is_playing():
                        vc.stop()
                    vc.play(discord.FFmpegPCMAudio(tts_file))

            except Exception as e:
                print("Erreur boucle écoute:", e)
                await asyncio.sleep(1)

async def setup(bot):
    await bot.add_cog(VoiceAI(bot))
