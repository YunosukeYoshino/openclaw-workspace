#!/usr/bin/env python3
"""
野球ライブハイライトエージェント

Creates and manages highlights from live baseball games
"""

import os
import json
import discord
from discord.ext import commands
from pathlib import Path
from datetime import datetime

class Baseball_Live_Highlights_Agent(commands.Bot):
    """野球ライブハイライトエージェント"""

    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(
            command_prefix="!",
            intents=intents,
            help_command=None
        )
        self.data_dir = Path(__file__).parent / "data"
        self.data_dir.mkdir(exist_ok=True)
        self.config_file = self.data_dir / "config.json"
        self.load_config()

    def load_config(self):
        """設定を読み込む"""
        if self.config_file.exists():
            with open(self.config_file, "r") as f:
                self.config = json.load(f)
        else:
            self.config = {
                "prefix": "!",
                "language": "ja",
                "notifications": True,
                "channels": []
            }
            self.save_config()

    def save_config(self):
        """設定を保存する"""
        with open(self.config_file, "w") as f:
            json.dump(self.config, f, indent=2)

    async def setup_hook(self):
        """Botの準備完了時"""
        print(f"✅ {野球ライブハイライトエージェント} の準備完了")

    async def on_ready(self):
        """Botが起動したとき"""
        print(f"🚀 {野球ライブハイライトエージェント} が起動しました！")
        activity = discord.Activity(
            type=discord.ActivityType.watching,
            name="baseball highlights"
        )
        await self.change_presence(activity=activity)

    async def on_message(self, message):
        """メッセージを受信したとき"""
        if message.author.bot:
            return
        await self.process_commands(message)

def main():
    """メイン関数"""
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        print("❌ DISCORD_TOKEN 環境変数が設定されていません")
        return

    bot = Baseball_Live_Highlights_Agent()
    bot.run(token)

if __name__ == "__main__":
    main()
