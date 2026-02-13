#!/usr/bin/env python3
"""
ゲームDLCエージェント Discord Bot
Game DLC Agent Discord Bot
"""

import discord
from discord.ext import commands
from typing import Optional
from .agent import GameDlcAgentAgent
from .db import GameDlcAgentDB

class GameDlcAgentDiscordBot(commands.Bot):
    "Game DLC Agent Discord Bot"

    def __init__(self, command_prefix: str = "!", db_path: str = "data/game-dlc-agent.db"):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix=command_prefix, intents=intents)
        self.agent = GameDlcAgentAgent(db_path)

    async def setup_hook(self):
        """起動時の処理"""
        print(f"{{self.agent.name}} Bot が起動しました")

    async def on_ready(self):
        """準備完了時の処理"""
        print(f"Logged in as {{self.user}}")

async def main():
    import asyncio
    bot = GameDlcAgentDiscordBot()
    # bot.run("YOUR_TOKEN_HERE")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
