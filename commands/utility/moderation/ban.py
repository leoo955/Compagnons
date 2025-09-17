from discord.ext import commands
from discord import app_commands, Interaction, Member

class Ban(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ban", description="Bannir un membre du serveur")
    @commands.has_permissions(administrator=True)
    @app_commands.default_permissions(ban_members=True)
    async def ban(self, interaction: Interaction, member: Member, reason: str = "Aucune raison fournie"):
        await member.ban(reason=reason)
        await interaction.response.send_message(f"{member} a été banni. Raison : {reason}")

async def setup(bot):
    await bot.add_cog(Ban(bot))
