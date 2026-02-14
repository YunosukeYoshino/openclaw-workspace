#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Discordボットモジュール - エッジデバイスエージェント
"""

import discord
from discord.ext import commands
import logging
from typing import Optional
from .db import Database

logger = logging.getLogger(__name__)

class DiscordBot(commands.Bot):
    """Discordボット"""

    def __init__(self, db: Database, command_prefix: str = "!"):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix=command_prefix, intents=intents, help_command=commands.DefaultHelpCommand())
        self.db = db

    async def on_ready(self):
        logger.info(f"Logged in as {self.user.name} ({self.user.id})")
        await self.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"for commands"))

    async def on_message(self, message: discord.Message):
        if message.author.id == self.user.id:
            return
        await self.process_commands(message)

    @commands.command(name="stats")
    async def cmd_stats(self, ctx: commands.Context):
        stats = self.db.get_stats()
        embed = discord.Embed(title="📊 統計情報", color=discord.Color.blue())
        embed.add_field(name="総レコード数", value=str(stats["total_records"]), inline=False)
        embed.add_field(name="データベースパス", value=stats["db_path"], inline=False)
        await ctx.send(embed=embed)

    @commands.command(name="info")
    async def cmd_info(self, ctx: commands.Context):
        embed = discord.Embed(title="エッジデバイスエージェント", description="エッジデバイスの管理・監視を行うエージェント", color=discord.Color.green())
        embed.add_field(name="カテゴリ", value="エッジコンピューティング", inline=False)
        await ctx.send(embed=embed)

async def run_bot(token: str, db: Database):
    bot = DiscordBot(db)
    await bot.start(token)

if __name__ == "__main__":
    import os
    DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
    if not DISCORD_TOKEN:
        print("DISCORD_TOKEN environment variable is required")
        exit(1)
    db = Database()
