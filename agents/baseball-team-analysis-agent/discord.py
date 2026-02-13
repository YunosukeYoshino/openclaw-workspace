#!/usr/bin/env python3
"""
野球チーム戦力分析エージェント Discord Bot
Baseball Team Analysis Agent Discord Bot
"""

import discord
from discord.ext import commands
from typing import Optional
from .agent import BaseballTeamAnalysisAgentAgent
from .db import BaseballTeamAnalysisAgentDB

class BaseballTeamAnalysisAgentDiscordBot(commands.Bot):
    "Baseball Team Analysis Agent Discord Bot"

    def __init__(self, command_prefix: str = "!", db_path: str = "data/baseball-team-analysis-agent.db"):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix=command_prefix, intents=intents)
        self.agent = BaseballTeamAnalysisAgentAgent(db_path)

    async def setup_hook(self):
        """起動時の処理"""
        print(f"{{self.agent.name}} Bot が起動しました")

    async def on_ready(self):
        """準備完了時の処理"""
        print(f"Logged in as {{self.user}}")

async def main():
    import asyncio
    bot = BaseballTeamAnalysisAgentDiscordBot()
    # bot.run("YOUR_TOKEN_HERE")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
