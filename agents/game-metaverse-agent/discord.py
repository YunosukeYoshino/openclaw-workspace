#!/usr/bin/env python3
"""
Discord bot integration for game-metaverse-agent
"""

import discord
from discord.ext import commands
from discord import app_commands
import logging
from pathlib import Path
import sys

# Add parent directory to path to import agent
sys.path.insert(0, str(Path(__file__).parent.parent))
from agent import GameMetaverseAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DiscordBot(commands.Bot):
    """Discord bot for game-metaverse-agent"""

    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True

        super().__init__(
            command_prefix="!",
            intents=intents,
            activity=discord.Activity(type=discord.ActivityType.watching, name="for commands")
        )

        self.agent = GameMetaverseAgent()

    async def setup_hook(self):
        """Setup hook for bot"""
        await self.tree.sync()
        logger.info("Commands synced")

            bot.tree.command(name="create_world")(self.create_world)
            bot.tree.command(name="manage_avatar")(self.manage_avatar)
            bot.tree.command(name="world_events")(self.world_events)
            bot.tree.command(name="metaverse_stats")(self.metaverse_stats)

    async def create_world(self, interaction):
        """Handle create_world command"""
        await interaction.response.send_message(f"{agent_name}: create_world command received!")

    async def manage_avatar(self, interaction):
        """Handle manage_avatar command"""
        await interaction.response.send_message(f"{agent_name}: manage_avatar command received!")

    async def world_events(self, interaction):
        """Handle world_events command"""
        await interaction.response.send_message(f"{agent_name}: world_events command received!")

    async def metaverse_stats(self, interaction):
        """Handle metaverse_stats command"""
        await interaction.response.send_message(f"{agent_name}: metaverse_stats command received!")

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
