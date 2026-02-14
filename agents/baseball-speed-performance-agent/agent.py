"""野球走力パフォーマンス分析エージェント。走塁・盗塁データの分析"""

import discord
from db import AgentDatabase

class BaseballSpeedPerformanceAgent(discord.Client):
    """野球走力パフォーマンス分析エージェント。走塁・盗塁データの分析"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db = AgentDatabase(f"baseball-speed-performance-agent.db")

    async def on_ready(self):
        print(f"{self.user} is ready!")

    async def on_message(self, message):
        if message.author == self.user:
            return

        # コマンド処理
        if message.content.startswith("!"):
            await self.handle_command(message)

    async def handle_command(self, message):
        """コマンドを処理する"""
        command = message.content[1:].split()[0]

        if command == "help":
            await self.show_help(message)
        elif command == "status":
            await self.show_status(message)
        elif command == "list":
            await self.list_items(message)
        else:
            await message.channel.send(f"Unknown command: {command}")

    async def show_help(self, message):
        """ヘルプを表示"""
        help_text = f"""
        baseball-speed-performance-agent - 野球走力パフォーマンス分析エージェント。走塁・盗塁データの分析

        Commands:
        !help - Show this help
        !status - Show status
        !list - List items
        """
        await message.channel.send(help_text)

    async def show_status(self, message):
        """ステータスを表示"""
        status = self.db.get_status()
        await message.channel.send(f"Status: {status}")

    async def list_items(self, message):
        """アイテム一覧を表示"""
        items = self.db.list_items()
        await message.channel.send(f"Items: {items}")
