import discord
import asyncio
from discord.ext import commands
from flask import Flask, request, jsonify, render_template_string
import os
import threading
import time

# Get the token from the environment variable
TOKEN = os.getenv("DISCORD_TOKEN")

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

app = Flask(__name__)

servers = {}

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    global servers
    servers = {guild.id: guild.name for guild in bot.guilds}

# Define the HTML content as a string
html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Discord Bot Messenger</title>
    <style>
        body {
            font-family: 'Arial', sans-serif;
            margin: 0;
            padding: 0;
            background-color: #121212;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            color: #fff;
        }

        .container {
            background-color: #2c2f33;
            padding: 40px 60px;
            border-radius: 25px;
            box-shadow: 0 10px 20px rgba(0, 0, 0, 0.5);
            text-align: center;
        }

        .icon {
            display: inline-block;
            vertical-align: middle;
            margin-bottom: 10px;
        }

        .icon img {
            width: 40px;
            height: 40px;
        }

        h2 {
            font-size: 28px;
            margin-bottom: 10px;
        }

        p.subtitle {
            font-size: 16px;
            margin-bottom: 20px;
            color: #ccc;
        }

        input, select, button {
            padding: 12px;
            margin: 10px 0;
            width: 100%;
            max-width: 400px;
            font-size: 16px;
            border: none;
            border-radius: 20px;
        }

        select, input {
            background-color: #fff;
            color: #333;
        }

        button {
            background-color: #007bff;
            color: white;
            cursor: pointer;
            transition: background-color 0.3s;
        }

        button:hover {
            background-color: #0056b3;
        }

        #statusMessage {
            margin-top: 20px;
            font-size: 18px;
        }

        form {
            display: flex;
            flex-direction: column;
            align-items: center;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="icon">
            <img src="https://img.icons8.com/ios-filled/50/ffffff/globe.png" alt="Globe Icon">
        </div>
        <h2>Discord Bot Messenger</h2>
        <p class="subtitle">Select a server and enter your message below!</p>
        <form id="messageForm">
            <select id="serverSelect" required>
                <option value="" disabled selected>Select Server</option>
                {% for server_id, server_name in servers.items() %}
                    <option value="{{ server_id }}">{{ server_name }}</option>
                {% endfor %}
            </select>
            <input type="text" id="messageInput" placeholder="Enter message" required>
            <button type="submit">Send Message</button>
        </form>
        <p id="statusMessage"></p>
    </div>
    <script>
        document.getElementById("messageForm").addEventListener("submit", function(event) {
            event.preventDefault();

            const serverId = document.getElementById("serverSelect").value;
            const message = document.getElementById("messageInput").value;

            if (!serverId || !message) {
                document.getElementById("statusMessage").textContent = "Please select a server and enter a message!";
                return;
            }

            const requestData = {
                server_id: serverId,
                message: message
            };

            fetch("/send_message", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(requestData)
            })
            .then(response => response.json())
            .then(data => {
                document.getElementById("statusMessage").textContent = data.message;
            })
            .catch(error => {
                console.error("Error:", error);
                document.getElementById("statusMessage").textContent = "An error occurred. Please try again.";
            });
        });
    </script>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(html_content, servers=servers)

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
    # Wait for the bot to be ready before starting the Flask server
    while not servers:
        time.sleep(1)
    app.run(host="0.0.0.0", port=5000)

threading.Thread(target=run_flask).start()

bot.run(TOKEN)
