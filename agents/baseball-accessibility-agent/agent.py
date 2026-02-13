#!/usr/bin/env python3
"""
野球スタジアムアクセシビリティエージェント
Baseball Stadium Accessibility Agent
"""

import discord
from discord.ext import commands
from db import init_db

class BaseballAccessibilityAgent(commands.Bot):
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
        await ctx.send(f"✅ 野球スタジアムアクセシビリティエージェント is online")

    @commands.command(name='help')
    async def help(self, ctx):
        """ヘルプを表示 / Show help"""
        response = f"📖 **野球スタジアムアクセシビリティエージェント**\n\n"
        response += "**Features / 機能:**\n"
        response += "• 車いす対応席の情報 / Wheelchair accessible seating\\n"
        response += "• バリアフリー施設の案内 / Barrier-free facility guidance\\n"
        response += "• サポートサービスの予約 / Support service booking\\n"
        response += "• 視覚・聴覚障害者支援 / Visual/hearing impairment support\\n"
        response += "• 多言語対応サービス / Multi-language services\\n"
        await ctx.send(response)

if __name__ == '__main__':
    bot = BaseballAccessibilityAgent()
    import os
    token = os.getenv('DISCORD_BOT_TOKEN')
    bot.run(token)
