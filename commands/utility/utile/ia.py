import os
import discord # type: ignore
from discord.ext import commands # type: ignore
from openai import OpenAI # type: ignore

# Client HuggingFace via OpenAI wrapper
client = OpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key=os.environ["HF_TOKEN"],  # ton token HF dans .env
)

async def send_long_message(channel, content: str):
    for i in range(0, len(content), 2000):
        await channel.send(content[i:i+2000])

class IA(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="ia", description="Pose une question à l'IA")
    async def ask(self, ctx, *, question: str):
        """Pose une question à l'IA"""
        try:
            async with ctx.typing():
                completion = client.chat.completions.create(
                    model="openai/gpt-oss-20b:together",
                    messages=[
                        {"role": "user", "content": question}
                    ],
                )

              
                response = completion.choices[0].message.content

            await send_long_message(ctx.channel, f"💡 Réponse : {response}")

        except Exception as e:
            await ctx.send(f"❌ Erreur lors de la génération de la réponse : {e}")

async def setup(bot):
    await bot.add_cog(IA(bot))
