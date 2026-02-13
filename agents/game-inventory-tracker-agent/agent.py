#!/usr/bin/env python3
"""
ゲーム在庫トラッカーエージェント
Game Inventory Tracker Agent
"""

import discord
from discord.ext import commands
from db import init_db

class GameInventoryTrackerAgent(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix='!', intents=intents)
        init_db()

    async def setup_hook(self):
        await self.add_command(self.status)
        await self.add_command(self.help)

    @commands.command(name='status')
    async def status(self, ctx):
        """ステータスを表示 / Show status"""
        await ctx.send(f"✅ ゲーム在庫トラッカーエージェント is online")

    @commands.command(name='help')
    async def help(self, ctx):
        """ヘルプを表示 / Show help"""
        response = f"📖 **ゲーム在庫トラッカーエージェント**\n\n"
        response += "**Features / 機能:**\n"
        response += "• 在庫管理 / Inventory management\\n"
        response += "• アイテム価値追跡 / Item value tracking\\n"
        response += "• 通貨残高管理 / Currency balance management\\n"
        response += "• アイテム履歴 / Item history\\n"
        response += "• 価値変動分析 / Value fluctuation analysis\\n"
        await ctx.send(response)

if __name__ == '__main__':
    bot = GameInventoryTrackerAgent()
    import os
    token = os.getenv('DISCORD_BOT_TOKEN')
    bot.run(token)
