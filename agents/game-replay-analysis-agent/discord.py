#!/usr/bin/env python3
"""
ゲームリプレイ分析エージェント - Discord Bot Module
ゲームモデリング・シミュレーションエージェントDiscordボットモジュール
"""

import discord
from discord.ext import commands
import logging
import json
from typing import Optional

from db import GameReplayAnalysisAgentDatabase

logger = logging.getLogger(__name__)

class GameReplayAnalysisAgentBot(commands.Bot):
    """ゲームモデリング・シミュレーションDiscordボット"""

    def __init__(self, command_prefix: str = "!modeling", db_path: str = "game_modeling.db"):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix=command_prefix, intents=intents)

        self.db = GameReplayAnalysisAgentDatabase(db_path)

    async def on_ready(self):
        logger.info(f"{self.user.name} is ready!")

    async def on_message(self, message: discord.Message):
        if message.author == self.user:
            return

        await self.process_commands(message)

    @commands.command(name="prob", aliases=["probability"])
    async def get_probability(self, ctx: commands.Context, event_name: Optional[str] = None):
        """確率計算結果を表示"""
        calcs = self.db.get_probability_calculations(event_name)

        if not calcs:
            await ctx.send("No probability calculations found.")
            return

        embed = discord.Embed(
            title="Probability Calculations / 確率計算",
            color=discord.Color.blue()
        )

        for calc in calcs[:5]:
            embed.add_field(
                name=f"{calc['event_name']}",
                value=f"Success Rate: {calc['success_rate']}\nCalculated: {calc['calculated_probability']:.4f}\nTrials: {calc['trials']}",
                inline=False
            )

        await ctx.send(embed=embed)

    @commands.command(name="sim", aliases=["simulation"])
    async def get_simulation(self, ctx: commands.Context, sim_type: Optional[str] = None):
        """シミュレーション結果を表示"""
        sims = self.db.get_simulations(sim_type)

        if not sims:
            await ctx.send("No simulations found.")
            return

        embed = discord.Embed(
            title="Simulations / シミュレーション",
            color=discord.Color.green()
        )

        for sim in sims[:5]:
            results = json.loads(sim.get("results_json", "[]"))[:3]
            embed.add_field(
                name=f"{sim['simulation_type']} ({sim['iterations']} iterations)",
                value=f"Average: {sim['average_result']:.2f}\nSample: {results}",
                inline=False
            )

        await ctx.send(embed=embed)

    @commands.command(name="mech", aliases=["mechanics"])
    async def get_mechanics(self, ctx: commands.Context):
        """メカニクス一覧を表示"""
        mechanics = self.db.get_mechanics()

        if not mechanics:
            await ctx.send("No mechanics found.")
            return

        embed = discord.Embed(
            title="Game Mechanics / ゲームメカニクス",
            color=discord.Color.orange()
        )

        for mech in mechanics[:5]:
            balance = f"Balance: {mech.get('balance_score', 'N/A')}"
            embed.add_field(
                name=f"{mech['mechanic_name']}",
                value=f"Formula: {mech.get('formula', 'N/A')}\n{balance}",
                inline=False
            )

        await ctx.send(embed=embed)

    @commands.command(name="theory", aliases=["gametheory"])
    async def get_game_theory(self, ctx: commands.Context):
        """ゲーム理論分析を表示"""
        analyses = self.db.get_game_theory_analyses()

        if not analyses:
            await ctx.send("No game theory analyses found.")
            return

        embed = discord.Embed(
            title="Game Theory Analyses / ゲーム理論分析",
            color=discord.Color.purple()
        )

        for analysis in analyses[:5]:
            embed.add_field(
                name=f"{analysis['scenario_name']} ({analysis['players_count']} players)",
                value=f"Nash: {analysis.get('nash_equilibrium', 'N/A')}\nOptimal: {analysis.get('optimal_strategy', 'N/A')}",
                inline=False
            )

        await ctx.send(embed=embed)

    @commands.command(name="replay", aliases=["replays"])
    async def get_replays(self, ctx: commands.Context, game_name: Optional[str] = None):
        """リプレイ一覧を表示"""
        replays = self.db.get_replays(game_name)

        if not replays:
            await ctx.send("No replays found.")
            return

        embed = discord.Embed(
            title="Replay Analyses / リプレイ分析",
            color=discord.Color.gold()
        )

        for replay in replays[:5]:
            patterns = json.loads(replay.get("patterns_found", "[]"))[:3]
            embed.add_field(
                name=f"{replay['game_name']} - {replay['player_name']}",
                value=f"Patterns: {patterns}",
                inline=False
            )

        await ctx.send(embed=embed)

    @commands.command(name="calculate", aliases=["calc"])
    async def calculate_prob(self, ctx: commands.Context, success_rate: float):
        """確率を計算"""
        await ctx.send(f"Calculating probability with success rate: {success_rate}")
        # 実際の計算は agent.py を使用

def main():
    import os

    token = os.getenv("DISCORD_TOKEN")
    if not token:
        logger.error("DISCORD_TOKEN environment variable not set")
        return

    bot = GameReplayAnalysisAgentBot()
    bot.run(token)

if __name__ == "__main__":
    main()
