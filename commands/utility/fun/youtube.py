import discord
from discord.ext import commands
import aiohttp
import yt_dlp

YT_ACTIVITY_ID = "880218394199220334"

class YouTubeTogether(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Fonction pour récupérer le titre de la vidéo
    def get_video_title(self, url):
        ydl_opts = {"quiet": True, "skip_download": True}
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                return info.get("title", "Unknown")
        except:
            return "Titre introuvable"

    @commands.command(name="yt", help="Lance YouTube Together dans ton canal vocal avec le titre de la vidéo")
    async def yt(self, ctx, *, link: str):
        # Vérifie que l'auteur est dans un canal vocal
        if not ctx.author.voice or not ctx.author.voice.channel:
            return await ctx.send("❌ Tu dois être dans un canal vocal pour lancer YouTube Together.")

        channel = ctx.author.voice.channel
        title = self.get_video_title(link)

        invite_payload = {
            "max_age": 3600,
            "max_uses": 0,
            "target_application_id": YT_ACTIVITY_ID,
            "target_type": 2,
            "temporary": False,
            "validate": None
        }

        headers = {
            "Authorization": f"Bot {self.bot.http.token}",
            "Content-Type": "application/json"
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"https://discord.com/api/v10/channels/{channel.id}/invites",
                    json=invite_payload,
                    headers=headers
                ) as resp:
                    if resp.status not in [200, 201]:
                        error_text = await resp.text()
                        return await ctx.send(f"❌ Échec du lancement de YouTube Together.\nCode : {resp.status}\n{error_text}")

                    data = await resp.json()
                    invite_url = f"https://discord.gg/{data['code']}"

            embed = discord.Embed(
                title="📺 YouTube Together",
                description=f"[Clique ici pour rejoindre l'activité]({invite_url})\n\n**Titre vidéo choisi :** {title}",
                color=discord.Color.red()
            )
            embed.set_footer(
                text=f"Demandé par {ctx.author.display_name}",
                icon_url=getattr(ctx.author.avatar, 'url', None)
            )
            await ctx.send(embed=embed)

        except Exception as e:
            await ctx.send(f"❌ Une erreur est survenue lors de la création de l'invite : {e}")


async def setup(bot):
    await bot.add_cog(YouTubeTogether(bot))
