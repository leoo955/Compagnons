import discord
from discord.ext import commands
import json
import os
from datetime import datetime, timedelta

COUNTER_FILE = "nekid_counter.json"
WARN_FILE = "commands/utility/moderation/warnings.json"
USAGE_FILE = "nekid_usage.json"
NEKID_ID = 940657982893604944  # Remplace par l'ID de nekid
COOLDOWN_HOURS = 1
ALLOWED_GUILD_ID = 1284912352885739581, 1360703845680021664  # Remplace par l'ID du serveur autorisé

class Nekid(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Création fichiers s'ils n'existent pas
        for f in [COUNTER_FILE, WARN_FILE, USAGE_FILE]:
            if not os.path.exists(f):
                with open(f, "w") as file:
                    json.dump({}, file)

    # --- Utils ---
    def load_json(self, file):
        try:
            with open(file, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}

    def save_json(self, file, data):
        with open(file, "w") as f:
            json.dump(data, f, indent=4)

    # --- Command !nekid ---
    @commands.command(
        name="nekid",
        help="Incrémente le compteur Nekid (1h de cooldown). Atteindre 100 avertit l'utilisateur 'nekid'."
    )
    async def nekid(self, ctx):
        # Vérification serveur autorisé
        if ctx.guild.id != ALLOWED_GUILD_ID:
            await ctx.send("❌ Cette commande n'est disponible que sur le serveur autorisé.")
            return

        now = datetime.utcnow()
        user_id = str(ctx.author.id)
        guild_id = str(ctx.guild.id)

        # ----- COOLDOWN -----
        usage = self.load_json(USAGE_FILE)
        user_cd = usage.get(user_id, {}).get("last_used")
        if user_cd:
            last = datetime.fromisoformat(user_cd)
            if now - last < timedelta(hours=COOLDOWN_HOURS):
                remaining = timedelta(hours=COOLDOWN_HOURS) - (now - last)
                await ctx.send(
                    f"❌ Tu dois attendre encore `{str(remaining).split('.')[0]}` avant de réutiliser cette commande."
                )
                return

        # ----- INCREMENT COUNTER -----
        counter = self.load_json(COUNTER_FILE)
        counter[guild_id] = counter.get(guild_id, 0) + 1
        self.save_json(COUNTER_FILE, counter)
        count = counter[guild_id]

        embed = discord.Embed(
            title="📊 Compteur Nekid",
            description=f"Le compteur est maintenant à **{count}/100**",
            color=discord.Color.purple(),
        )
        await ctx.send(embed=embed)

        # ----- WARN NEKID -----
        if count >= 100:
            warnings = self.load_json(WARN_FILE)
            warnings.setdefault(str(NEKID_ID), []).append("A atteint 100 Nekid !")
            self.save_json(WARN_FILE, warnings)

            member = ctx.guild.get_member(NEKID_ID)
            if member:
                await ctx.send(f"⚠️ {member.mention} reçoit un avertissement !")
            else:
                await ctx.send("⚠️ L’utilisateur `nekid` a reçu un avertissement (non trouvé sur ce serveur).")

            counter[guild_id] = 0
            self.save_json(COUNTER_FILE, counter)

        # ----- UPDATE USAGE -----
        usage.setdefault(user_id, {"count": 0, "last_used": now.isoformat()})
        usage[user_id]["count"] += 1
        usage[user_id]["last_used"] = now.isoformat()
        self.save_json(USAGE_FILE, usage)

    # --- Leaderboard ---
    @commands.command(
        name="nekidLead",
        help="Affiche le classement des 10 utilisateurs ayant le plus utilisé !nekid."
    )
    async def nekid_leaderboard(self, ctx):
        usage = self.load_json(USAGE_FILE)
        if not usage:
            await ctx.send("Aucun utilisateur n’a encore utilisé `!nekid`.")
            return

        leaderboard = sorted(usage.items(), key=lambda x: x[1]["count"], reverse=True)
        embed = discord.Embed(
            title="🏆 Classement Nekid",
            description="Top 10 des plus gros spammeurs de `!nekid`",
            color=discord.Color.gold(),
        )

        for i, (user_id, data) in enumerate(leaderboard[:10], start=1):
            member = ctx.guild.get_member(int(user_id))
            name = member.display_name if member else f"Utilisateur supprimé ({user_id})"
            embed.add_field(
                name=f"{i}. {name}",
                value=f"Utilisations : **{data['count']}**",
                inline=False,
            )

        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Nekid(bot))
