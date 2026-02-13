#!/usr/bin/env python3
"""
esports-interview-agent - eスポーツインタビューエージェント / Esports Interview Agent
選手インタビュー準備、質問生成、翻訳サポートを行うエージェント
Prepares player interviews, generates questions, and provides translation support
"""

import discord
from discord.ext import commands
from db import EsportsInterviewAgentDB
from typing import Optional, List, Dict, Any
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("EsportsInterviewAgent")

class EsportsInterviewAgent(commands.Cog):
    """eスポーツインタビューエージェント / Esports Interview Agent"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db = EsportsInterviewAgentDB()
        logger.info("EsportsInterviewAgent initialized")

    @commands.group(name="esportsinterviewagent", invoke_without_command=True)
    async def esportsinterviewagent(self, ctx: commands.Context):
        """eスポーツインタビューエージェントのメインコマンド / Main command for Esports Interview Agent"""
        embed = discord.Embed(
            title="eスポーツインタビューエージェント / Esports Interview Agent",
            description="選手インタビュー準備、質問生成、翻訳サポートを行うエージェント\n\nPrepares player interviews, generates questions, and provides translation support",
            color=discord.Color.blue()
        )
        embed.add_field(
            name="Commands / コマンド",
            value="
`esportsinterviewagent status` - ステータス確認
`esportsinterviewagent add` - 追加
`esportsinterviewagent list` - 一覧表示
`esportsinterviewagent search` - 検索
`esportsinterviewagent remove` - 削除
".strip(),
            inline=False
        )
        await ctx.send(embed=embed)

    @esportsinterviewagent.command(name="status")
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

    @esportsinterviewagent.command(name="add")
    async def add_item(self, ctx: commands.Context, *, content: str):
        try:
            item_id = self.db.add_item(content, ctx.author.id)
            msg = "Added successfully (ID: " + str(item_id) + ") / 追加しました (ID: " + str(item_id) + ")"
            await ctx.send(msg)
        except Exception as e:
            logger.error("Error in add command: " + str(e))
            await ctx.send("Error adding item / アイテムの追加中にエラーが発生しました")

    @esportsinterviewagent.command(name="list")
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

    @esportsinterviewagent.command(name="search")
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

    @esportsinterviewagent.command(name="remove")
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
    await bot.add_cog(EsportsInterviewAgent(bot))
