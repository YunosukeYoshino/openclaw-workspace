#!/usr/bin/env python3
"""
Discord bot integration for baseball-bigdata-agent
"""

import discord
from discord.ext import commands
from discord import app_commands
import logging
from pathlib import Path
import sys

# Add parent directory to path to import agent
sys.path.insert(0, str(Path(__file__).parent.parent))
from agent import BaseballBigdataAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DiscordBot(commands.Bot):
    """Discord bot for baseball-bigdata-agent"""

    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True

        super().__init__(
            command_prefix="!",
            intents=intents,
            activity=discord.Activity(type=discord.ActivityType.watching, name="for commands")
        )

        self.agent = BaseballBigdataAgent()

    async def setup_hook(self):
        """Setup hook for bot"""
        await self.tree.sync()
        logger.info("Commands synced")

            bot.tree.command(name="ingest_data")(self.ingest_data)
            bot.tree.command(name="query_data")(self.query_data)
            bot.tree.command(name="data_jobs")(self.data_jobs)
            bot.tree.command(name="data_info")(self.data_info)

    async def ingest_data(self, interaction):
        """Handle ingest_data command"""
        await interaction.response.send_message(f"{agent_name}: ingest_data command received!")

    async def query_data(self, interaction):
        """Handle query_data command"""
        await interaction.response.send_message(f"{agent_name}: query_data command received!")

    async def data_jobs(self, interaction):
        """Handle data_jobs command"""
        await interaction.response.send_message(f"{agent_name}: data_jobs command received!")

    async def data_info(self, interaction):
        """Handle data_info command"""
        await interaction.response.send_message(f"{agent_name}: data_info command received!")

    async def on_ready(self):
        """Called when bot is ready"""
        logger.info(f"{self.user} is ready!")
        logger.info(f"Connected to {len(self.guilds)} guilds")

    async def on_message(self, message: discord.Message):
        """Handle incoming messages"""
        # Ignore messages from bot itself
        if message.author == self.user:
            return

        # Process message through agent
        response = await self.agent.process_message(message.content, str(message.author.id))

        # Send response if not empty
        if response and "error" not in response:
            await message.channel.send(f"Processed: {response.get('status', 'done')}")


async def main():
    """Main entry point"""
    # Get Discord token from environment or config
    import os
    token = os.getenv("DISCORD_TOKEN")

    if not token:
        logger.error("DISCORD_TOKEN environment variable not set")
        return

    bot = DiscordBot()
    await bot.start(token)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
