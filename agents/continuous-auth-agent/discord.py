#!/usr/bin/env python3
"""
Discord bot integration for continuous-auth-agent
"""

import discord
from discord.ext import commands
from discord import app_commands
import logging
from pathlib import Path
import sys

# Add parent directory to path to import agent
sys.path.insert(0, str(Path(__file__).parent.parent))
from agent import ContinuousAuthAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DiscordBot(commands.Bot):
    """Discord bot for continuous-auth-agent"""

    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True

        super().__init__(
            command_prefix="!",
            intents=intents,
            activity=discord.Activity(type=discord.ActivityType.watching, name="for commands")
        )

        self.agent = ContinuousAuthAgent()

    async def setup_hook(self):
        """Setup hook for bot"""
        await self.tree.sync()
        logger.info("Commands synced")

            bot.tree.command(name="session_status")(self.session_status)
            bot.tree.command(name="auth_history")(self.auth_history)
            bot.tree.command(name="set_trigger")(self.set_trigger)
            bot.tree.command(name="force_reauth")(self.force_reauth)

    async def session_status(self, interaction):
        """Handle session_status command"""
        await interaction.response.send_message(f"{agent_name}: session_status command received!")

    async def auth_history(self, interaction):
        """Handle auth_history command"""
        await interaction.response.send_message(f"{agent_name}: auth_history command received!")

    async def set_trigger(self, interaction):
        """Handle set_trigger command"""
        await interaction.response.send_message(f"{agent_name}: set_trigger command received!")

    async def force_reauth(self, interaction):
        """Handle force_reauth command"""
        await interaction.response.send_message(f"{agent_name}: force_reauth command received!")

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
