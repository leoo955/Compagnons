import discord
from discord.ext import commands, tasks
from collections import defaultdict
from datetime import datetime, timedelta

class AntiRaid(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.join_times = defaultdict(list)
        self.check_interval.start()

    @commands.Cog.listener()
    async def on_member_join(self, member):
        guild_id = member.guild.id
        now = datetime.utcnow()
        self.join_times[guild_id].append(now)

        # Garde seulement les derniers 10 joins
        self.join_times[guild_id] = [
            t for t in self.join_times[guild_id] if t > now - timedelta(seconds=10)
        ]

        if len(self.join_times[guild_id]) > 5:  # trop de joins en 10s
            embed = discord.Embed(
                title="⚠️ Possible raid détecté !",
                description=f"Vérifiez les nouveaux membres sur **{member.guild.name}**.",
                color=discord.Color.red()
            )
            if member.guild.system_channel:
                await member.guild.system_channel.send(embed=embed)

    @tasks.loop(seconds=30)
    async def check_interval(self):
        pass

async def setup(bot):
    await bot.add_cog(AntiRaid(bot))
