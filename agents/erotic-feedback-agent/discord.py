#!/usr/bin/env python3
"""
えっちコンテンツフィードバックエージェント Discord Bot
Erotic Content Feedback Agent Discord Bot

An agent for managing erotic content feedback, ratings, and improvement suggestions
"""

import discord
from discord.ext import commands
import sqlite3
from typing import Optional

class EroticFeedbackAgentBot(commands.Bot):
    """えっちコンテンツフィードバックエージェント Discord Bot"""

    def __init__(self, command_prefix: str = "!", db_path: str = "erotic_feedback_agent.db"):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix=command_prefix, intents=intents)
        self.db_path = db_path

    async def on_ready(self):
        print(f'{self.user} has connected to Discord!')

    @commands.command()
    async def add_feedback(self, ctx, name: str, *, data: str):
        """Add Feedback"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(f"INSERT INTO feedback (name, data) VALUES (?, ?)", (name, data))
        conn.commit()
        conn.close()
        await ctx.send(f"Added feedback!")

    @commands.command()
    async def list_feedbacks(self, ctx, limit: int = 10):
        """List All Feedback"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM feedback LIMIT ?", (limit,))
        results = cursor.fetchall()
        conn.close()
        if results:
            response = "\n".join([str(r) for r in results])
            await ctx.send(f"**Feedback List:**\n{response}")
        else:
            await ctx.send("No items found.")

    @commands.command()
    async def add_review(self, ctx, name: str, *, data: str):
        """Add Review"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(f"INSERT INTO reviews (name, data) VALUES (?, ?)", (name, data))
        conn.commit()
        conn.close()
        await ctx.send(f"Added review!")

    @commands.command()
    async def list_reviewss(self, ctx, limit: int = 10):
        """List All Reviews"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM reviews LIMIT ?", (limit,))
        results = cursor.fetchall()
        conn.close()
        if results:
            response = "\n".join([str(r) for r in results])
            await ctx.send(f"**Reviews List:**\n{response}")
        else:
            await ctx.send("No items found.")

