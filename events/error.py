import discord
from discord.ext import commands

class ErrorHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        # Ignore les erreurs gérées ailleurs
        if hasattr(ctx.command, 'on_error'):
            return

        embed = discord.Embed(color=discord.Color.red())

        # Gestion des erreurs spécifiques
        if isinstance(error, commands.MissingRequiredArgument):
            embed.title = "❌ Argument manquant"
            embed.description = f"Il manque un argument pour la commande `{ctx.command}`."
        elif isinstance(error, commands.CommandNotFound):
            embed.title = "❌ Commande introuvable"
            embed.description = "Cette commande n'existe pas."
        elif isinstance(error, commands.MissingPermissions):
            embed.title = "❌ Permissions manquantes"
            embed.description = "Tu n'as pas les permissions nécessaires pour exécuter cette commande."
        elif isinstance(error, commands.BotMissingPermissions):
            embed.title = "❌ Permissions du bot manquantes"
            embed.description = "Le bot n'a pas les permissions nécessaires pour exécuter cette commande."
        elif isinstance(error, commands.BadArgument):
            embed.title = "❌ Argument invalide"
            embed.description = "Un ou plusieurs arguments fournis sont invalides."
        elif isinstance(error, commands.CommandOnCooldown):
            embed.title = "❌ Commande en cooldown"
            embed.description = f"Réessaie dans {error.retry_after:.1f}s."
        elif isinstance(error, commands.NoPrivateMessage):
            embed.title = "❌ Commande indisponible en DM"
            embed.description = "Cette commande ne peut pas être utilisée en message privé."
        elif isinstance(error, commands.CheckFailure):
            embed.title = "❌ Vérification échouée"
            embed.description = "Tu ne remplis pas les conditions nécessaires pour utiliser cette commande."
        elif isinstance(error, commands.UserInputError):
            embed.title = "❌ Erreur d'entrée utilisateur"
            embed.description = "La commande a reçu des arguments invalides."
        else:
            embed.title = "❌ Une erreur est survenue"
            embed.description = str(error)
            print(f"[ERREUR] Commande `{ctx.command}` a échoué dans {ctx.guild} par {ctx.author}: {error}")

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(ErrorHandler(bot))
