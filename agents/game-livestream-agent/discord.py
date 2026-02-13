#!/usr/bin/env python3
"""
ゲームライブ配信エージェント Discord Bot Module
Game Livestream Agent Discord Bot

An agent for managing game livestream info, schedules, and popular streamers
"""

import discord
from discord.ext import commands
from typing import Optional, List
import json


class GameLivestreamAgentBot(commands.Bot):
    """ゲームライブ配信エージェント Discord Bot"""

    def __init__(self, db_path: str = "game-livestream-agent.db", command_prefix: str = "!"):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix=command_prefix, intents=intents)

        self.db_path = db_path

    async def on_ready(self):
        """Bot起動時"""
        print(f'Logged in as {self.user}')

    @commands.command(name='livestreamagentadd')
    async def add_entry(self, ctx, title: str, *, description: str = ""):
        """新しいエントリーを追加"""
        from game-livestream-agent import GameLivestreamAgent
        agent = GameLivestreamAgent(self.db_path)
        entry_id = agent.add_entry(title, description)
        await ctx.send(f"Added entry with ID: {entry_id}")

    @commands.command(name='livestreamagentlist')
    async def list_entries(self, ctx, limit: int = 10):
        """エントリー一覧を表示"""
        from game-livestream-agent import GameLivestreamAgent
        agent = GameLivestreamAgent(self.db_path)
        entries = agent.list_entries(limit)

        if not entries:
            await ctx.send("No entries found.")
            return

        embed = discord.Embed(
            title="ゲームライブ配信エージェント Entries",
            description=f"Showing {len(entries)} entries",
            color=discord.Color.blue()
        )

        for entry in entries:
            embed.add_field(
                name=f"{entry['title']} (ID: {entry['id']})",
                value=entry['description'][:100] or "No description",
                inline=False
            )

        await ctx.send(embed=embed)

    @commands.command(name='livestreamagentget')
    async def get_entry(self, ctx, entry_id: int):
        """エントリーの詳細を表示"""
        from game-livestream-agent import GameLivestreamAgent
        agent = GameLivestreamAgent(self.db_path)
        entry = agent.get_entry(entry_id)

        if not entry:
            await ctx.send(f"Entry with ID {entry_id} not found.")
            return

        embed = discord.Embed(
            title=entry['title'],
            description=entry['description'] or "No description",
            color=discord.Color.green()
        )
        embed.add_field(name="ID", value=entry['id'])
        embed.add_field(name="Status", value=entry['status'])
        embed.add_field(name="Created", value=entry['created_at'])

        await ctx.send(embed=embed)

    @commands.command(name='livestreamagentsearch')
    async def search_entries(self, ctx, *, query: str):
        """エントリーを検索"""
        from game-livestream-agent import GameLivestreamAgent
        agent = GameLivestreamAgent(self.db_path)
        entries = agent.search_entries(query)

        if not entries:
            await ctx.send(f"No entries found for query: {query}")
            return

        embed = discord.Embed(
            title=f"Search Results for: {query}",
            description=f"Found {len(entries)} entries",
            color=discord.Color.purple()
        )

        for entry in entries[:10]:
            embed.add_field(
                name=f"{entry['title']} (ID: {entry['id']})",
                value=entry['description'][:100] or "No description",
                inline=False
            )

        await ctx.send(embed=embed)

    @commands.command(name='livestreamagentstats')
    async def get_stats(self, ctx):
        """統計情報を表示"""
        from game-livestream-agent import GameLivestreamAgent
        agent = GameLivestreamAgent(self.db_path)
        stats = agent.get_stats()

        embed = discord.Embed(
            title="ゲームライブ配信エージェント Statistics",
            color=discord.Color.gold()
        )
        embed.add_field(name="Total Entries", value=stats['total_entries'])
        embed.add_field(name="Active Entries", value=stats['active_entries'])
        embed.add_field(name="Total Items", value=stats['total_items'])

        await ctx.send(embed=embed)

    @commands.command(name='livestreamagenthelp')
    async def show_help(self, ctx):
        """ヘルプを表示"""
        embed = discord.Embed(
            title="ゲームライブ配信エージェント Commands",
            description="Available commands:",
            color=discord.Color.blue()
        )
        embed.add_field(name="!livestreamagentadd <title> [description]", value="Add a new entry", inline=False)
        embed.add_field(name="!livestreamagentlist [limit]", value="List entries", inline=False)
        embed.add_field(name="!livestreamagentget <id>", value="Get entry details", inline=False)
        embed.add_field(name="!livestreamagentsearch <query>", value="Search entries", inline=False)
        embed.add_field(name="!livestreamagentstats", value="Show statistics", inline=False)
        embed.add_field(name="!livestreamagenthelp", value="Show this help", inline=False)

        await ctx.send(embed=embed)


def main():
    """メイン関数"""
    import os
    token = os.environ.get("DISCORD_TOKEN")
    if not token:
        print("DISCORD_TOKEN environment variable not set")
        return

    bot = GameLivestreamAgentBot()
    bot.run(token)


if __name__ == "__main__":
    main()
