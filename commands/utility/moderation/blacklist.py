import discord
from discord.ext import commands
import json
import os

BLACKLIST_FILE = "blacklist.json"
OWNER_ID = 1074814902683844810  # ton ID Discord

def load_blacklist():
    if os.path.exists(BLACKLIST_FILE):
        with open(BLACKLIST_FILE, "r") as f:
            return set(json.load(f))
    return set()

def save_blacklist(banned_users):
    with open(BLACKLIST_FILE, "w") as f:
        json.dump(list(banned_users), f, indent=4)

class BotBlacklist(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.banned_users = load_blacklist()

    # --- check globale pour toutes les commandes ---
    async def cog_check(self, ctx):
        if ctx.author.id in self.banned_users:
            embed = discord.Embed(
                title="🚫 Tu es banni du bot",
                description="Aucune commande ne peut être utilisée pour toi !",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return False
        return True

    # --- helper admin/owner ---
    def is_admin_or_owner(self, ctx):
        return ctx.author.id == OWNER_ID or ctx.author.guild_permissions.administrator

    # --- commande pour ban un utilisateur du bot ---
    @commands.command()
    async def botban(self, ctx, user: discord.User):
        if not self.is_admin_or_owner(ctx):
            embed = discord.Embed(
                title="❌ Permission refusée",
                description="Tu n’as pas la permission d’utiliser cette commande.",
                color=discord.Color.red()
            )
            return await ctx.send(embed=embed)

        if user.id in self.banned_users:
            embed = discord.Embed(
                title="⚠️ Déjà banni",
                description=f"{user.mention} est déjà banni du bot.",
                color=discord.Color.orange()
            )
            return await ctx.send(embed=embed)

        self.banned_users.add(user.id)
        save_blacklist(self.banned_users)
        embed = discord.Embed(
            title="🚫 Utilisateur banni",
            description=f"{user.mention} a été banni du bot.",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)

    # --- commande pour unban ---
    @commands.command()
    async def botunban(self, ctx, user: discord.User):
        if not self.is_admin_or_owner(ctx):
            embed = discord.Embed(
                title="❌ Permission refusée",
                description="Tu n’as pas la permission d’utiliser cette commande.",
                color=discord.Color.red()
            )
            return await ctx.send(embed=embed)

        if user.id not in self.banned_users:
            embed = discord.Embed(
                title="⚠️ Non banni",
                description=f"{user.mention} n’était pas banni du bot.",
                color=discord.Color.orange()
            )
            return await ctx.send(embed=embed)

        self.banned_users.remove(user.id)
        save_blacklist(self.banned_users)
        embed = discord.Embed(
            title="✅ Utilisateur débanni",
            description=f"{user.mention} a été débanni du bot.",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(BotBlacklist(bot))
