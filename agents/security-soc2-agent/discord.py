#!/usr/bin/env python3
"""
Discord bot integration for security-soc2-agent
"""

import discord
from discord.ext import commands
from discord import app_commands
import logging
from pathlib import Path
import sys

# Add parent directory to path to import agent
sys.path.insert(0, str(Path(__file__).parent.parent))
from agent import SecuritySoc2Agent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DiscordBot(commands.Bot):
    """Discord bot for security-soc2-agent"""

    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True

        super().__init__(
            command_prefix="!",
            intents=intents,
            activity=discord.Activity(type=discord.ActivityType.watching, name="for commands")
        )

        self.agent = SecuritySoc2Agent()

    async def setup_hook(self):
        """Setup hook for bot"""
        await self.tree.sync()
        logger.info("Commands synced")

            bot.tree.command(name="trust_services")(self.trust_services)
            bot.tree.command(name="collect_evidence")(self.collect_evidence)
            bot.tree.command(name="audit_status")(self.audit_status)
            bot.tree.command(name="soc2_report")(self.soc2_report)

    async def trust_services(self, interaction):
        """Handle trust_services command"""
        await interaction.response.send_message(f"{agent_name}: trust_services command received!")

    async def collect_evidence(self, interaction):
        """Handle collect_evidence command"""
        await interaction.response.send_message(f"{agent_name}: collect_evidence command received!")

    async def audit_status(self, interaction):
        """Handle audit_status command"""
        await interaction.response.send_message(f"{agent_name}: audit_status command received!")

    async def soc2_report(self, interaction):
        """Handle soc2_report command"""
        await interaction.response.send_message(f"{agent_name}: soc2_report command received!")

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
