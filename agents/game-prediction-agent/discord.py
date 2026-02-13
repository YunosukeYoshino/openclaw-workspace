#!/usr/bin/env python3
"""
ゲーム進行予測エージェント Discord Bot
Game Progress Prediction Agent Discord Bot
"""

import discord
from discord.ext import commands
from typing import Optional
from .agent import GamePredictionAgentAgent
from .db import GamePredictionAgentDB

class GamePredictionAgentDiscordBot(commands.Bot):
    "Game Progress Prediction Agent Discord Bot"

    def __init__(self, command_prefix: str = "!", db_path: str = "data/game-prediction-agent.db"):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix=command_prefix, intents=intents)
        self.agent = GamePredictionAgentAgent(db_path)

    async def setup_hook(self):
        """起動時の処理"""
        print(f"{{self.agent.name}} Bot が起動しました")

    async def on_ready(self):
        """準備完了時の処理"""
        print(f"Logged in as {{self.user}}")

async def main():
    import asyncio
    bot = GamePredictionAgentDiscordBot()
    # bot.run("YOUR_TOKEN_HERE")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
