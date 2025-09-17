import discord
from discord.ext import commands
import json
import os

OWNERS_FILE = "owners.json"
OWNER_ID = 1074814902683844810  # <-- Ton ID Discord

def load_owners():
    if os.path.exists(OWNERS_FILE):
        with open(OWNERS_FILE, "r") as f:
            return set(json.load(f))
    return {OWNER_ID}  # par défaut, toi seulement

def save_owners(owners):
    with open(OWNERS_FILE, "w") as f:
        json.dump(list(owners), f, indent=4)

class Ownership(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.owners = load_owners()

    def is_owner(self, user_id: int):
        return user_id in self.owners

    @commands.command()
    async def addowner(self, ctx, user: discord.User):
        """Ajoute un co-owner du bot"""
        if ctx.author.id != OWNER_ID:
            embed = discord.Embed(
                description="❌ Seul le propriétaire principal peut ajouter des co-owners.",
                color=discord.Color.red()
            )
            return await ctx.send(embed=embed)

        if user.id in self.owners:
            embed = discord.Embed(
                description=f"⚠️ {user.name}#{user.discriminator} est déjà co-owner.",
                color=discord.Color.orange()
            )
            return await ctx.send(embed=embed)
        
        self.owners.add(user.id)
        save_owners(self.owners)
        embed = discord.Embed(
            description=f"✅ {user.name}#{user.discriminator} est maintenant co-owner du bot.",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)

    @commands.command()
    async def removeowner(self, ctx, user: discord.User):
        """Retire un co-owner du bot"""
        if ctx.author.id != OWNER_ID:
            embed = discord.Embed(
                description="❌ Seul le propriétaire principal peut retirer des co-owners.",
                color=discord.Color.red()
            )
            return await ctx.send(embed=embed)

        if user.id == OWNER_ID:
            embed = discord.Embed(
                description="❌ Tu ne peux pas te retirer toi-même en tant que propriétaire principal.",
                color=discord.Color.red()
            )
            return await ctx.send(embed=embed)
        
        if user.id not in self.owners:
            embed = discord.Embed(
                description=f"⚠️ {user.name}#{user.discriminator} n’est pas co-owner.",
                color=discord.Color.orange()
            )
            return await ctx.send(embed=embed)
        
        self.owners.remove(user.id)
        save_owners(self.owners)
        embed = discord.Embed(
            description=f"✅ {user.name}#{user.discriminator} n’est plus co-owner du bot.",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)

    @commands.command()
    async def owners(self, ctx):
        """Liste les co-owners actuels sans ping"""
        members = []
        for uid in self.owners:
            member = ctx.guild.get_member(uid)
            if member:
                members.append(f"{member.name}#{member.discriminator}")
            else:
                members.append(f"ID:{uid}")

        embed = discord.Embed(
            title="👑 Co-owners actuels",
            description="\n".join(members) if members else "Aucun co-owner",
            color=discord.Color.gold()
        )
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Ownership(bot))
