#!/usr/bin/env python3
"""
baseball-draft-history-agent - 野球ドラフト歴史エージェント / Baseball Draft History Agent
過去のドラフトデータ、選手追跡、ドラフト成功率分析を行うエージェント
Tracks past draft data, player careers, and analyzes draft success rates
"""

import discord
from discord.ext import commands
from db import BaseballDraftHistoryAgentDB
from typing import Optional, List, Dict, Any
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("BaseballDraftHistoryAgent")

class BaseballDraftHistoryAgent(commands.Cog):
    """野球ドラフト歴史エージェント / Baseball Draft History Agent"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db = BaseballDraftHistoryAgentDB()
        logger.info("BaseballDraftHistoryAgent initialized")

    @commands.group(name="baseballdrafthistoryagent", invoke_without_command=True)
    async def baseballdrafthistoryagent(self, ctx: commands.Context):
        """野球ドラフト歴史エージェントのメインコマンド / Main command for Baseball Draft History Agent"""
        embed = discord.Embed(
            title="野球ドラフト歴史エージェント / Baseball Draft History Agent",
            description="過去のドラフトデータ、選手追跡、ドラフト成功率分析を行うエージェント\n\nTracks past draft data, player careers, and analyzes draft success rates",
            color=discord.Color.blue()
        )
        embed.add_field(
            name="Commands / コマンド",
            value="
`baseballdrafthistoryagent status` - ステータス確認
`baseballdrafthistoryagent add` - 追加
`baseballdrafthistoryagent list` - 一覧表示
`baseballdrafthistoryagent search` - 検索
`baseballdrafthistoryagent remove` - 削除
".strip(),
            inline=False
        )
        await ctx.send(embed=embed)

    @baseballdrafthistoryagent.command(name="status")
    async def status(self, ctx: commands.Context):
        try:
            stats = self.db.get_stats()
            embed = discord.Embed(title="Status / ステータス", color=discord.Color.green())
            embed.add_field(name="Total Items", value=stats.get("total", 0), inline=True)
            embed.add_field(name="Active Items", value=stats.get("active", 0), inline=True)
            size_kb = stats.get("size", 0)
            embed.add_field(name="Database Size", value=str(round(size_kb, 2)) + " KB", inline=True)
            await ctx.send(embed=embed)
        except Exception as e:
            logger.error("Error in status command: " + str(e))
            await ctx.send("Error retrieving status / ステータスの取得中にエラーが発生しました")

    @baseballdrafthistoryagent.command(name="add")
    async def add_item(self, ctx: commands.Context, *, content: str):
        try:
            item_id = self.db.add_item(content, ctx.author.id)
            msg = "Added successfully (ID: " + str(item_id) + ") / 追加しました (ID: " + str(item_id) + ")"
            await ctx.send(msg)
        except Exception as e:
            logger.error("Error in add command: " + str(e))
            await ctx.send("Error adding item / アイテムの追加中にエラーが発生しました")

    @baseballdrafthistoryagent.command(name="list")
    async def list_items(self, ctx: commands.Context, limit: int = 10):
        try:
            items = self.db.list_items(limit=limit)
            if not items:
                await ctx.send("No items found / アイテムが見つかりませんでした")
                return
            embed = discord.Embed(title="Items List / アイテム一覧", color=discord.Color.blue())
            for item in items[:25]:
                embed.add_field(name="ID: " + str(item['id']), value=item['content'][:100] + "...", inline=False)
            await ctx.send(embed=embed)
        except Exception as e:
            logger.error("Error in list command: " + str(e))
            await ctx.send("Error listing items / アイテム一覧の取得中にエラーが発生しました")

    @baseballdrafthistoryagent.command(name="search")
    async def search_items(self, ctx: commands.Context, *, query: str):
        try:
            items = self.db.search_items(query)
            if not items:
                msg = "No items found for '" + query + "' / '" + query + "' に一致するアイテムが見つかりませんでした"
                await ctx.send(msg)
                return
            embed = discord.Embed(title="Search Results: " + query + " / 検索結果: " + query, color=discord.Color.blue())
            for item in items[:25]:
                embed.add_field(name="ID: " + str(item['id']), value=item['content'][:100] + "...", inline=False)
            await ctx.send(embed=embed)
        except Exception as e:
            logger.error("Error in search command: " + str(e))
            await ctx.send("Error searching items / アイテムの検索中にエラーが発生しました")

    @baseballdrafthistoryagent.command(name="remove")
    async def remove_item(self, ctx: commands.Context, item_id: int):
        try:
            if self.db.remove_item(item_id):
                msg = "Item " + str(item_id) + " removed successfully / アイテム " + str(item_id) + " を削除しました"
                await ctx.send(msg)
            else:
                msg = "Item " + str(item_id) + " not found / アイテム " + str(item_id) + " が見つかりませんでした"
                await ctx.send(msg)
        except Exception as e:
            logger.error("Error in remove command: " + str(e))
            await ctx.send("Error removing item / アイテムの削除中にエラーが発生しました")

    @commands.Cog.listener()
    async def on_ready(self):
        logger.info(str(self.__class__.__name__) + " is ready")

async def setup(bot: commands.Bot):
    await bot.add_cog(BaseballDraftHistoryAgent(bot))
