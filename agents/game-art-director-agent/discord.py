#!/usr/bin/env python3
"""
Discord bot integration for game-art-director-agent
"""

import discord
from discord.ext import commands
from discord import app_commands
import logging
from pathlib import Path
import sys

# Add parent directory to path to import agent
sys.path.insert(0, str(Path(__file__).parent.parent))
from agent import GameArtDirectorAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DiscordBot(commands.Bot):
    """Discord bot for game-art-director-agent"""

    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True

        super().__init__(
            command_prefix="!",
            intents=intents,
            activity=discord.Activity(type=discord.ActivityType.watching, name="for commands")
        )

        self.agent = GameArtDirectorAgent()

    async def setup_hook(self):
        """Setup hook for bot"""
        await self.tree.sync()
        logger.info("Commands synced")

            bot.tree.command(name="art_style")(self.art_style)
            bot.tree.command(name="add_asset")(self.add_asset)
            bot.tree.command(name="review_art")(self.review_art)
            bot.tree.command(name="visual_guide")(self.visual_guide)

    async def art_style(self, interaction):
        """Handle art_style command"""
        await interaction.response.send_message(f"{agent_name}: art_style command received!")

    async def add_asset(self, interaction):
        """Handle add_asset command"""
        await interaction.response.send_message(f"{agent_name}: add_asset command received!")

    async def review_art(self, interaction):
        """Handle review_art command"""
        await interaction.response.send_message(f"{agent_name}: review_art command received!")

    async def visual_guide(self, interaction):
        """Handle visual_guide command"""
        await interaction.response.send_message(f"{agent_name}: visual_guide command received!")

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
