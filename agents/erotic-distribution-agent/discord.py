#!/usr/bin/env python3
"""
Discord bot integration for erotic-distribution-agent
"""

import discord
from discord.ext import commands
from discord import app_commands
import logging
from pathlib import Path
import sys

# Add parent directory to path to import agent
sys.path.insert(0, str(Path(__file__).parent.parent))
from agent import EroticDistributionAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DiscordBot(commands.Bot):
    """Discord bot for erotic-distribution-agent"""

    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True

        super().__init__(
            command_prefix="!",
            intents=intents,
            activity=discord.Activity(type=discord.ActivityType.watching, name="for commands")
        )

        self.agent = EroticDistributionAgent()

    async def setup_hook(self):
        """Setup hook for bot"""
        await self.tree.sync()
        logger.info("Commands synced")

            bot.tree.command(name="add_channel")(self.add_channel)
            bot.tree.command(name="distribute")(self.distribute)
            bot.tree.command(name="schedule_publish")(self.schedule_publish)
            bot.tree.command(name="distribution_status")(self.distribution_status)

    async def add_channel(self, interaction):
        """Handle add_channel command"""
        await interaction.response.send_message(f"{agent_name}: add_channel command received!")

    async def distribute(self, interaction):
        """Handle distribute command"""
        await interaction.response.send_message(f"{agent_name}: distribute command received!")

    async def schedule_publish(self, interaction):
        """Handle schedule_publish command"""
        await interaction.response.send_message(f"{agent_name}: schedule_publish command received!")

    async def distribution_status(self, interaction):
        """Handle distribution_status command"""
        await interaction.response.send_message(f"{agent_name}: distribution_status command received!")

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
