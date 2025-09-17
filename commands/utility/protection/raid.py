import discord
from discord.ext import commands, tasks
import asyncio

class RaidSimulator(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="simuleraid")
    @commands.is_owner()  # seul le propriétaire du bot peut lancer
    async def simulate_raid(self, ctx):
        """Simule un raid massif sur le serveur de test."""
        embed_start = discord.Embed(
            title="⚠️ Simulation de raid MASSIVE",
            description="Des messages rapides et mentions vont être envoyés pour tester les protections.",
            color=discord.Color.orange()
        )
        await ctx.send(embed=embed_start)

        for i in range(30):  # nombre de messages simulés
            # Simule un message avec mention fictive
            await ctx.send(f"@everyone Message de test {i+1}")
            
            # Simule un lien
            await ctx.send(f"Test de lien: https://example.com/{i+1}")
            
            # Simule un embed
            embed = discord.Embed(
                title=f"Embed raid {i+1}",
                description="Ceci est un message de test pour simuler un raid",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)

            await asyncio.sleep(0.3)  # intervalle rapide pour simuler un flood massif

        embed_end = discord.Embed(
            title="✅ Simulation terminée",
            description="La simulation de raid MASSIVE est terminée.",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed_end)

async def setup(bot):
    await bot.add_cog(RaidSimulator(bot))
