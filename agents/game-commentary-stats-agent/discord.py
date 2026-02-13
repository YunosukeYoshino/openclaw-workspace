#!/usr/bin/env python3
"""
Discord Bot module for {agent_name}
{agent_name}のDiscord Botモジュール
"""

import discord
from discord.ext import commands
from typing import Optional
import os


class {class_name}Bot(commands.Cog):
    """Discord Bot for {agent_name} / {agent_name}のDiscord Bot"""

    def __init__(self, bot: commands.Bot, agent):
        self.bot = bot
        self.agent = agent

    @commands.command(name="{discord_prefix}add")
    async def add_entry(self, ctx: commands.Context, title: str, *, content: str):
        """Add a {agent_short} entry / {agent_short}エントリーを追加"""
        entry_id = self.agent.add_entry(title, content)
        await ctx.send(f"Added entry #{entry_id}: {title}")

    @commands.command(name="{discord_prefix}list")
    async def list_entries(self, ctx: commands.Context, limit: int = 10):
        """List {agent_short} entries / {agent_short}エントリーを一覧"""
        entries = self.agent.list_entries(limit)
        if not entries:
            await ctx.send("No entries found / エントリーが見つかりません")
            return

        response = f"__{agent_short} Entries__\n\n"
        for entry in entries:
            response += f"**#{entry['id']}** {entry['title']}\n"

        await ctx.send(response)

    @commands.command(name="{discord_prefix}search")
    async def search_entries(self, ctx: commands.Context, *, query: str):
        """Search {agent_short} entries / {agent_short}エントリーを検索"""
        entries = self.agent.search_entries(query)
        if not entries:
            await ctx.send(f"No entries found for: {query}")
            return

        response = f"__Search Results for: {query}__\n\n"
        for entry in entries[:10]:
            response += f"**#{entry['id']}** {entry['title']}\n"

        await ctx.send(response)


def setup(bot: commands.Bot, agent):
    """Setup the cog / Cogをセットアップ"""
    bot.add_cog({class_name}Bot(bot, agent))
