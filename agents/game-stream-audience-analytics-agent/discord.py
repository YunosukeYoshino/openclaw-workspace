"""Discord bot for game-stream-audience-analytics-agent"""

import os
import discord
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
intents.messages = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"{client.user} is ready!")

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith("!"):
        await handle_command(message)

async def handle_command(message):
    command = message.content[1:].split()[0]

    if command == "help":
        await show_help(message)
    elif command == "status":
        await show_status(message)
    else:
        await message.channel.send(f"Unknown command: {command}")

async def show_help(message):
    help_text = f"""
    game-stream-audience-analytics-agent - ゲーム配信視聴者分析エージェント。視聴者の分析・管理

    Commands:
    !help - Show this help
    !status - Show status
    """
    await message.channel.send(help_text)

async def show_status(message):
    await message.channel.send("Bot is running normally!")

if __name__ == "__main__":
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        print("DISCORD_TOKEN not found!")
        exit(1)

    client.run(token)
