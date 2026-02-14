#!/usr/bin/env python3
"""
Discord bot integration for erotic-content-embedding-agent
"""

import discord
from discord.ext import commands
from discord import app_commands
import logging
from pathlib import Path
import sys

# Add parent directory to path to import agent
sys.path.insert(0, str(Path(__file__).parent.parent))
from agent import EroticContentEmbeddingAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DiscordBot(commands.Bot):
    """Discord bot for erotic-content-embedding-agent"""

    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True

        super().__init__(
            command_prefix="!",
            intents=intents,
            activity=discord.Activity(type=discord.ActivityType.watching, name="for commands")
        )

        self.agent = EroticContentEmbeddingAgent()

    async def setup_hook(self):
        """Setup hook for bot"""
        await self.tree.sync()
        logger.info("Commands synced")

            bot.tree.command(name="generate_embedding")(self.generate_embedding)
            bot.tree.command(name="similarity_search")(self.similarity_search)
            bot.tree.command(name="batch_embed")(self.batch_embed)
            bot.tree.command(name="model_info")(self.model_info)

    async def generate_embedding(self, interaction):
        """Handle generate_embedding command"""
        await interaction.response.send_message(f"{agent_name}: generate_embedding command received!")

    async def similarity_search(self, interaction):
        """Handle similarity_search command"""
        await interaction.response.send_message(f"{agent_name}: similarity_search command received!")

    async def batch_embed(self, interaction):
        """Handle batch_embed command"""
        await interaction.response.send_message(f"{agent_name}: batch_embed command received!")

    async def model_info(self, interaction):
        """Handle model_info command"""
        await interaction.response.send_message(f"{agent_name}: model_info command received!")

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
