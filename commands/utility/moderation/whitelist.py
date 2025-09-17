import discord
from discord.ext import commands
import json
import os

WHITELIST_FILE = "whitelist.json"

def load_whitelist():
    if os.path.exists(WHITELIST_FILE):
        with open(WHITELIST_FILE, "r") as f:
            return set(json.load(f))
    return set()

def save_whitelist(whitelist):
    with open(WHITELIST_FILE, "w") as f:
        json.dump(list(whitelist), f, indent=4)

class Whitelist(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.whitelist = load_whitelist()
        # Ajoute le check global
        bot.add_check(self.global_check)
        # Ajoute un handler d’erreur global
        bot.add_listener(self.on_command_error)

    def is_allowed(self, user_id: int):
        ownership_cog = self.bot.get_cog("Ownership")
        if ownership_cog and ownership_cog.is_owner(user_id):
            return True  # Owners/co-owners toujours autorisés
        return user_id in self.whitelist

    async def global_check(self, ctx: commands.Context):
        return self.is_allowed(ctx.author.id)

    async def on_command_error(self, ctx, error):
        """Message d’erreur personnalisé quand l’utilisateur n’est pas whitelist"""
        if isinstance(error, commands.CheckFailure):
            await ctx.send("❌ Tu n’es pas whitelist.")
        else:
            raise error  # On laisse les autres erreurs normales passer

    @commands.command()
    async def botadd(self, ctx, user: discord.User):
        """Ajoute un utilisateur à la whitelist"""
        ownership_cog = self.bot.get_cog("Ownership")
        if not (ownership_cog and ownership_cog.is_owner(ctx.author.id)):
            return await ctx.send("❌ Tu n’as pas la permission d’ajouter des utilisateurs.")

        if user.id in self.whitelist:
            return await ctx.send(f"⚠️ {user} est déjà whitelist.")

        self.whitelist.add(user.id)
        save_whitelist(self.whitelist)
        await ctx.send(f"✅ {user} peut maintenant utiliser le bot.")

    @commands.command()
    async def botremove(self, ctx, user: discord.User):
        """Retire un utilisateur de la whitelist"""
        ownership_cog = self.bot.get_cog("Ownership")
        if not (ownership_cog and ownership_cog.is_owner(ctx.author.id)):
            return await ctx.send("❌ Tu n’as pas la permission de retirer des utilisateurs.")

        if user.id not in self.whitelist:
            return await ctx.send(f"⚠️ {user} n’est pas whitelist.")

        self.whitelist.remove(user.id)
        save_whitelist(self.whitelist)
        await ctx.send(f"✅ {user} ne peut plus utiliser le bot.")

    @commands.command()
    async def botlist(self, ctx):
        """Liste les utilisateurs whitelist (sans ping)"""
        members = []
        for uid in self.whitelist:
            member = ctx.guild.get_member(uid)
            if member:
                members.append(f"{member.name}#{member.discriminator}")
            else:
                members.append(f"ID:{uid}")

        embed = discord.Embed(
            title="📜 Utilisateurs whitelist",
            description="\n".join(members) if members else "Aucun utilisateur whitelist",
            color=discord.Color.blue()
        )
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Whitelist(bot))
