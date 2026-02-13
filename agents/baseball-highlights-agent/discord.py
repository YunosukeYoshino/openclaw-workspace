#!/usr/bin/env python3
"""
Discord Bot module for baseball-highlights-agent
"""

import discord
from discord.ext import commands
import os

class BaseballHighlightsAgentBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(*args, intents=intents, **kwargs)

    async def setup_hook(self):
        """Load cogs."""
        # Load cogs here
        pass

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')

@bot.command(name='info')
async def info(ctx):
    """Show bot information."""
    await ctx.send(f"野球ハイライト映像管理エージェント - Baseball Highlights Video Agent")

if __name__ == "__main__":
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        print("DISCORD_TOKEN environment variable not set")
        exit(1)
    bot.run(token)
