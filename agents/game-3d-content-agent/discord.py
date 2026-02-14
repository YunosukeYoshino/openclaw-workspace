#!/usr/bin/env python3
"""
Discord bot integration for game-3d-content-agent
"""

import discord
from discord.ext import commands
from discord import app_commands
import logging
from pathlib import Path
import sys

# Add parent directory to path to import agent
sys.path.insert(0, str(Path(__file__).parent.parent))
from agent import Game3DContentAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DiscordBot(commands.Bot):
    """Discord bot for game-3d-content-agent"""

    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True

        super().__init__(
            command_prefix="!",
            intents=intents,
            activity=discord.Activity(type=discord.ActivityType.watching, name="for commands")
        )

        self.agent = Game3DContentAgent()

    async def setup_hook(self):
        """Setup hook for bot"""
        await self.tree.sync()
        logger.info("Commands synced")

            bot.tree.command(name="add_model")(self.add_model)
            bot.tree.command(name="add_material")(self.add_material)
            bot.tree.command(name="add_animation")(self.add_animation)
            bot.tree.command(name="3d_library")(self.3d_library)

    async def add_model(self, interaction):
        """Handle add_model command"""
        await interaction.response.send_message(f"{agent_name}: add_model command received!")

    async def add_material(self, interaction):
        """Handle add_material command"""
        await interaction.response.send_message(f"{agent_name}: add_material command received!")

    async def add_animation(self, interaction):
        """Handle add_animation command"""
        await interaction.response.send_message(f"{agent_name}: add_animation command received!")

    async def 3d_library(self, interaction):
        """Handle 3d_library command"""
        await interaction.response.send_message(f"{agent_name}: 3d_library command received!")

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
