import discord
from discord.ext import commands
import re

# Liste des domaines bloqués
BLOCKED_DOMAINS = [
    "discord.com",
    "discord.gg",
    "t.me"
]

# Regex pour détecter les liens HTTPS
HTTPS_LINK_REGEX = r"https://[^\s]+"

class AntiLink(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        # Ignore les messages avec des fichiers attachés (GIF, PNG, JPG)
        if message.attachments:
            return

        # Cherche tous les liens HTTPS dans le message
        links = re.findall(HTTPS_LINK_REGEX, message.content)
        for link in links:
            if any(blocked in link for blocked in BLOCKED_DOMAINS):
                try:
                    await message.delete()
                    embed = discord.Embed(
                        description=f"🚫 {message.author.mention}, les liens vers Discord ou Telegram ne sont pas autorisés !",
                        color=discord.Color.red()
                    )
                    await message.channel.send(embed=embed, delete_after=5)
                    return  # stop après le premier lien bloqué
                except:
                    pass

async def setup(bot):
    await bot.add_cog(AntiLink(bot))
