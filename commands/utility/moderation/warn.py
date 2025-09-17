import discord
from discord.ext import commands
import json
import os

WARN_FILE = os.path.join("commands", "utility", "moderation", "warnings.json")

class Warn(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Si le fichier n’existe pas, on le crée avec un objet vide
        if not os.path.exists(WARN_FILE):
            with open(WARN_FILE, "w") as f:
                json.dump({}, f)

    def load_warnings(self):
        """Charge les avertissements depuis le fichier JSON"""
        if os.stat(WARN_FILE).st_size == 0:  # fichier vide
            return {}
        with open(WARN_FILE, "r") as f:
            return json.load(f)

    def save_warnings(self, data):
        """Sauvegarde les avertissements"""
        with open(WARN_FILE, "w") as f:
            json.dump(data, f, indent=4)

    @commands.command()
    async def warn(self, ctx, member: discord.Member, *, reason: str = "Aucune raison fournie"):
        """Donne un avertissement à un membre"""
        data = self.load_warnings()

        if str(member.id) not in data:
            data[str(member.id)] = []

        data[str(member.id)].append(reason)
        self.save_warnings(data)

        await ctx.send(f"⚠️ {member.mention} a été averti pour : **{reason}**")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def warnings(self, ctx, member: discord.Member):
        """Affiche les avertissements d’un membre"""
        data = self.load_warnings()

        if str(member.id) not in data or len(data[str(member.id)]) == 0:
            await ctx.send(f"{member.mention} n’a aucun avertissement.")
            return

        warnings_list = "\n".join([f"{i+1}. {reason}" for i, reason in enumerate(data[str(member.id)])])
        await ctx.send(f"⚠️ Avertissements de {member.mention} :\n{warnings_list}")

async def setup(bot):
    await bot.add_cog(Warn(bot))
