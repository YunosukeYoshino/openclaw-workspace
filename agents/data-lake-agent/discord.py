#!/usr/bin/env python3
"""
Discord bot integration for data-lake-agent
"""

import discord
from discord.ext import commands
from discord import app_commands
import logging
from pathlib import Path
import sys

# Add parent directory to path to import agent
sys.path.insert(0, str(Path(__file__).parent.parent))
from agent import DataLakeAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DiscordBot(commands.Bot):
    """Discord bot for data-lake-agent"""

    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True

        super().__init__(
            command_prefix="!",
            intents=intents,
            activity=discord.Activity(type=discord.ActivityType.watching, name="for commands")
        )

        self.agent = DataLakeAgent()

    async def setup_hook(self):
        """Setup hook for bot"""
        await self.tree.sync()
        logger.info("Commands synced")

            bot.tree.command(name="ingest")(self.ingest)
            bot.tree.command(name="list_datasets")(self.list_datasets)
            bot.tree.command(name="dataset_info")(self.dataset_info)
            bot.tree.command(name="query_lake")(self.query_lake)

    async def ingest(self, interaction):
        """Handle ingest command"""
        await interaction.response.send_message(f"{agent_name}: ingest command received!")

    async def list_datasets(self, interaction):
        """Handle list_datasets command"""
        await interaction.response.send_message(f"{agent_name}: list_datasets command received!")

    async def dataset_info(self, interaction):
        """Handle dataset_info command"""
        await interaction.response.send_message(f"{agent_name}: dataset_info command received!")

    async def query_lake(self, interaction):
        """Handle query_lake command"""
        await interaction.response.send_message(f"{agent_name}: query_lake command received!")

    async def on_ready(self):
        """Called when bot is ready"""
        logger.info(f"{self.user} is ready!")
        logger.info(f"Connected to {len(self.guilds)} guilds")

    async def on_message(self, message: discord.Message):
        """Handle incoming messages"""
        # Ignore messages from the bot itself
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
