#!/usr/bin/env python3
"""
えっちコンテンツキュレーションエージェント Discord Bot
Erotic Content Curation Agent Discord Bot

An agent for managing erotic content curation, collections, and recommended lists
"""

import discord
from discord.ext import commands
import sqlite3
from typing import Optional

class EroticCurationAgentBot(commands.Bot):
    """えっちコンテンツキュレーションエージェント Discord Bot"""

    def __init__(self, command_prefix: str = "!", db_path: str = "erotic_curation_agent.db"):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix=command_prefix, intents=intents)
        self.db_path = db_path

    async def on_ready(self):
        print(f'{self.user} has connected to Discord!')

    @commands.command()
    async def add_collection(self, ctx, name: str, *, data: str):
        """Add Collection"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(f"INSERT INTO collections (name, data) VALUES (?, ?)", (name, data))
        conn.commit()
        conn.close()
        await ctx.send(f"Added collection!")

    @commands.command()
    async def list_collectionss(self, ctx, limit: int = 10):
        """List All Collections"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM collections LIMIT ?", (limit,))
        results = cursor.fetchall()
        conn.close()
        if results:
            response = "\n".join([str(r) for r in results])
            await ctx.send(f"**Collections List:**\n{response}")
        else:
            await ctx.send("No items found.")

    @commands.command()
    async def add_item(self, ctx, name: str, *, data: str):
        """Add Item"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(f"INSERT INTO items (name, data) VALUES (?, ?)", (name, data))
        conn.commit()
        conn.close()
        await ctx.send(f"Added item!")

    @commands.command()
    async def list_itemss(self, ctx, limit: int = 10):
        """List All Items"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM items LIMIT ?", (limit,))
        results = cursor.fetchall()
        conn.close()
        if results:
            response = "\n".join([str(r) for r in results])
            await ctx.send(f"**Items List:**\n{response}")
        else:
            await ctx.send("No items found.")

