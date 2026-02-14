#!/usr/bin/env python3
"""
Discord bot integration for baseball-team-management-agent
"""

import discord
from discord.ext import commands
from discord import app_commands
import logging
from pathlib import Path
import sys

# Add parent directory to path to import agent
sys.path.insert(0, str(Path(__file__).parent.parent))
from agent import BaseballTeamManagementAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DiscordBot(commands.Bot):
    """Discord bot for baseball-team-management-agent"""

    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True

        super().__init__(
            command_prefix="!",
            intents=intents,
            activity=discord.Activity(type=discord.ActivityType.watching, name="for commands")
        )

        self.agent = BaseballTeamManagementAgent()

    async def setup_hook(self):
        """Setup hook for bot"""
        await self.tree.sync()
        logger.info("Commands synced")

            bot.tree.command(name="team_info")(self.team_info)
            bot.tree.command(name="roster")(self.roster)
            bot.tree.command(name="staff")(self.staff)
            bot.tree.command(name="contracts")(self.contracts)
            bot.tree.command(name="manage_team")(self.manage_team)

    async def team_info(self, interaction):
        """Handle team_info command"""
        await interaction.response.send_message(f"{agent_name}: team_info command received!")

    async def roster(self, interaction):
        """Handle roster command"""
        await interaction.response.send_message(f"{agent_name}: roster command received!")

    async def staff(self, interaction):
        """Handle staff command"""
        await interaction.response.send_message(f"{agent_name}: staff command received!")

    async def contracts(self, interaction):
        """Handle contracts command"""
        await interaction.response.send_message(f"{agent_name}: contracts command received!")

    async def manage_team(self, interaction):
        """Handle manage_team command"""
        await interaction.response.send_message(f"{agent_name}: manage_team command received!")

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
