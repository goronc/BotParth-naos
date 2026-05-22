import discord
from discord.ext import commands, tasks
from mcstatus import JavaServer
import asyncio
from datetime import datetime
from aiohttp import web

# ═══════════════════════════════════════════════════════
# CONFIGURATION — Remplace les valeurs ici
# ═══════════════════════════════════════════════════════
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = 1507177617277849620
SERVER_IP = "23.109.46.233"
SERVER_PORT = 25579

# ═══════════════════════════════════════════════════════
# BOT SETUP
# ═══════════════════════════════════════════════════════
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

status_message = None  # Message de statut en temps réel

# ═══════════════════════════════════════════════════════
# FONCTION : Récupérer le statut du serveur
# ═══════════════════════════════════════════════════════
def get_server_status():
    try:
        server = JavaServer(SERVER_IP, SERVER_PORT, timeout=5)
        status = server.status()
        players = status.players.online
        max_players = status.players.max
        player_list = []
        if status.players.sample:
            player_list = [p.name for p in status.players.sample]
        return {
            "online": True,
            "players": players,
            "max": max_players,
            "player_list": player_list,
            "ping": round(status.latency)
        }
    except Exception:
        return {"online": False}

# ═══════════════════════════════════════════════════════
# FONCTION : Créer l'embed de statut
# ═══════════════════════════════════════════════════════
def create_status_embed(status):
    if status["online"]:
        embed = discord.Embed(
            title="Parthénaos",
            color=0x2ECC71  # Vert
        )
        embed.add_field(
            name="🟢 Statut",
            value="En ligne",
            inline=True
        )
        embed.add_field(
            name="👥 Joueurs",
            value=f"{status['players']}/{status['max']}",
            inline=True
        )
        embed.add_field(
            name="📡 Ping",
            value=f"{status['ping']}ms",
            inline=True
        )
        embed.add_field(
            name="IP de connexion",
            value=f"strapontia.game-server.host",
            inline=False
        )
        if status["player_list"]:
            embed.add_field(
                name="🧑‍🤝‍🧑 Joueurs connectés",
                value="\n".join([f"• {p}" for p in status["player_list"]]),
                inline=False
            )
        else:
            embed.add_field(
                name="🧑‍🤝‍🧑 Joueurs connectés",
                value="Aucun joueur en ligne",
                inline=False
            )
    else:
        embed = discord.Embed(
            title="Parthénaos",
            color=0xE74C3C  # Rouge
        )
        embed.add_field(
            name="🔴 Statut",
            value="Hors ligne",
            inline=True
        )
        embed.add_field(
            name="IP de connexion",
            value="strapontia.game-server.host",
            inline=False
        )

    embed.set_footer(text=f"Dernière mise à jour : {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}      Dev By Goro")
    return embed

# ═══════════════════════════════════════════════════════
# TÂCHE : Mise à jour automatique toutes les 60 secondes
# ═══════════════════════════════════════════════════════
@tasks.loop(seconds=60)
async def update_status():
    global status_message
    channel = bot.get_channel(CHANNEL_ID)
    if channel is None:
        return

    status = await asyncio.to_thread(get_server_status)
    embed = create_status_embed(status)

    # Mettre à jour le message de statut existant
    if status_message:
        try:
            await status_message.edit(embed=embed)
        except discord.NotFound:
            status_message = await channel.send(embed=embed)
    else:
        # Chercher un message existant du bot dans le channel
        async for message in channel.history(limit=10):
            if message.author == bot.user:
                status_message = message
                await status_message.edit(embed=embed)
                return
        # Sinon envoyer un nouveau message
        status_message = await channel.send(embed=embed)

    # Mettre à jour le statut du bot
    if status["online"]:
        await bot.change_presence(
            activity=discord.Game(f"🟢 {status['players']}/{status['max']} joueurs en ligne")
        )
    else:
        await bot.change_presence(
            activity=discord.Game("🔴 Serveur hors ligne")
        )

# ═══════════════════════════════════════════════════════
# COMMANDE : !status
# ═══════════════════════════════════════════════════════
@bot.command(name="status")
async def status_command(ctx):
    status = await asyncio.to_thread(get_server_status)
    embed = create_status_embed(status)
    await ctx.send(embed=embed)

# ═══════════════════════════════════════════════════════
# COMMANDE : !joueurs
# ═══════════════════════════════════════════════════════
@bot.command(name="joueurs")
async def joueurs_command(ctx):
    status = await asyncio.to_thread(get_server_status)
    if status["online"]:
        if status["player_list"]:
            joueurs = "\n".join([f"• {p}" for p in status["player_list"]])
            await ctx.send(f"**👥 Joueurs connectés ({status['players']}/{status['max']}) :**\n{joueurs}")
        else:
            await ctx.send(f"**👥 Aucun joueur connecté** (0/{status['max']})")
    else:
        await ctx.send("**🔴 Le serveur est hors ligne.**")

# ═══════════════════════════════════════════════════════
# ÉVÉNEMENT : Bot prêt
# ═══════════════════════════════════════════════════════
@bot.event
async def on_ready():
    print(f"✅ Bot connecté : {bot.user}")
    print(f"📡 Surveillance de {SERVER_IP}:{SERVER_PORT}")
    update_status.start()

# ═══════════════════════════════════════════════════════
# SERVEUR WEB (requis pour Render free tier)
# ═══════════════════════════════════════════════════════
async def health_check(_request):
    return web.Response(text="OK")

async def start_web_server():
    app = web.Application()
    app.router.add_get("/", health_check)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

# ═══════════════════════════════════════════════════════
# LANCEMENT
# ═══════════════════════════════════════════════════════
async def main():
    await start_web_server()
    await bot.start(TOKEN)

asyncio.run(main())
