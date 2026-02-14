#!/usr/bin/env python3
"""
Discord bot integration for ai-feature-store-agent
"""

import discord
from discord.ext import commands
from discord import app_commands
import logging
from pathlib import Path
import sys

# Add parent directory to path to import agent
sys.path.insert(0, str(Path(__file__).parent.parent))
from agent import AiFeatureStoreAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DiscordBot(commands.Bot):
    """Discord bot for ai-feature-store-agent"""

    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True

        super().__init__(
            command_prefix="!",
            intents=intents,
            activity=discord.Activity(type=discord.ActivityType.watching, name="for commands")
        )

        self.agent = AiFeatureStoreAgent()

    async def setup_hook(self):
        """Setup hook for bot"""
        await self.tree.sync()
        logger.info("Commands synced")

            bot.tree.command(name="add_feature")(self.add_feature)
            bot.tree.command(name="create_group")(self.create_group)
            bot.tree.command(name="get_features")(self.get_features)
            bot.tree.command(name="feature_history")(self.feature_history)

    async def add_feature(self, interaction):
        """Handle add_feature command"""
        await interaction.response.send_message(f"{agent_name}: add_feature command received!")

    async def create_group(self, interaction):
        """Handle create_group command"""
        await interaction.response.send_message(f"{agent_name}: create_group command received!")

    async def get_features(self, interaction):
        """Handle get_features command"""
        await interaction.response.send_message(f"{agent_name}: get_features command received!")

    async def feature_history(self, interaction):
        """Handle feature_history command"""
        await interaction.response.send_message(f"{agent_name}: feature_history command received!")

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
