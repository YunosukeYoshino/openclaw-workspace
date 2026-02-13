#!/usr/bin/env python3
"""
えっちコンテンツパーソナライゼーションエージェント Discord Bot
Erotic Content Personalization Agent Discord Bot

An agent for managing personalized erotic content recommendations and user preferences
"""

import discord
from discord.ext import commands
import sqlite3
from typing import Optional

class EroticPersonalizationAgentBot(commands.Bot):
    """えっちコンテンツパーソナライゼーションエージェント Discord Bot"""

    def __init__(self, command_prefix: str = "!", db_path: str = "erotic_personalization_agent.db"):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix=command_prefix, intents=intents)
        self.db_path = db_path

    async def on_ready(self):
        print(f'{self.user} has connected to Discord!')

    @commands.command()
    async def add_preference(self, ctx, name: str, *, data: str):
        """Add Preference"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(f"INSERT INTO preferences (name, data) VALUES (?, ?)", (name, data))
        conn.commit()
        conn.close()
        await ctx.send(f"Added preference!")

    @commands.command()
    async def list_preferencess(self, ctx, limit: int = 10):
        """List All Preferences"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM preferences LIMIT ?", (limit,))
        results = cursor.fetchall()
        conn.close()
        if results:
            response = "\n".join([str(r) for r in results])
            await ctx.send(f"**Preferences List:**\n{response}")
        else:
            await ctx.send("No items found.")

    @commands.command()
    async def add_recommendation(self, ctx, name: str, *, data: str):
        """Add Recommendation"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(f"INSERT INTO recommendations (name, data) VALUES (?, ?)", (name, data))
        conn.commit()
        conn.close()
        await ctx.send(f"Added recommendation!")

    @commands.command()
    async def list_recommendationss(self, ctx, limit: int = 10):
        """List All Recommendations"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM recommendations LIMIT ?", (limit,))
        results = cursor.fetchall()
        conn.close()
        if results:
            response = "\n".join([str(r) for r in results])
            await ctx.send(f"**Recommendations List:**\n{response}")
        else:
            await ctx.send("No items found.")

