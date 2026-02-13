#!/usr/bin/env python3
"""
野球伝説選手プロフィールエージェント Discord インテグレーション
"""

import discord
from discord.ext import commands
import logging

class BaseballLegendProfileAgentDiscord(commands.Cog):
    """野球伝説選手プロフィールエージェント Discord ボット"""

    def __init__(self, bot, db):
        self.bot = bot
        self.db = db
        self.logger = logging.getLogger(__name__)

    @commands.command(name="baseball_legend_profile_agent_info")
    async def agent_info(self, ctx):
        """エージェント情報を表示"""
        embed = discord.Embed(
            title="野球伝説選手プロフィールエージェント",
            description="殿堂入り選手、レジェンド選手のプロフィール管理",
            color=discord.Color.blue()
        )
        embed.add_field(name="エージェント名", value="baseball-legend-profile-agent")
        await ctx.send(embed=embed)

    @commands.command(name="baseball_legend_profile_agent_list")
    async def list_records(self, ctx, limit: int = 10):
        """レコード一覧を表示"""
        records = self.db.list_records(limit=limit)
        if not records:
            await ctx.send("レコードがありません")
            return

        embed = discord.Embed(
            title="野球伝説選手プロフィールエージェント - レコード一覧",
            color=discord.Color.green()
        )
        for record in records[:10]:
            embed.add_field(
                name=record['title'] or f"ID: {record['id']}",
                value=record['description'] or "説明なし",
                inline=False
            )
        await ctx.send(embed=embed)

def setup(bot):
    """ボットにCogを追加"""
    from .db import BaseballLegendProfileAgentDB
    db = BaseballLegendProfileAgentDB()
    bot.add_cog(BaseballLegendProfileAgentDiscord(bot, db))

def to_camel_case(snake_str):
    return ''.join(word.capitalize() for word in snake_str.split('-'))
