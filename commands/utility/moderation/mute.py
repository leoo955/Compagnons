from discord.ext import commands
from discord import app_commands, Interaction, Member
import discord

class Mute(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="mute", description="Rendre muet un membre (timeout)")
    @commands.has_permissions(administrator=True)
    @app_commands.default_permissions(moderate_members=True)
    async def mute(self, interaction: Interaction, member: Member, duration: int, reason: str = "Aucune raison fournie"):
        try:
            await member.timeout(discord.utils.utcnow() + discord.timedelta(minutes=duration), reason=reason)
            await interaction.response.send_message(f"{member} a été mute pour {duration} minutes. Raison : {reason}")
        except Exception as e:
            await interaction.response.send_message(f"Erreur : {e}")

async def setup(bot):
    await bot.add_cog(Mute(bot))
