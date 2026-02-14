#!/usr/bin/env python3
"""
Discord Bot for ml-experiment-tracker-agent
"""

import discord
from discord.ext import commands
import os

class DiscordBot(commands.Bot):
    def __init__(self, token: str, db_manager):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)
        self.token = token
        self.db = db_manager
    
    async def on_ready(self):
        print(f"Bot logged in as {self.user}")
    
    async def on_message(self, message):
        if message.author == self.user:
            return
        await self.process_commands(message)
    
    @commands.command()
    async def hello(self, ctx):
        await ctx.send("Hello! I am ML実験トラッカーエージェント")
    
    @commands.command()
    async def add(self, ctx, *, content: str):
        record_id = self.db.add_record(content)
        await ctx.send(f"Added record #{record_id}")
    
    @commands.command()
    async def list(self, ctx, limit: int = 10):
        records = self.db.list_records(limit)
        if records:
            response = "Recent records:\n" + "\n".join(f"#{r['id']}: {r['content'][:50]}..." for r in records[:5])
            await ctx.send(response)
        else:
            await ctx.send("No records found")

if __name__ == "__main__":
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from db import DatabaseManager
    
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        print("DISCORD_TOKEN is required")
        exit(1)
    
    db = DatabaseManager()
    bot = DiscordBot(token, db)
    bot.run(token)
