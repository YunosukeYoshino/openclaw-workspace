#!/usr/bin/env python3
"""
野球スタジアムフード・ドリンクエージェント
Baseball Stadium Food and Beverage Agent
"""

import discord
from discord.ext import commands
from db import init_db

class BaseballFoodBeverageAgent(commands.Bot):
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
        await ctx.send(f"✅ 野球スタジアムフード・ドリンクエージェント is online")

    @commands.command(name='help')
    async def help(self, ctx):
        """ヘルプを表示 / Show help"""
        response = f"📖 **野球スタジアムフード・ドリンクエージェント**\n\n"
        response += "**Features / 機能:**\n"
        response += "• スタジアムフードメニューのカタログ / Food menu catalog\\n"
        response += "• 待ち時間の予測・監視 / Wait time prediction\\n"
        response += "• 事前注文機能の統合 / Pre-order integration\\n"
        response += "• 人気メニューのランキング / Popular menu rankings\\n"
        response += "• 食事タイミングの提案 / Meal timing recommendations\\n"
        await ctx.send(response)

if __name__ == '__main__':
    bot = BaseballFoodBeverageAgent()
    import os
    token = os.getenv('DISCORD_BOT_TOKEN')
    bot.run(token)
