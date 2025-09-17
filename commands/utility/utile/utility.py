import discord
from discord.ext import commands
def safe_text(text):
    
    # Empêche @everyone et @here
    return text.replace("@everyone", "@\u200beveryone").replace("@here", "@\u200bhere")

class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # 1️⃣ Poll
    @commands.command()
    async def poll(self, ctx, *, question):
        """Crée un sondage rapide avec réactions 👍👎"""
        msg = await ctx.send(f"📊 Sondage : {question}")
        await msg.add_reaction("👍")
        await msg.add_reaction("👎")

    @commands.command()
    async def serverroles(self, ctx):
     roles = [r.name for r in ctx.guild.roles[::-1] if r.name != "@everyone"]
     safe_roles = [safe_text(r) for r in roles]  # filtre
     await ctx.send(
        "🎭 Rôles du serveur : " + ", ".join(safe_roles),
        allowed_mentions=discord.AllowedMentions.none()
    )
#c cette commande qui ta ping
    # 3️⃣ Server Info
    @commands.command()
    async def serverinfo(self, ctx):
        """Affiche les informations du serveur"""
        guild = ctx.guild
        embed = discord.Embed(title=f"Infos sur {guild.name}", color=discord.Color.purple())
        embed.add_field(name="ID", value=guild.id)
        embed.add_field(name="Propriétaire", value=guild.owner)
        embed.add_field(name="Membres", value=guild.member_count)
        embed.add_field(name="Création", value=guild.created_at.strftime("%d/%m/%Y"))
        await ctx.send(embed=embed)

    # 4️⃣ User Info
    @commands.command()
    async def userinfo(self, ctx, member: discord.Member = None):
        """Affiche les informations d'un membre"""
        member = member or ctx.author
        embed = discord.Embed(title=f"Infos sur {member}", color=discord.Color.green())
        embed.add_field(name="ID", value=member.id)
        embed.add_field(name="Nom", value=str(member))
        embed.add_field(name="Rôles", value=", ".join([r.name for r in member.roles[1:]]))
        embed.add_field(name="Date d'arrivée", value=member.joined_at.strftime("%d/%m/%Y"))
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Utility(bot))
