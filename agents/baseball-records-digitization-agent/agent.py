#!/usr/bin/env python3
"""
野球記録デジタル化エージェント。紙ベースの記録をデジタル化。

野球記録デジタル化エージェント。紙ベースの記録をデジタル化。
"""

import asyncio
import discord
from discord.ext import commands

class BaseballRecordsDigitizationAgentBot(commands.Bot):
    """baseball-records-digitization-agent Bot"""

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
    bot = BaseballRecordsDigitizationAgentBot()
    # bot.run("YOUR_DISCORD_BOT_TOKEN")

if __name__ == "__main__":
    main()
