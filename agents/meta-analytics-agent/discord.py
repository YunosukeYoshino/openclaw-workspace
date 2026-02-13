#!/usr/bin/env python3
"""Discord Bot module for meta-analytics-agent"""

import discord
from discord.ext import commands
from db import Database

bot = commands.Bot(command_prefix='!', intents=discord.Intents.default())
db = Database("meta-analytics-agent.db")
db.initialize()

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')

@bot.command()
async def hello(ctx):
    """Say hello"""
    await ctx.send(f"Hello! I'm メタアナリティクスエージェント agent!")

@bot.command()
async def stats(ctx, category: str = None):
    """Show statistics"""
    if category:
        stats = db.get_category_stats(category)
        await ctx.send(f"""📊 {category}の分析結果:
{stats}""")
    else:
        stats = db.get_overall_stats()
        await ctx.send(f"""📊 全体分析結果:
{stats}""")

@bot.command()
async def help(ctx):
    """Show help"""
    help_text = """📖 Available Commands:
- !hello: Greeting
- !stats [category]: Show statistics
- !help: Show this help
"""
    await ctx.send(help_text)

def run_bot(token):
    bot.run(token)

if __name__ == "__main__":
    import os
    token = os.getenv("DISCORD_TOKEN")
    if token:
        run_bot(token)
    else:
        print("DISCORD_TOKEN not found")
