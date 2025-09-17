from discord.ext import commands

class OnReady(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.bot.user} est en ligne et prêt !")

# setup doit être async et utiliser await
async def setup(bot):
    await bot.add_cog(OnReady(bot))
