#!/usr/bin/env python3
"""
Discord bot integration for ai-experiment-tracking-agent
"""

import discord
from discord.ext import commands
from discord import app_commands
import logging
from pathlib import Path
import sys

# Add parent directory to path to import agent
sys.path.insert(0, str(Path(__file__).parent.parent))
from agent import AiExperimentTrackingAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DiscordBot(commands.Bot):
    """Discord bot for ai-experiment-tracking-agent"""

    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True

        super().__init__(
            command_prefix="!",
            intents=intents,
            activity=discord.Activity(type=discord.ActivityType.watching, name="for commands")
        )

        self.agent = AiExperimentTrackingAgent()

    async def setup_hook(self):
        """Setup hook for bot"""
        await self.tree.sync()
        logger.info("Commands synced")

            bot.tree.command(name="create_experiment")(self.create_experiment)
            bot.tree.command(name="log_run")(self.log_run)
            bot.tree.command(name="compare_runs")(self.compare_runs)
            bot.tree.command(name="experiment_history")(self.experiment_history)

    async def create_experiment(self, interaction):
        """Handle create_experiment command"""
        await interaction.response.send_message(f"{agent_name}: create_experiment command received!")

    async def log_run(self, interaction):
        """Handle log_run command"""
        await interaction.response.send_message(f"{agent_name}: log_run command received!")

    async def compare_runs(self, interaction):
        """Handle compare_runs command"""
        await interaction.response.send_message(f"{agent_name}: compare_runs command received!")

    async def experiment_history(self, interaction):
        """Handle experiment_history command"""
        await interaction.response.send_message(f"{agent_name}: experiment_history command received!")

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
