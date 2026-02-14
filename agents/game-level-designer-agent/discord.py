#!/usr/bin/env python3
"""
Discord bot integration for game-level-designer-agent
"""

import discord
from discord.ext import commands
from discord import app_commands
import logging
from pathlib import Path
import sys

# Add parent directory to path to import agent
sys.path.insert(0, str(Path(__file__).parent.parent))
from agent import GameLevelDesignerAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DiscordBot(commands.Bot):
    """Discord bot for game-level-designer-agent"""

    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True

        super().__init__(
            command_prefix="!",
            intents=intents,
            activity=discord.Activity(type=discord.ActivityType.watching, name="for commands")
        )

        self.agent = GameLevelDesignerAgent()

    async def setup_hook(self):
        """Setup hook for bot"""
        await self.tree.sync()
        logger.info("Commands synced")

            bot.tree.command(name="create_level")(self.create_level)
            bot.tree.command(name="add_object")(self.add_object)
            bot.tree.command(name="level_flow")(self.level_flow)
            bot.tree.command(name="playtest")(self.playtest)

    async def create_level(self, interaction):
        """Handle create_level command"""
        await interaction.response.send_message(f"{agent_name}: create_level command received!")

    async def add_object(self, interaction):
        """Handle add_object command"""
        await interaction.response.send_message(f"{agent_name}: add_object command received!")

    async def level_flow(self, interaction):
        """Handle level_flow command"""
        await interaction.response.send_message(f"{agent_name}: level_flow command received!")

    async def playtest(self, interaction):
        """Handle playtest command"""
        await interaction.response.send_message(f"{agent_name}: playtest command received!")

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
