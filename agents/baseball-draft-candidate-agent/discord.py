#!/usr/bin/env python3
"""
野球ドラフト候補エージェント Discord インテグレーション
"""

import discord
from discord.ext import commands
import logging

class BaseballDraftCandidateAgentDiscord(commands.Cog):
    """野球ドラフト候補エージェント Discord ボット"""

    def __init__(self, bot, db):
        self.bot = bot
        self.db = db
        self.logger = logging.getLogger(__name__)

    @commands.command(name="baseball_draft_candidate_agent_info")
    async def agent_info(self, ctx):
        """エージェント情報を表示"""
        embed = discord.Embed(
            title="野球ドラフト候補エージェント",
            description="ドラフト候補選手のプロフィール、統計、評価",
            color=discord.Color.blue()
        )
        embed.add_field(name="エージェント名", value="baseball-draft-candidate-agent")
        await ctx.send(embed=embed)

    @commands.command(name="baseball_draft_candidate_agent_list")
    async def list_records(self, ctx, limit: int = 10):
        """レコード一覧を表示"""
        records = self.db.list_records(limit=limit)
        if not records:
            await ctx.send("レコードがありません")
            return

        embed = discord.Embed(
            title="野球ドラフト候補エージェント - レコード一覧",
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
    from .db import BaseballDraftCandidateAgentDB
    db = BaseballDraftCandidateAgentDB()
    bot.add_cog(BaseballDraftCandidateAgentDiscord(bot, db))

def to_camel_case(snake_str):
    return ''.join(word.capitalize() for word in snake_str.split('-'))
