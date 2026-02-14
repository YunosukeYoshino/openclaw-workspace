#!/usr/bin/env python3
"""
Discord bot integration for ai-model-registry-agent
"""

import discord
from discord.ext import commands
from discord import app_commands
import logging
from pathlib import Path
import sys

# Add parent directory to path to import agent
sys.path.insert(0, str(Path(__file__).parent.parent))
from agent import AiModelRegistryAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DiscordBot(commands.Bot):
    """Discord bot for ai-model-registry-agent"""

    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True

        super().__init__(
            command_prefix="!",
            intents=intents,
            activity=discord.Activity(type=discord.ActivityType.watching, name="for commands")
        )

        self.agent = AiModelRegistryAgent()

    async def setup_hook(self):
        """Setup hook for bot"""
        await self.tree.sync()
        logger.info("Commands synced")

            bot.tree.command(name="register_model")(self.register_model)
            bot.tree.command(name="add_version")(self.add_version)
            bot.tree.command(name="deploy_model")(self.deploy_model)
            bot.tree.command(name="model_metadata")(self.model_metadata)

    async def register_model(self, interaction):
        """Handle register_model command"""
        await interaction.response.send_message(f"{agent_name}: register_model command received!")

    async def add_version(self, interaction):
        """Handle add_version command"""
        await interaction.response.send_message(f"{agent_name}: add_version command received!")

    async def deploy_model(self, interaction):
        """Handle deploy_model command"""
        await interaction.response.send_message(f"{agent_name}: deploy_model command received!")

    async def model_metadata(self, interaction):
        """Handle model_metadata command"""
        await interaction.response.send_message(f"{agent_name}: model_metadata command received!")

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
