from discord.ext import commands
import discord
import random

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ------------------ Avatar ------------------
    @commands.command()
    async def avatar(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        embed = discord.Embed(
            title=f"Avatar de {member}",
            color=discord.Color.blue()
        )
        embed.set_image(url=member.avatar.url)
        await ctx.send(embed=embed)

    # ------------------ Dice ------------------
    @commands.command()
    async def roll(self, ctx, dice: str = "1d6"):
        """Lance un dé. Exemple : !roll 2d20"""
        try:
            rolls, limit = map(int, dice.lower().split("d"))
        except:
            embed = discord.Embed(
                title="❌ Format invalide",
                description="Exemple correct : `2d6`",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        results = [random.randint(1, limit) for _ in range(rolls)]
        embed = discord.Embed(
            title="🎲 Résultat du dé",
            description=f"{', '.join(map(str, results))}\n**Total : {sum(results)}**",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)

    # ------------------ Random choice ------------------
    @commands.command()
    async def choose(self, ctx, *choices):
        """Choisit aléatoirement parmi les options"""
        if not choices:
            embed = discord.Embed(
                title="❌ Aucune option fournie",
                description="Donne-moi au moins une option !",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        selection = random.choice(choices)
        embed = discord.Embed(
            title="🎯 Choix aléatoire",
            description=f"Je choisis : **{selection}**",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Fun(bot))
