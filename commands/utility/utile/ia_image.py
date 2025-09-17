import os
import discord
from discord.ext import commands
from huggingface_hub import InferenceClient
from io import BytesIO

# Client HuggingFace
client_hf = InferenceClient(
    token=os.getenv("HF_TOKEN")  # Assure-toi que ton .env contient HF_TOKEN
)

class ImageGen(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="img", help="Génère une image à partir d'un prompt texte")
    async def img(self, ctx: commands.Context, *, prompt: str):
        """Commande classique (préfixe uniquement) pour générer une image"""
        try:
            # Génération de l'image (renvoie déjà un PIL.Image)
            image = client_hf.text_to_image(
                prompt,
                model="stabilityai/stable-diffusion-xl-base-1.0"
            )

            # Conversion en bytes pour Discord
            img_bytes = BytesIO()
            image.save(img_bytes, format="PNG")
            img_bytes.seek(0)
            file = discord.File(img_bytes, filename="image.png")

            # Embed
            embed = discord.Embed(
                title="🖼️ Image générée",
                description=f"Prompt : `{prompt}`",
                color=discord.Color.blue()
            )
            embed.set_image(url="attachment://image.png")

            await ctx.send(embed=embed, file=file)

        except Exception as e:
            await ctx.send(f"❌ Erreur lors de la génération de l'image : {e}")

async def setup(bot):
    await bot.add_cog(ImageGen(bot))
