import discord
from discord.ext import commands
import os

class SlashManager(commands.Cog):
    """Gestion des slash commands"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    
    from dotenv import load_dotenv
    load_dotenv()  # <- ça lit le fichier .env

    GUILD_ID = os.getenv("GUILD_ID")

    

    @commands.command(name="clear_slash")
    @commands.is_owner()
    async def clear_slash(self, ctx: commands.Context):
        await ctx.send("🧹 Suppression des anciennes slash commands...")

        GUILD_ID = os.getenv("GUILD_ID")
        if GUILD_ID and GUILD_ID.strip() != "":
            guild = discord.Object(id=int(GUILD_ID))
            # Suppression et resync sur serveur de test
            await self.bot.tree.clear_commands(guild=guild)
            await self.bot.tree.sync(guild=guild)
            await ctx.send("✅ Anciennes slash commands supprimées pour le serveur de test.")
        else:
            # Suppression globale
            await self.bot.tree.clear_commands()
            await self.bot.tree.sync()
            await ctx.send("✅ Anciennes slash commands supprimées globalement.")

async def setup(bot: commands.Bot):
    await bot.add_cog(SlashManager(bot))
