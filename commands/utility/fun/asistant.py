import discord
from discord.ext import commands
import os
from gtts import gTTS
from openai import OpenAI
import tempfile

# Client HuggingFace (IA via OpenAI wrapper)
client = OpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key=os.environ["HF_TOKEN"],  # mets ton token HF dans .env
)

class VoiceAssistant(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.assistant_active = False  # par défaut inactif

    @commands.command()
    async def startassistant(self, ctx):
        """Active le mode assistant vocal"""
        self.assistant_active = True
        await ctx.send("🎙️ Assistant vocal **activé**. Utilise `!ask <ta question>` pour parler avec moi.")

    @commands.command()
    async def stopassistant(self, ctx):
        """Désactive le mode assistant vocal"""
        self.assistant_active = False
        await ctx.send("🛑 Assistant vocal **désactivé**.")

    @commands.command()
    async def ask(self, ctx, *, question: str):
        """Pose une question à l’IA et le bot répond en vocal"""
        if not self.assistant_active:
            return await ctx.send("❌ L’assistant n’est pas activé. Lance `!startassistant` d’abord.")

        if not ctx.voice_client:
            return await ctx.send("❌ Je dois déjà être connecté à un salon vocal.")

        await ctx.send(f"🤔 Question : {question}")

        # IA (HuggingFace Mistral)
        try:
            completion = client.chat.completions.create(
                model="mistralai/Mistral-7B-Instruct-v0.2:featherless-ai",
                messages=[{"role": "user", "content": question}],
                max_tokens=300,
            )
            response = completion.choices[0].message.content
        except Exception as e:
            return await ctx.send(f"❌ Erreur IA : {e}")

        await ctx.send(f"💡 Réponse : {response}")

        # Convertir en voix
        try:
            tts = gTTS(response, lang="fr")
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
                tts.save(f.name)
                filename = f.name
        except Exception as e:
            return await ctx.send(f"❌ Erreur TTS : {e}")

        # Jouer en vocal
        try:
            ctx.voice_client.play(
                discord.FFmpegPCMAudio(filename),
                after=lambda e: os.remove(filename) if os.path.exists(filename) else None
            )
        except Exception as e:
            return await ctx.send(f"❌ Erreur audio : {e}")

async def setup(bot):
    await bot.add_cog(VoiceAssistant(bot))
