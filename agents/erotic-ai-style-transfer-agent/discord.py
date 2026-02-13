#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Discord Integration for Erotic AI Style Transfer Agent
えっちAIスタイル変換エージェント
"""

import discord
from discord.ext import commands, tasks
import logging
from typing import Optional
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("erotic-ai-style-transfer-agent")


class EroticAiStyleTransferAgentDiscord(commands.Bot):
    """Discord bot for Erotic AI Style Transfer Agent"""

    def __init__(self, command_prefix: str = "!", intents: Optional[discord.Intents] = None):
        intents = intents or discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix=command_prefix, intents=intents)
        self.started = False

    async def setup_hook(self):
        """Called when the bot is starting."""
        await self.add_commands()
        logger.info(f""えっちAIスタイル変換エージェント" Discord bot ready")

    async def add_commands(self):
        """Add bot commands."""

        @self.command(name="status")
        async def status(ctx):
            """Show bot status."""
            embed = discord.Embed(
                title="Erotic AI Style Transfer Agent Status",
                color=discord.Color.blue()
            )
            embed.add_field(name="Status", value="✅ Online", inline=True)
            embed.add_field(name="Version", value="1.0.0", inline=True)
            await ctx.send(embed=embed)

        @self.command(name="help")
        async def help_cmd(ctx):
            """Show help message."""
            embed = discord.Embed(
                title="Erotic AI Style Transfer Agent - Help",
                description="えっちAIスタイル変換エージェント",
                color=discord.Color.green()
            )
            embed.add_field(name="Commands", value="`!status` - Show status\n`!help` - Show this help", inline=False)
            await ctx.send(embed=embed)

    async def on_ready(self):
        """Called when the bot is ready."""
        logger.info(f""えっちAIスタイル変換エージェント" bot logged in as {self.user}")
        self.started = True

    async def on_message(self, message):
        """Called when a message is received."""
        if message.author == self.user:
            return
        await self.process_commands(message)

    async def send_notification(self, channel_id: int, content: str, **kwargs):
        """Send notification to a channel."""
        try:
            channel = self.get_channel(channel_id)
            if channel:
                await channel.send(content, **kwargs)
        except Exception as e:
            logger.error(f"Failed to send notification: {e}")

    async def send_embed(self, channel_id: int, title: str, description: str, **kwargs):
        """Send an embed to a channel."""
        try:
            channel = self.get_channel(channel_id)
            if channel:
                embed = discord.Embed(title=title, description=description, **kwargs)
                await channel.send(embed=embed)
        except Exception as e:
            logger.error(f"Failed to send embed: {e}")


async def run_bot(token: str):
    """Run the Discord bot."""
    bot = EroticAiStyleTransferAgentDiscord()
    await bot.start(token)


if __name__ == "__main__":
    import os
    token = os.getenv("DISCORD_TOKEN", "")
    if not token:
        logger.warning("DISCORD_TOKEN not set, running without Discord")
    else:
        import asyncio
        asyncio.run(run_bot(token))
