#!/usr/bin/env python3
"""
野球プレスリリースエージェント。球団・選手の発表管理。

野球プレスリリースエージェント。球団・選手の発表管理。
"""

import asyncio
import discord
from discord.ext import commands

class BaseballPressReleaseAgentBot(commands.Bot):
    """baseball-press-release-agent Bot"""

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
    bot = BaseballPressReleaseAgentBot()
    # bot.run("YOUR_DISCORD_BOT_TOKEN")

if __name__ == "__main__":
    main()
