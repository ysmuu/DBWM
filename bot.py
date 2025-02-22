import discord
import asyncio
import requests
from discord.ext import commands
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Get the token from the environment variable
TOKEN = os.getenv("token")

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

app = Flask(__name__)

servers = {}

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    global servers
    servers = {guild.id: guild.name for guild in bot.guilds}

@app.route("/")
def home():
    return render_template("index.html", servers=servers)

@app.route("/send_message", methods=["POST"])
def send_message():
    try:
        data = request.json
        server_id = int(data["server_id"])
        message = data["message"]

        guild = discord.utils.get(bot.guilds, id=server_id)
        if guild:
            for channel in guild.text_channels:
                if channel.permissions_for(guild.me).send_messages:
                    asyncio.run_coroutine_threadsafe(channel.send(message), bot.loop)
                    return jsonify({"status": "success", "message": "Message sent!"})

        return jsonify({"status": "error", "message": "Failed to send message"}), 400

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


def run_flask():
    app.run(host="0.0.0.0", port=5000)


import threading
threading.Thread(target=run_flask).start()


bot.run(TOKEN)
