#!/usr/bin/env python3
"""
えっちコンテンツソーシャルエージェント Discord Bot
Erotic Content Social Agent Discord Bot

An agent for managing erotic content social sharing, likes, and comments
"""

import discord
from discord.ext import commands
import sqlite3
from typing import Optional

class EroticSocialAgentBot(commands.Bot):
    """えっちコンテンツソーシャルエージェント Discord Bot"""

    def __init__(self, command_prefix: str = "!", db_path: str = "erotic_social_agent.db"):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix=command_prefix, intents=intents)
        self.db_path = db_path

    async def on_ready(self):
        print(f'{self.user} has connected to Discord!')

    @commands.command()
    async def add_post(self, ctx, name: str, *, data: str):
        """Add Post"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(f"INSERT INTO posts (name, data) VALUES (?, ?)", (name, data))
        conn.commit()
        conn.close()
        await ctx.send(f"Added post!")

    @commands.command()
    async def list_postss(self, ctx, limit: int = 10):
        """List All Posts"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM posts LIMIT ?", (limit,))
        results = cursor.fetchall()
        conn.close()
        if results:
            response = "\n".join([str(r) for r in results])
            await ctx.send(f"**Posts List:**\n{response}")
        else:
            await ctx.send("No items found.")

    @commands.command()
    async def add_interaction(self, ctx, name: str, *, data: str):
        """Add Interaction"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(f"INSERT INTO interactions (name, data) VALUES (?, ?)", (name, data))
        conn.commit()
        conn.close()
        await ctx.send(f"Added interaction!")

    @commands.command()
    async def list_interactionss(self, ctx, limit: int = 10):
        """List All Interactions"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM interactions LIMIT ?", (limit,))
        results = cursor.fetchall()
        conn.close()
        if results:
            response = "\n".join([str(r) for r in results])
            await ctx.send(f"**Interactions List:**\n{response}")
        else:
            await ctx.send("No items found.")

