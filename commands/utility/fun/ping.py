from discord.ext import commands
from discord import app_commands

class Ping(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="ping", description="Vérifie la latence du bot")
    async def ping(self, interaction):
        await interaction.response.send_message(
            f"Pong! Latence : {round(self.bot.latency * 1000)} ms"
        )

# setup doit être une coroutine (async def) et retourner add_cog
async def setup(bot):
    await bot.add_cog(Ping(bot))
