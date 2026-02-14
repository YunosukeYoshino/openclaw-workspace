#!/usr/bin/env python3
"""
Discord bot integration for erotic-recommendation-v3-agent
"""

import discord
from discord.ext import commands
from discord import app_commands
import logging
from pathlib import Path
import sys

# Add parent directory to path to import agent
sys.path.insert(0, str(Path(__file__).parent.parent))
from agent import EroticRecommendationV3Agent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DiscordBot(commands.Bot):
    """Discord bot for erotic-recommendation-v3-agent"""

    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True

        super().__init__(
            command_prefix="!",
            intents=intents,
            activity=discord.Activity(type=discord.ActivityType.watching, name="for commands")
        )

        self.agent = EroticRecommendationV3Agent()

    async def setup_hook(self):
        """Setup hook for bot"""
        await self.tree.sync()
        logger.info("Commands synced")

            bot.tree.command(name="recommend")(self.recommend)
            bot.tree.command(name="train_model")(self.train_model)
            bot.tree.command(name="model_performance")(self.model_performance)
            bot.tree.command(name="recommendation_history")(self.recommendation_history)

    async def recommend(self, interaction):
        """Handle recommend command"""
        await interaction.response.send_message(f"{agent_name}: recommend command received!")

    async def train_model(self, interaction):
        """Handle train_model command"""
        await interaction.response.send_message(f"{agent_name}: train_model command received!")

    async def model_performance(self, interaction):
        """Handle model_performance command"""
        await interaction.response.send_message(f"{agent_name}: model_performance command received!")

    async def recommendation_history(self, interaction):
        """Handle recommendation_history command"""
        await interaction.response.send_message(f"{agent_name}: recommendation_history command received!")

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
