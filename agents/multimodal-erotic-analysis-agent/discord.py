#!/usr/bin/env python3
"""
えっちコンテンツマルチモーダル分析エージェント - Discord Bot モジュール
"""

import discord
from discord.ext import commands
import os
from .agent import MultimodalEroticAnalysisAgent

class MultimodalEroticAnalysisAgentDiscord(commands.Cog):
    """えっちコンテンツマルチモーダル分析エージェント Discord Bot"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.agent = MultimodalEroticAnalysisAgent(bot)

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'🔞 えっちコンテンツマルチモーダル分析エージェント loaded and ready!')

    @commands.command(name='multimodal-erotic-analysis-agent')
    async def process_multimodal(self, ctx: commands.Context, media_url: str = None):
        """
        Multimodal AI agent for analyzing erotic content including images, videos, and audio

        画像、動画、音声を含むえっちコンテンツを分析するマルチモーダルAIエージェント

        Usage: !multimodal-erotic-analysis-agent [media_url]
        """
        if media_url is None and ctx.message.attachments:
            media_url = ctx.message.attachments[0].url

        if media_url is None:
            await ctx.send("Please provide a media URL or attach a file.")
            return

        await ctx.send(f"Processing media: {media_url}...")

        result = self.agent.analyze_media(media_url)

        embed = discord.Embed(
            title="🔞 Multimodal Analysis Result",
            color=discord.Color.green()
        )
        embed.add_field(name="Content Type", value=result.get("content_type", "unknown"), inline=True)
        embed.add_field(name="Confidence", value=f"{result.get('confidence', 0):.2%}", inline=True)
        embed.add_field(name="Tags", value=', '.join(result.get("tags", [])), inline=False)
        embed.add_field(name="Analysis", value=result.get("analysis_result", "N/A"), inline=False)

        await ctx.send(embed=embed)

    @commands.command(name='multimodal-erotic-analysis-agent-list')
    async def list_entries(self, ctx: commands.Context, limit: int = 10):
        """
        List recent entries

        Usage: !multimodal-erotic-analysis-agent-list [limit]
        """
        entries = self.agent.db.list_entries(limit=limit)

        if not entries:
            await ctx.send("No entries found.")
            return

        embed = discord.Embed(
            title="🔞 Recent Entries",
            color=discord.Color.blue()
        )

        for entry in entries[:5]:
            embed.add_field(
                name=f"Entry #{entry['id']} ({entry['content_type']})",
                value=f"Tags: {', '.join(entry['tags'][:3])} | Confidence: {entry['confidence']:.0%}",
                inline=False
            )

        await ctx.send(embed=embed)

    @commands.command(name='multimodal-erotic-analysis-agent-stats')
    async def show_stats(self, ctx: commands.Context):
        """
        Show statistics

        Usage: !multimodal-erotic-analysis-agent-stats
        """
        stats = self.agent.db.get_stats()

        embed = discord.Embed(
            title="🔞 Statistics",
            color=discord.Color.purple()
        )
        embed.add_field(name="Total Entries", value=str(stats.get("total", 0)), inline=True)

        by_type = stats.get("by_type", {})
        for content_type, count in by_type.items():
            embed.add_field(name=content_type.capitalize(), value=str(count), inline=True)

        await ctx.send(embed=embed)

def setup(bot: commands.Bot):
    bot.add_cog(MultimodalEroticAnalysisAgentDiscord(bot))
