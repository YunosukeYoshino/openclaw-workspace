#!/usr/bin/env python3
"""
野球チケット最適化エージェント
Baseball Ticket Optimizer Agent
"""

import discord
from discord.ext import commands
from db import init_db

class BaseballTicketOptimizerAgent(commands.Bot):
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
        await ctx.send(f"✅ 野球チケット最適化エージェント is online")

    @commands.command(name='help')
    async def help(self, ctx):
        """ヘルプを表示 / Show help"""
        response = f"📖 **野球チケット最適化エージェント**\n\n"
        response += "**Features / 機能:**\n"
        response += "• チケット価格の比較・最適化 / Ticket price comparison\\n"
        response += "• リアルタイム空席監視 / Real-time seat monitoring\\n"
        response += "• 価格変動の予測 / Price prediction\\n"
        response += "• 購入タイミングの提案 / Purchase timing\\n"
        response += "• 割引情報の収集・配信 / Discount information\\n"
        await ctx.send(response)

if __name__ == '__main__':
    bot = BaseballTicketOptimizerAgent()
    import os
    token = os.getenv('DISCORD_BOT_TOKEN')
    bot.run(token)
