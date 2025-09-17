from discord.ext import commands
from discord import app_commands, Interaction, Member

class Unmute(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="unmute", description="Retirer le mute d’un membre")
    @commands.has_permissions(administrator=True)
    @app_commands.default_permissions(moderate_members=True)
    async def unmute(self, interaction: Interaction, member: Member):
        await member.timeout(None)
        await interaction.response.send_message(f"{member} n’est plus mute.")

async def setup(bot):
    await bot.add_cog(Unmute(bot))
