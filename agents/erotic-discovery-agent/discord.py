#!/usr/bin/env python3
"""
えっちコンテンツディスカバリーエージェント Discord Bot
Erotic Content Discovery Agent Discord Bot

An agent for managing erotic content discovery, trends, and new content
"""

import discord
from discord.ext import commands
import sqlite3
from typing import Optional

class EroticDiscoveryAgentBot(commands.Bot):
    """えっちコンテンツディスカバリーエージェント Discord Bot"""

    def __init__(self, command_prefix: str = "!", db_path: str = "erotic_discovery_agent.db"):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix=command_prefix, intents=intents)
        self.db_path = db_path

    async def on_ready(self):
        print(f'{self.user} has connected to Discord!')

    @commands.command()
    async def add_trend(self, ctx, name: str, *, data: str):
        """Add Trend"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(f"INSERT INTO trends (name, data) VALUES (?, ?)", (name, data))
        conn.commit()
        conn.close()
        await ctx.send(f"Added trend!")

    @commands.command()
    async def list_trendss(self, ctx, limit: int = 10):
        """List All Trends"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM trends LIMIT ?", (limit,))
        results = cursor.fetchall()
        conn.close()
        if results:
            response = "\n".join([str(r) for r in results])
            await ctx.send(f"**Trends List:**\n{response}")
        else:
            await ctx.send("No items found.")

    @commands.command()
    async def add_new_content(self, ctx, name: str, *, data: str):
        """Add New_content"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(f"INSERT INTO new_content (name, data) VALUES (?, ?)", (name, data))
        conn.commit()
        conn.close()
        await ctx.send(f"Added new_content!")

    @commands.command()
    async def list_new_contents(self, ctx, limit: int = 10):
        """List All New_content"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM new_content LIMIT ?", (limit,))
        results = cursor.fetchall()
        conn.close()
        if results:
            response = "\n".join([str(r) for r in results])
            await ctx.send(f"**New_content List:**\n{response}")
        else:
            await ctx.send("No items found.")

