from discord.ext import commands
from discord import app_commands, Interaction, Member

class Kick(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="kick", description="Expulser un membre du serveur")
    @commands.has_permissions(administrator=True)
    @app_commands.default_permissions(kick_members=True)
    async def kick(self, interaction: Interaction, member: Member, reason: str = "Aucune raison fournie"):
        await member.kick(reason=reason)
        await interaction.response.send_message(f"{member} a été expulsé. Raison : {reason}")

async def setup(bot):
    await bot.add_cog(Kick(bot))
