#!/usr/bin/env python3
import discord
from discord.ext import commands
import sqlite3

class BaseballAdvancedBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)

    async def on_ready(self):
        print(f'{self.user.name} ready!')

def main():
    import os
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        print("DISCORD_TOKEN not set")
        return
    bot = BaseballAdvancedBot()
    bot.run(token)

if __name__ == "__main__":
    main()
