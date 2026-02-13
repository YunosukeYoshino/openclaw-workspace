#!/usr/bin/env python3
"""
野球歴史データベース管理エージェント。過去の試合記録、選手成績をデータベース化。

野球歴史データベース管理エージェント。過去の試合記録、選手成績をデータベース化。
"""

import asyncio
import discord
from discord.ext import commands

class BaseballHistoricalDbAgentBot(commands.Bot):
    """baseball-historical-db-agent Bot"""

    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        """Bot起動時の処理"""
        print(f"{self.__class__.__name__} is ready!")

    async def on_ready(self):
        """Bot準備完了時の処理"""
        print(f"Logged in as {self.user}")

def main():
    """メイン関数"""
    bot = BaseballHistoricalDbAgentBot()
    # bot.run("YOUR_DISCORD_BOT_TOKEN")

if __name__ == "__main__":
    main()
