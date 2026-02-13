#!/usr/bin/env python3
"""
erotic-brand-collab-agent - えっちブランドコラボエージェント / Erotic Brand Collaboration Agent
ブランドコラボ企画、スポンサーシップ管理、PRキャンペーンを行うエージェント
Plans brand collaborations, manages sponsorships, and runs PR campaigns
"""

import discord
from discord.ext import commands
from db import EroticBrandCollabAgentDB
from typing import Optional, List, Dict, Any
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("EroticBrandCollabAgent")

class EroticBrandCollabAgent(commands.Cog):
    """えっちブランドコラボエージェント / Erotic Brand Collaboration Agent"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db = EroticBrandCollabAgentDB()
        logger.info("EroticBrandCollabAgent initialized")

    @commands.group(name="eroticbrandcollabagent", invoke_without_command=True)
    async def eroticbrandcollabagent(self, ctx: commands.Context):
        """えっちブランドコラボエージェントのメインコマンド / Main command for Erotic Brand Collaboration Agent"""
        embed = discord.Embed(
            title="えっちブランドコラボエージェント / Erotic Brand Collaboration Agent",
            description="ブランドコラボ企画、スポンサーシップ管理、PRキャンペーンを行うエージェント\n\nPlans brand collaborations, manages sponsorships, and runs PR campaigns",
            color=discord.Color.blue()
        )
        embed.add_field(
            name="Commands / コマンド",
            value="
`eroticbrandcollabagent status` - ステータス確認
`eroticbrandcollabagent add` - 追加
`eroticbrandcollabagent list` - 一覧表示
`eroticbrandcollabagent search` - 検索
`eroticbrandcollabagent remove` - 削除
".strip(),
            inline=False
        )
        await ctx.send(embed=embed)

    @eroticbrandcollabagent.command(name="status")
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

    @eroticbrandcollabagent.command(name="add")
    async def add_item(self, ctx: commands.Context, *, content: str):
        try:
            item_id = self.db.add_item(content, ctx.author.id)
            msg = "Added successfully (ID: " + str(item_id) + ") / 追加しました (ID: " + str(item_id) + ")"
            await ctx.send(msg)
        except Exception as e:
            logger.error("Error in add command: " + str(e))
            await ctx.send("Error adding item / アイテムの追加中にエラーが発生しました")

    @eroticbrandcollabagent.command(name="list")
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

    @eroticbrandcollabagent.command(name="search")
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

    @eroticbrandcollabagent.command(name="remove")
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
    await bot.add_cog(EroticBrandCollabAgent(bot))
