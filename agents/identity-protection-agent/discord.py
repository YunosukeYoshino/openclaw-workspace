#!/usr/bin/env python3
"""
Discord bot integration for identity-protection-agent
"""

import discord
from discord.ext import commands
from discord import app_commands
import logging
from pathlib import Path
import sys

# Add parent directory to path to import agent
sys.path.insert(0, str(Path(__file__).parent.parent))
from agent import IdentityProtectionAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DiscordBot(commands.Bot):
    """Discord bot for identity-protection-agent"""

    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True

        super().__init__(
            command_prefix="!",
            intents=intents,
            activity=discord.Activity(type=discord.ActivityType.watching, name="for commands")
        )

        self.agent = IdentityProtectionAgent()

    async def setup_hook(self):
        """Setup hook for bot"""
        await self.tree.sync()
        logger.info("Commands synced")

            bot.tree.command(name="protected_ids")(self.protected_ids)
            bot.tree.command(name="check_breach")(self.check_breach)
            bot.tree.command(name="alerts")(self.alerts)
            bot.tree.command(name="acknowledge_alert")(self.acknowledge_alert)

    async def protected_ids(self, interaction):
        """Handle protected_ids command"""
        await interaction.response.send_message(f"{agent_name}: protected_ids command received!")

    async def check_breach(self, interaction):
        """Handle check_breach command"""
        await interaction.response.send_message(f"{agent_name}: check_breach command received!")

    async def alerts(self, interaction):
        """Handle alerts command"""
        await interaction.response.send_message(f"{agent_name}: alerts command received!")

    async def acknowledge_alert(self, interaction):
        """Handle acknowledge_alert command"""
        await interaction.response.send_message(f"{agent_name}: acknowledge_alert command received!")

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
