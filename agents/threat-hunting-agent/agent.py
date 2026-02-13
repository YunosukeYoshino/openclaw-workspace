#!/usr/bin/env python3
"""
脅威ハンティングエージェント。脅威の捜索。

脅威ハンティングエージェント。脅威の捜索。
"""

import asyncio
import discord
from discord.ext import commands

class ThreatHuntingAgentBot(commands.Bot):
    """threat-hunting-agent Bot"""

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
    bot = ThreatHuntingAgentBot()
    # bot.run("YOUR_DISCORD_BOT_TOKEN")

if __name__ == "__main__":
    main()
