#!/usr/bin/env python3
"""
野球メディア放送エージェント
メディア放送の管理
"""

import discord
from discord.ext import commands
import sqlite3
from datetime import datetime
import json

class BaseballMediaBroadcastAgent(commands.Bot):
    def __init__(self, token):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)
        self.token = token
        self.db_path = "baseball-media-broadcast-agent.db"
        self.init_db()
    
    def init_db(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS records (id INTEGER PRIMARY KEY AUTOINCREMENT, content TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
        conn.commit()
        conn.close()
    
    async def on_ready(self):
        print(f"{{self.user}} has connected to Discord!")
    
    async def on_message(self, message):
        if message.author == self.user:
            return
        await self.process_commands(message)
    
    def run_bot(self):
        self.run(self.token)

if __name__ == "__main__":
    import os
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        print("DISCORD_TOKEN environment variable is required")
        exit(1)
    bot = BaseballMediaBroadcastAgent(token)
    bot.run_bot()
