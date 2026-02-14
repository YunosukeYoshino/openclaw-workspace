#!/usr/bin/env python3
"""
Discord bot integration for security-gdpr-agent
"""

import discord
from discord.ext import commands
from discord import app_commands
import logging
from pathlib import Path
import sys

# Add parent directory to path to import agent
sys.path.insert(0, str(Path(__file__).parent.parent))
from agent import SecurityGdprAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DiscordBot(commands.Bot):
    """Discord bot for security-gdpr-agent"""

    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True

        super().__init__(
            command_prefix="!",
            intents=intents,
            activity=discord.Activity(type=discord.ActivityType.watching, name="for commands")
        )

        self.agent = SecurityGdprAgent()

    async def setup_hook(self):
        """Setup hook for bot"""
        await self.tree.sync()
        logger.info("Commands synced")

            bot.tree.command(name="subject_info")(self.subject_info)
            bot.tree.command(name="manage_consent")(self.manage_consent)
            bot.tree.command(name="handle_request")(self.handle_request)
            bot.tree.command(name="privacy_audit")(self.privacy_audit)

    async def subject_info(self, interaction):
        """Handle subject_info command"""
        await interaction.response.send_message(f"{agent_name}: subject_info command received!")

    async def manage_consent(self, interaction):
        """Handle manage_consent command"""
        await interaction.response.send_message(f"{agent_name}: manage_consent command received!")

    async def handle_request(self, interaction):
        """Handle handle_request command"""
        await interaction.response.send_message(f"{agent_name}: handle_request command received!")

    async def privacy_audit(self, interaction):
        """Handle privacy_audit command"""
        await interaction.response.send_message(f"{agent_name}: privacy_audit command received!")

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
