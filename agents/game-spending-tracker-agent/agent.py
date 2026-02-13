#!/usr/bin/env python3
"""
ゲーム支出トラッカーエージェント
Game Spending Tracker Agent
"""

import discord
from discord.ext import commands
from db import init_db

class GameSpendingTrackerAgent(commands.Bot):
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
        await ctx.send(f"✅ ゲーム支出トラッカーエージェント is online")

    @commands.command(name='help')
    async def help(self, ctx):
        """ヘルプを表示 / Show help"""
        response = f"📖 **ゲーム支出トラッカーエージェント**\n\n"
        response += "**Features / 機能:**\n"
        response += "• 支出追跡 / Expense tracking\\n"
        response += "• 購入履歴 / Purchase history\\n"
        response += "• カテゴリ別分析 / Category-based analysis\\n"
        response += "• 月次レポート / Monthly reports\\n"
        response += "• 支出予測 / Expense forecasting\\n"
        await ctx.send(response)

if __name__ == '__main__':
    bot = GameSpendingTrackerAgent()
    import os
    token = os.getenv('DISCORD_BOT_TOKEN')
    bot.run(token)
