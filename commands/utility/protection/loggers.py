import discord
from discord.ext import commands

class Logger(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def log(self, guild, message, color=discord.Color.blue()):
        channel = discord.utils.get(guild.text_channels, name="logs")
        if channel:
            embed = discord.Embed(description=message, color=color)
            await channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Logger(bot))
    