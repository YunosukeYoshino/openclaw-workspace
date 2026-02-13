#!/usr/bin/env python3
"""
Discord Bot for erotic-commission-tracker-agent
えっちコミッショントラッカーエージェント / Erotic Commission Tracker Agent
"""

import discord
from discord.ext import commands
from agent import EroticCommissionTrackerAgent
import logging
from pathlib import Path
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("erotic-commission-tracker-agent")

TOKEN = os.getenv("DISCORD_TOKEN", "YOUR_DISCORD_BOT_TOKEN")
INTENTS = discord.Intents.default()
INTENTS.message_content = True

bot = commands.Bot(command_prefix="!", intents=INTENTS, help_command=commands.DefaultHelpCommand())

@bot.event
async def on_ready():
    logger.info(str(bot.user.name) + " is ready!")
    logger.info("Bot ID: " + str(bot.user.id))
    logger.info("Connected to " + str(len(bot.guilds)) + " guilds")

@bot.event
async def on_command_error(ctx: commands.Context, error):
    if isinstance(error, commands.CommandNotFound):
        return
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Missing required argument: " + str(error.param.name))
    else:
        logger.error("Command error: " + str(error))
        await ctx.send("An error occurred: " + str(error))

async def main():
    Path("data").mkdir(exist_ok=True)
    await bot.add_cog(EroticCommissionTrackerAgent(bot))
    logger.info("Starting bot...")
    await bot.start(TOKEN)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
