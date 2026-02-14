#!/usr/bin/env python3
"""
Discord bot integration for erotic-collaborative-filtering-agent
"""

import discord
from discord.ext import commands
from discord import app_commands
import logging
from pathlib import Path
import sys

# Add parent directory to path to import agent
sys.path.insert(0, str(Path(__file__).parent.parent))
from agent import EroticCollaborativeFilteringAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DiscordBot(commands.Bot):
    """Discord bot for erotic-collaborative-filtering-agent"""

    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True

        super().__init__(
            command_prefix="!",
            intents=intents,
            activity=discord.Activity(type=discord.ActivityType.watching, name="for commands")
        )

        self.agent = EroticCollaborativeFilteringAgent()

    async def setup_hook(self):
        """Setup hook for bot"""
        await self.tree.sync()
        logger.info("Commands synced")

            bot.tree.command(name="find_similar_users")(self.find_similar_users)
            bot.tree.command(name="find_similar_items")(self.find_similar_items)
            bot.tree.command(name="user_neighborhood")(self.user_neighborhood)
            bot.tree.command(name="collaborative_recommend")(self.collaborative_recommend)

    async def find_similar_users(self, interaction):
        """Handle find_similar_users command"""
        await interaction.response.send_message(f"{agent_name}: find_similar_users command received!")

    async def find_similar_items(self, interaction):
        """Handle find_similar_items command"""
        await interaction.response.send_message(f"{agent_name}: find_similar_items command received!")

    async def user_neighborhood(self, interaction):
        """Handle user_neighborhood command"""
        await interaction.response.send_message(f"{agent_name}: user_neighborhood command received!")

    async def collaborative_recommend(self, interaction):
        """Handle collaborative_recommend command"""
        await interaction.response.send_message(f"{agent_name}: collaborative_recommend command received!")

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
