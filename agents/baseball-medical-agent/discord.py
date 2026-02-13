#!/usr/bin/env python3
"""
野球メディカルエージェント Discord Bot Module
Baseball Medical Agent Discord Bot

An agent for managing player injuries, recovery predictions, and medical data
"""

import discord
from discord.ext import commands
from typing import Optional, List
import json


class BaseballMedicalAgentBot(commands.Bot):
    """野球メディカルエージェント Discord Bot"""

    def __init__(self, db_path: str = "baseball-medical-agent.db", command_prefix: str = "!"):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix=command_prefix, intents=intents)

        self.db_path = db_path

    async def on_ready(self):
        """Bot起動時"""
        print(f'Logged in as {self.user}')

    @commands.command(name='medicalagentadd')
    async def add_entry(self, ctx, title: str, *, description: str = ""):
        """新しいエントリーを追加"""
        from baseball-medical-agent import BaseballMedicalAgent
        agent = BaseballMedicalAgent(self.db_path)
        entry_id = agent.add_entry(title, description)
        await ctx.send(f"Added entry with ID: {entry_id}")

    @commands.command(name='medicalagentlist')
    async def list_entries(self, ctx, limit: int = 10):
        """エントリー一覧を表示"""
        from baseball-medical-agent import BaseballMedicalAgent
        agent = BaseballMedicalAgent(self.db_path)
        entries = agent.list_entries(limit)

        if not entries:
            await ctx.send("No entries found.")
            return

        embed = discord.Embed(
            title="野球メディカルエージェント Entries",
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

    @commands.command(name='medicalagentget')
    async def get_entry(self, ctx, entry_id: int):
        """エントリーの詳細を表示"""
        from baseball-medical-agent import BaseballMedicalAgent
        agent = BaseballMedicalAgent(self.db_path)
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

    @commands.command(name='medicalagentsearch')
    async def search_entries(self, ctx, *, query: str):
        """エントリーを検索"""
        from baseball-medical-agent import BaseballMedicalAgent
        agent = BaseballMedicalAgent(self.db_path)
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

    @commands.command(name='medicalagentstats')
    async def get_stats(self, ctx):
        """統計情報を表示"""
        from baseball-medical-agent import BaseballMedicalAgent
        agent = BaseballMedicalAgent(self.db_path)
        stats = agent.get_stats()

        embed = discord.Embed(
            title="野球メディカルエージェント Statistics",
            color=discord.Color.gold()
        )
        embed.add_field(name="Total Entries", value=stats['total_entries'])
        embed.add_field(name="Active Entries", value=stats['active_entries'])
        embed.add_field(name="Total Items", value=stats['total_items'])

        await ctx.send(embed=embed)

    @commands.command(name='medicalagenthelp')
    async def show_help(self, ctx):
        """ヘルプを表示"""
        embed = discord.Embed(
            title="野球メディカルエージェント Commands",
            description="Available commands:",
            color=discord.Color.blue()
        )
        embed.add_field(name="!medicalagentadd <title> [description]", value="Add a new entry", inline=False)
        embed.add_field(name="!medicalagentlist [limit]", value="List entries", inline=False)
        embed.add_field(name="!medicalagentget <id>", value="Get entry details", inline=False)
        embed.add_field(name="!medicalagentsearch <query>", value="Search entries", inline=False)
        embed.add_field(name="!medicalagentstats", value="Show statistics", inline=False)
        embed.add_field(name="!medicalagenthelp", value="Show this help", inline=False)

        await ctx.send(embed=embed)


def main():
    """メイン関数"""
    import os
    token = os.environ.get("DISCORD_TOKEN")
    if not token:
        print("DISCORD_TOKEN environment variable not set")
        return

    bot = BaseballMedicalAgentBot()
    bot.run(token)


if __name__ == "__main__":
    main()
