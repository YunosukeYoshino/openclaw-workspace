#!/usr/bin/env python3
"""
Discord bot integration for privilege-access-agent
"""

import discord
from discord.ext import commands
from discord import app_commands
import logging
from pathlib import Path
import sys

# Add parent directory to path to import agent
sys.path.insert(0, str(Path(__file__).parent.parent))
from agent import PrivilegeAccessAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DiscordBot(commands.Bot):
    """Discord bot for privilege-access-agent"""

    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True

        super().__init__(
            command_prefix="!",
            intents=intents,
            activity=discord.Activity(type=discord.ActivityType.watching, name="for commands")
        )

        self.agent = PrivilegeAccessAgent()

    async def setup_hook(self):
        """Setup hook for bot"""
        await self.tree.sync()
        logger.info("Commands synced")

            bot.tree.command(name="privileges")(self.privileges)
            bot.tree.command(name="request_access")(self.request_access)
            bot.tree.command(name="approve_request")(self.approve_request)
            bot.tree.command(name="audit_log")(self.audit_log)

    async def privileges(self, interaction):
        """Handle privileges command"""
        await interaction.response.send_message(f"{agent_name}: privileges command received!")

    async def request_access(self, interaction):
        """Handle request_access command"""
        await interaction.response.send_message(f"{agent_name}: request_access command received!")

    async def approve_request(self, interaction):
        """Handle approve_request command"""
        await interaction.response.send_message(f"{agent_name}: approve_request command received!")

    async def audit_log(self, interaction):
        """Handle audit_log command"""
        await interaction.response.send_message(f"{agent_name}: audit_log command received!")

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
