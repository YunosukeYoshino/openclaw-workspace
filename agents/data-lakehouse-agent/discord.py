#!/usr/bin/env python3
"""
Discord bot integration for data-lakehouse-agent
"""

import discord
from discord.ext import commands
from discord import app_commands
import logging
from pathlib import Path
import sys

# Add parent directory to path to import agent
sys.path.insert(0, str(Path(__file__).parent.parent))
from agent import DataLakehouseAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DiscordBot(commands.Bot):
    """Discord bot for data-lakehouse-agent"""

    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True

        super().__init__(
            command_prefix="!",
            intents=intents,
            activity=discord.Activity(type=discord.ActivityType.watching, name="for commands")
        )

        self.agent = DataLakehouseAgent()

    async def setup_hook(self):
        """Setup hook for bot"""
        await self.tree.sync()
        logger.info("Commands synced")

            bot.tree.command(name="create_table")(self.create_table)
            bot.tree.command(name="zones")(self.zones)
            bot.tree.command(name="table_lineage")(self.table_lineage)
            bot.tree.command(name="query_lakehouse")(self.query_lakehouse)

    async def create_table(self, interaction):
        """Handle create_table command"""
        await interaction.response.send_message(f"{agent_name}: create_table command received!")

    async def zones(self, interaction):
        """Handle zones command"""
        await interaction.response.send_message(f"{agent_name}: zones command received!")

    async def table_lineage(self, interaction):
        """Handle table_lineage command"""
        await interaction.response.send_message(f"{agent_name}: table_lineage command received!")

    async def query_lakehouse(self, interaction):
        """Handle query_lakehouse command"""
        await interaction.response.send_message(f"{agent_name}: query_lakehouse command received!")

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
