import discord
from discord.ext import commands
import os
import traceback
import logging
import asyncio
from typing import Optional
from core import config

# Configuration du logging plus robuste
def setup_logging():
    """Configure le système de logging avec rotation des fichiers."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('bot.log', encoding='utf-8'),
            logging.StreamHandler()
        ]
    )

setup_logging()
logger = logging.getLogger("bot")

# Configuration des intents plus précise
def get_intents() -> discord.Intents:
    """Configure les intents nécessaires pour le bot."""
    intents = discord.Intents.default()
    intents.members = True
    intents.message_content = True
    # Ajoute d'autres intents seulement si nécessaire
    # intents.presences = True  # Décommente si besoin
    return intents

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=self._get_prefix,
            intents=get_intents(),
            help_command=None,
            case_insensitive=True,  # Commandes insensibles à la casse
            strip_after_prefix=True  # Supprime les espaces après le préfixe
        )
        self.initial_extensions = []
        self.startup_time = None

    async def _get_prefix(self, bot, message) -> list[str]:
        """Préfixes dynamiques selon le serveur."""
        # Tu peux ajouter une logique pour différents préfixes par serveur
        return commands.when_mentioned_or("!", "?")(bot, message)

    async def setup_hook(self):
        """Hook d'initialisation du bot."""
        logger.info("🔹 Démarrage du chargement des cogs...")
        self.startup_time = discord.utils.utcnow()
        
        # Chargement des extensions
        await self._load_extensions()
        
        # Synchronisation des slash commands
        await self._sync_commands()

    async def _load_extensions(self) -> tuple[int, int]:
        """Charge toutes les extensions depuis le dossier commands."""
        cogs_found = 0
        cogs_loaded = 0
        failed_cogs = []

        for root, _, files in os.walk("./commands"):
            for file in files:
                if not file.endswith(".py") or file.startswith("_"):
                    continue

                # Conversion du chemin en module Python
                rel_path = os.path.relpath(os.path.join(root, file), "commands")
                module_name = os.path.splitext(rel_path)[0].replace(os.sep, ".")
                ext = f"commands.{module_name}"
                
                cogs_found += 1
                logger.info(f"🔹 Tentative de chargement : {ext}")
                
                try:
                    await self.load_extension(ext)
                    cogs_loaded += 1
                    self.initial_extensions.append(ext)
                    logger.info(f"✅ Cog chargé : {ext}")
                except Exception as e:
                    failed_cogs.append((ext, e))
                    logger.error(f"❌ Erreur chargement {ext} : {type(e).__name__}: {e}")
                    if logger.isEnabledFor(logging.DEBUG):
                        traceback.print_exc()

        # Rapport de chargement
        logger.info(f"📊 Résumé : {cogs_loaded}/{cogs_found} cogs chargés avec succès.")
        if failed_cogs:
            logger.warning(f"⚠️ Cogs échoués : {', '.join(cog[0] for cog in failed_cogs)}")

        return cogs_loaded, cogs_found

    async def _sync_commands(self):
        """Synchronise les slash commands."""
        try:
            if hasattr(config, 'GUILD_ID') and config.GUILD_ID:
                guild = discord.Object(id=config.GUILD_ID)
                synced = await self.tree.sync(guild=guild)
                logger.info(f"✅ {len(synced)} slash commands synchronisées sur le serveur de test.")
            else:
                synced = await self.tree.sync()
                logger.info(f"✅ {len(synced)} slash commands synchronisées globalement.")
        except discord.HTTPException as e:
            logger.error(f"❌ Erreur HTTP lors de la sync : {e}")
        except Exception as e:
            logger.error(f"❌ Erreur sync slash : {type(e).__name__}: {e}")
            if logger.isEnabledFor(logging.DEBUG):
                traceback.print_exc()

    async def on_ready(self):
        """Événement déclenché quand le bot est prêt."""
        uptime = (discord.utils.utcnow() - self.startup_time).total_seconds()
        logger.info(f"✅ Bot connecté : {self.user} (ID: {self.user.id})")
        logger.info(f"📊 Temps de démarrage : {uptime:.2f}s")
        logger.info(f"🔧 Cogs chargés : {', '.join(self.cogs.keys()) or 'Aucun'}")
        logger.info(f"🌐 Serveurs : {len(self.guilds)} | Utilisateurs : {len(self.users)}")

    async def on_command_error(self, ctx, error):
        """Gestionnaire d'erreurs global pour les commandes."""
        # Ignore les erreurs de commandes non trouvées
        if isinstance(error, commands.CommandNotFound):
            return

        # Log des erreurs importantes
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"❌ Argument manquant : `{error.param.name}`")
        elif isinstance(error, commands.BadArgument):
            await ctx.send("❌ Argument invalide. Vérifiez votre syntaxe.")
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ Vous n'avez pas les permissions nécessaires.")
        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send("❌ Le bot n'a pas les permissions nécessaires.")
        else:
            # Erreur inattendue
            logger.error(f"Erreur dans la commande {ctx.command}: {type(error).__name__}: {error}")
            await ctx.send("❌ Une erreur inattendue s'est produite.")

    async def reload_cog(self, cog_name: str) -> bool:
        """Recharge un cog spécifique."""
        try:
            await self.reload_extension(cog_name)
            logger.info(f"🔄 Cog rechargé : {cog_name}")
            return True
        except Exception as e:
            logger.error(f"❌ Erreur rechargement {cog_name} : {e}")
            return False

    async def close(self):
        """Nettoyage avant fermeture."""
        logger.info("🔹 Fermeture du bot...")
        await super().close()

def main():
    """Point d'entrée principal."""
    logger.info("🔹 Lancement du bot...")
    
    # Vérification du token
    token = getattr(config, 'DISCORD_TOKEN', os.getenv('DISCORD_TOKEN'))
    if not token:
        raise RuntimeError(
            "DISCORD_TOKEN manquant. Ajoutez-le dans config.py ou comme variable d'environnement."
        )

    # Création et lancement du bot
    bot = MyBot()
    
    try:
        bot.run(token, log_handler=None)  # On gère nous-mêmes le logging
    except KeyboardInterrupt:
        logger.info("🔹 Arrêt demandé par l'utilisateur.")
    except discord.LoginFailure:
        logger.error("❌ Token Discord invalide.")
    except Exception as e:
        logger.error(f"❌ Erreur critique : {type(e).__name__}: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()