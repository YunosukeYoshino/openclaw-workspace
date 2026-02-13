#!/usr/bin/env python3
"""
Discord Bot module for erotic-recommendation-agent
えっちコンテンツ推薦エージェントのDiscord Botモジュール
"""

import discord
from discord.ext import commands
from typing import Optional
import asyncio

from .agent import EroticRecommendationAgentAgent
from .db import get_db


class DiscordBot(commands.Bot):
    """えっちコンテンツ推薦エージェント Discord Bot"""

    def __init__(self, agent: EroticRecommendationAgentAgent):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(
            command_prefix="!",
            intents=intents,
            help_command=None
        )
        self.agent = agent
        self.db = get_db()

    async def on_ready(self):
        """Bot起動時"""
        print(f"Logged in as {{self.user}} (ID: {{self.user.id}})")
        await self.change_presence(activity=discord.Activity(
            type=discord.ActivityType.watching,
            name="コンテンツ分析"
        ))

    async def on_message(self, message: discord.Message):
        """メッセージ受信時"""
        if message.author.bot:
            return

        await self.process_commands(message)


def create_bot(agent: EroticRecommendationAgentAgent, token: str) -> DiscordBot:
    """Botインスタンスを作成"""
    bot = DiscordBot(agent)

    @bot.command(name="add")
    async def add_entry(ctx, title: str, *, content: str = ""):
        """エントリーを追加"""
        entry_id = agent.add_entry(title, content)
        await ctx.send(f"エントリーを追加しました (ID: {{entry_id}})")

    @bot.command(name="list")
    async def list_entries(ctx, limit: int = 10):
        """エントリー一覧"""
        entries = agent.list_entries(limit=limit)
        if not entries:
            await ctx.send("エントリーがありません")
            return

        embed = discord.Embed(title="えっちコンテンツ推薦エージェント", color=discord.Color.blue())
        for entry in entries:
            embed.add_field(
                name=entry["title"],
                value=f"ID: {{entry['id']}} | {{entry.get('tags', 'N/A')}}",
                inline=False
            )
        await ctx.send(embed=embed)

    @bot.command(name="search")
    async def search_entries(ctx, *, query: str):
        """エントリーを検索"""
        entries = agent.search_entries(query)
        if not entries:
            await ctx.send("該当するエントリーがありません")
            return

        embed = discord.Embed(
            title=f"検索結果: {{query}}",
            color=discord.Color.green()
        )
        for entry in entries[:10]:
            embed.add_field(
                name=entry["title"],
                value=f"ID: {{entry['id']}}",
                inline=False
            )
        await ctx.send(embed=embed)

    @bot.command(name="get")
    async def get_entry(ctx, entry_id: int):
        """エントリー詳細"""
        entry = agent.get_entry(entry_id)
        if not entry:
            await ctx.send(f"エントリー ID {{entry_id}} は見つかりませんでした")
            return

        embed = discord.Embed(
            title=entry["title"],
            description=entry.get("content", "N/A"),
            color=discord.Color.purple()
        )
        embed.add_field(name="ID", value=entry["id"], inline=True)
        embed.add_field(name="Artist", value=entry.get("artist", "N/A"), inline=True)
        embed.add_field(name="Tags", value=entry.get("tags", "N/A"), inline=True)
        await ctx.send(embed=embed)

    @bot.command(name="help")
    async def help_command(ctx):
        """ヘルプ"""
        embed = discord.Embed(
            title="えっちコンテンツ推薦エージェント - ヘルプ",
            color=discord.Color.gold()
        )
        embed.add_field(name="!add <title> [content]", value="エントリーを追加", inline=False)
        embed.add_field(name="!list [limit]", value="エントリー一覧", inline=False)
        embed.add_field(name="!search <query>", value="エントリーを検索", inline=False)
        embed.add_field(name="!get <id>", value="エントリー詳細", inline=False)
        await ctx.send(embed=embed)

    return bot


async def run_bot(agent: EroticRecommendationAgentAgent, token: str):
    """Botを実行"""
    bot = create_bot(agent, token)
    await bot.start(token)


def run_bot_sync(token: str):
    """Botを同期的に実行"""
    agent = EroticRecommendationAgentAgent()
    asyncio.run(run_bot(agent, token))
