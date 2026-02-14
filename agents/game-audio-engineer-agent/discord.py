#!/usr/bin/env python3
"""
Discord bot integration for game-audio-engineer-agent
"""

import discord
from discord.ext import commands
from discord import app_commands
import logging
from pathlib import Path
import sys

# Add parent directory to path to import agent
sys.path.insert(0, str(Path(__file__).parent.parent))
from agent import GameAudioEngineerAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DiscordBot(commands.Bot):
    """Discord bot for game-audio-engineer-agent"""

    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True

        super().__init__(
            command_prefix="!",
            intents=intents,
            activity=discord.Activity(type=discord.ActivityType.watching, name="for commands")
        )

        self.agent = GameAudioEngineerAgent()

    async def setup_hook(self):
        """Setup hook for bot"""
        await self.tree.sync()
        logger.info("Commands synced")

            bot.tree.command(name="add_music")(self.add_music)
            bot.tree.command(name="add_sfx")(self.add_sfx)
            bot.tree.command(name="voice_over")(self.voice_over)
            bot.tree.command(name="audio_library")(self.audio_library)

    async def add_music(self, interaction):
        """Handle add_music command"""
        await interaction.response.send_message(f"{agent_name}: add_music command received!")

    async def add_sfx(self, interaction):
        """Handle add_sfx command"""
        await interaction.response.send_message(f"{agent_name}: add_sfx command received!")

    async def voice_over(self, interaction):
        """Handle voice_over command"""
        await interaction.response.send_message(f"{agent_name}: voice_over command received!")

    async def audio_library(self, interaction):
        """Handle audio_library command"""
        await interaction.response.send_message(f"{agent_name}: audio_library command received!")

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
