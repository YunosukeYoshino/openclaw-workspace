#!/usr/bin/env python3
"""
野球フィットネストラッカーエージェント
Baseball Fitness Tracker Agent
"""

import discord
from discord.ext import commands
from db import init_db

class BaseballFitnessTrackerAgent(commands.Bot):
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
        await ctx.send(f"✅ 野球フィットネストラッカーエージェント is online")

    @commands.command(name='help')
    async def help(self, ctx):
        """ヘルプを表示 / Show help"""
        response = f"📖 **野球フィットネストラッカーエージェント**\n\n"
        response += "**Features / 機能:**\n"
        response += "• フィットネスデータ追跡 / Fitness data tracking\\n"
        response += "• ウェアラブル統合 / Wearable integration\\n"
        response += "• トレーニングログ / Training logs\\n"
        response += "• 目標設定 / Goal setting\\n"
        response += "• 分析・レポート / Analysis and reporting\\n"
        await ctx.send(response)

if __name__ == '__main__':
    bot = BaseballFitnessTrackerAgent()
    import os
    token = os.getenv('DISCORD_BOT_TOKEN')
    bot.run(token)
