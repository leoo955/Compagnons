import discord
from discord.ext import commands
from collections import defaultdict
from datetime import datetime, timedelta

class AntiSpam(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.user_messages = defaultdict(list)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        now = datetime.utcnow()
        self.user_messages[message.author.id].append(now)

        # Nettoie les messages de plus de 5 secondes
        self.user_messages[message.author.id] = [
            t for t in self.user_messages[message.author.id] if t > now - timedelta(seconds=5)
        ]

        if len(self.user_messages[message.author.id]) > 5:
            try:
                await message.delete()
                embed = discord.Embed(
                    description=f"⚠️ {message.author.mention}, stop le spam !",
                    color=discord.Color.orange()
                )
                await message.channel.send(embed=embed, delete_after=5)
            except:
                pass

async def setup(bot):
    await bot.add_cog(AntiSpam(bot))
    