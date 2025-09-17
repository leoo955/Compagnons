import discord
from discord.ext import commands

OWNER_ID = 1074814902683844810  # Ton ID Discord
CO_OWNERS = [463453035327389696, 987654321098765432]  # Mets les ID des co-owners ici

class VoiceMove(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="move")
    async def move(self, ctx, member: discord.Member, channel: discord.VoiceChannel):
        """
        Déplace un membre dans un autre salon vocal.
        Seulement l'owner et les co-owners peuvent utiliser cette commande.
        Usage : !move @membre salon
        """
        embed = discord.Embed(color=discord.Color.blurple())

        # Vérifie si l'utilisateur est owner ou co-owner
        if ctx.author.id != OWNER_ID and ctx.author.id not in CO_OWNERS:
            embed.title = "❌ Permission refusée"
            embed.description = "Tu n'as pas la permission d'utiliser cette commande."
            embed.color = discord.Color.red()
            return await ctx.send(embed=embed)

        # Vérifie si la cible est en vocal
        if not member.voice:
            embed.title = "❌ Membre non connecté"
            embed.description = f"{member.display_name} n'est pas connecté en vocal."
            embed.color = discord.Color.orange()
            return await ctx.send(embed=embed)

        # Déplace le membre
        await member.move_to(channel)
        embed.title = "✅ Membre déplacé"
        embed.description = f"{member.mention} a été déplacé dans **{channel.name}**."
        embed.color = discord.Color.green()
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(VoiceMove(bot))
