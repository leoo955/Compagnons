import discord
from discord.ext import commands
from discord import app_commands


class CustomHelp(commands.MinimalHelpCommand):
    async def send_bot_help(self, mapping):
        embed = discord.Embed(
            title="📖 Commandes disponibles",
            description="Voici la liste des commandes du bot, triées par catégorie :\n",
            color=discord.Color.blurple()
        )

        for cog, commands_list in mapping.items():
            filtered = await self.filter_commands(commands_list, sort=True)
            if not filtered:
                continue

            cog_name = cog.qualified_name if cog else "Autres"
            value = "\n".join(
                [f"• **{c.name}** → {c.help or 'Pas de description'}" for c in filtered]
            )
            embed.add_field(name=f"📂 {cog_name}", value=value, inline=False)

        embed.set_footer(text="Tape !help <commande> pour plus de détails.")
        await self.get_destination().send(embed=embed)

    async def send_command_help(self, command):
        embed = discord.Embed(
            title=f"❓ Aide pour `{command.name}`",
            description=command.help or "Pas de description fournie.",
            color=discord.Color.green()
        )
        if command.aliases:
            embed.add_field(name="Alias", value=", ".join(command.aliases), inline=False)
        if command.usage:
            embed.add_field(name="Utilisation", value=f"`{command.usage}`", inline=False)
        await self.get_destination().send(embed=embed)

    async def send_cog_help(self, cog):
        embed = discord.Embed(
            title=f"📂 Catégorie : {cog.qualified_name}",
            description=cog.__doc__ or "Pas de description fournie.",
            color=discord.Color.orange()
        )
        filtered = await self.filter_commands(cog.get_commands(), sort=True)
        for command in filtered:
            embed.add_field(
                name=f"• {command.name}",
                value=command.help or "Pas de description.",
                inline=False
            )
        await self.get_destination().send(embed=embed)


class HelpCog(commands.Cog):
    """Commandes d'aide hybrides pour le bot."""
    
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="help", description="Affiche l'aide du bot")
    @app_commands.describe(command="La commande pour laquelle obtenir de l'aide")
    async def help_command(self, ctx, *, command: str = None):
        """Commande d'aide hybride."""
        if command:
            # Aide pour une commande spécifique
            cmd = self.bot.get_command(command)
            if cmd:
                await ctx.bot.help_command.send_command_help(cmd)
            else:
                await ctx.send(f"❌ Commande `{command}` introuvable.")
        else:
            # Aide générale
            mapping = self.bot.help_command.get_bot_mapping()
            await ctx.bot.help_command.send_bot_help(mapping)


# ⚡ setup pour extension
async def setup(bot: commands.Bot):
    bot.help_command = CustomHelp()
    await bot.add_cog(HelpCog(bot))