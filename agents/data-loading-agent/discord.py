#!/usr/bin/env python3
"""
Discord integration for data-loading-agent
"""

import discord
from discord.ext import commands
import sqlite3
import json
from typing import Optional

class DataLoadingBot(commands.Bot):
    """Discord bot for data-loading-agent"""

    def __init__(self, command_prefix: str = "!", db_path: str = "agents/data-loading-agent/data.db"):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix=command_prefix, intents=intents)
        self.db_path = db_path

    async def on_ready(self):
        print(f'Logged in as {self.user}')

    async def create_entry(self, ctx, title: str, content: str):
        """Create entry"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            sql = "INSERT INTO entries (title, content, metadata, status, created_at) VALUES (?, ?, ?, ?, datetime('now'))"
            cursor.execute(sql, (title, content, json.dumps(dict(), ensure_ascii=False), "active"))
            conn.commit()
            await ctx.send(f"Created: {title} (ID: {cursor.lastrowid})")

    async def list_entries(self, ctx, limit: int = 10):
        """List entries"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            sql = "SELECT id, title FROM entries WHERE status = ? ORDER BY created_at DESC LIMIT ?"
            cursor.execute(sql, ("active", limit))
            rows = cursor.fetchall()
            if rows:
                msg = "\n".join([f"{r[0]}: {r[1]}" for r in rows])
                await ctx.send(f"\n{msg}")
            else:
                await ctx.send("No entries found.")

if __name__ == "__main__":
    import os
    bot = DataLoadingBot()
    token = os.getenv("DISCORD_TOKEN")
    if token:
        bot.run(token)
