#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
erotic-user-behavior-agent - Discord Integration
Discord bot integration for erotic-user-behavior-agent
"""

import discord
from discord.ext import commands
import logging
from typing import Optional
import json
from pathlib import Path

class EroticUserBehaviorAgentDiscord:
    """Discord bot integration for erotic-user-behavior-agent"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.logger = logging.getLogger("erotic-user-behavior-agent.discord")
        self.config_path = Path(__file__).parent / "discord_config.json"
        self.config = self._load_config()

    def _load_config(self) -> dict:
        default_config = {
            "command_prefix": "!",
            "enabled_channels": [],
            "admin_roles": []
        }
        if self.config_path.exists():
            with open(self.config_path, "r", encoding="utf-8") as f:
                return {**default_config, **json.load(f)}
        return default_config

    def setup_commands(self):
        @self.bot.command(name="eroticuserbehavioragent_status")
        async def agent_status(ctx):
            embed = discord.Embed(
                title="erotic-user-behavior-agent Status",
                description="えっちユーザー行動エージェント。ユーザー行動のAI分析。",
                color=discord.Color.blue()
            )
            embed.add_field(name="Active", value="Yes", inline=True)
            embed.add_field(name="Version", value="1.0.0", inline=True)
            await ctx.send(embed=embed)

        @self.bot.command(name="eroticuserbehavioragent_help")
        async def agent_help(ctx):
            embed = discord.Embed(
                title="erotic-user-behavior-agent Help",
                description="えっちユーザー行動エージェント。ユーザー行動のAI分析。",
                color=discord.Color.green()
            )
            embed.add_field(
                name="Commands",
                value="`!eroticuserbehavioragent_status` - Show agent status\n`!eroticuserbehavioragent_help` - Show this help message",
                inline=False
            )
            await ctx.send(embed=embed)

    async def send_notification(self, channel_id: int, message: str, embed: discord.Embed = None):
        try:
            channel = self.bot.get_channel(channel_id)
            if channel:
                await channel.send(content=message, embed=embed)
                return True
        except Exception as e:
            self.logger.error("Failed to send notification: " + str(e))
        return False

    async def send_alert(self, channel_id: int, title: str, description: str, level: str = "info"):
        color_map = {
            "info": discord.Color.blue(),
            "warning": discord.Color.orange(),
            "error": discord.Color.red(),
            "success": discord.Color.green()
        }
        embed = discord.Embed(
            title=title,
            description=description,
            color=color_map.get(level, discord.Color.blue())
        )
        embed.set_footer(text="erotic-user-behavior-agent")
        return await self.send_notification(channel_id, "", embed)

def setup(bot: commands.Bot):
    discord_integration = EroticUserBehaviorAgentDiscord(bot)
    discord_integration.setup_commands()
    bot.add_cog(discord_integration)
    return discord_integration
