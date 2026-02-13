#!/usr/bin/env python3
"""
ゲーム予算管理エージェント
Game Budget Manager Agent
"""

import discord
from discord.ext import commands
from db import init_db

class GameBudgetManagerAgent(commands.Bot):
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
        await ctx.send(f"✅ ゲーム予算管理エージェント is online")

    @commands.command(name='help')
    async def help(self, ctx):
        """ヘルプを表示 / Show help"""
        response = f"📖 **ゲーム予算管理エージェント**\n\n"
        response += "**Features / 機能:**\n"
        response += "• 予算設定 / Budget setting\\n"
        response += "• 支出アラート / Spending alerts\\n"
        response += "• 予算進捗表示 / Budget progress display\\n"
        response += "• 予算超過警告 / Over-budget warnings\\n"
        response += "• 節約提案 / Saving suggestions\\n"
        await ctx.send(response)

if __name__ == '__main__':
    bot = GameBudgetManagerAgent()
    import os
    token = os.getenv('DISCORD_BOT_TOKEN')
    bot.run(token)
