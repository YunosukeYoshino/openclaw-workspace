#!/usr/bin/env python3
"""
ゲーム理論エージェント Discord インテグレーション
"""

import discord
from discord.ext import commands
import logging

class GameTheoryAgentDiscord(commands.Cog):
    """ゲーム理論エージェント Discord ボット"""

    def __init__(self, bot, db):
        self.bot = bot
        self.db = db
        self.logger = logging.getLogger(__name__)

    @commands.command(name="game_theory_agent_info")
    async def agent_info(self, ctx):
        """エージェント情報を表示"""
        embed = discord.Embed(
            title="ゲーム理論エージェント",
            description="プレイヤー間の意思決定、ナッシュ均衡の分析",
            color=discord.Color.blue()
        )
        embed.add_field(name="エージェント名", value="game-theory-agent")
        await ctx.send(embed=embed)

    @commands.command(name="game_theory_agent_sim")
    async def run_simulation(self, ctx, iterations: int = 1000):
        """シミュレーションを実行"""
        await ctx.send(f"シミュレーションを実行中 ({iterations}回)...")

    @commands.command(name="game_theory_agent_stats")
    async def show_stats(self, ctx):
        """統計情報を表示"""
        simulations = self.db.list_simulations(limit=10)
        if not simulations:
            await ctx.send("シミュレーション結果がありません")
            return

        embed = discord.Embed(
            title="ゲーム理論エージェント - 統計",
            color=discord.Color.green()
        )
        for sim in simulations[:5]:
            embed.add_field(
                name=sim['name'] or f"ID: {sim['id']}",
                value=f"作成日: {sim['created_at']}",
                inline=False
            )
        await ctx.send(embed=embed)

def setup(bot):
    """ボットにCogを追加"""
    from .db import GameTheoryAgentDB
    db = GameTheoryAgentDB()
    bot.add_cog(GameTheoryAgentDiscord(bot, db))
