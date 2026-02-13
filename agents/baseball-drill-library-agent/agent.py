#!/usr/bin/env python3
"""
野球ドリルライブラリエージェント
Baseball Drill Library Agent
"""

import discord
from discord.ext import commands
from db import init_db

class BaseballDrillLibraryAgent(commands.Bot):
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
        await ctx.send(f"✅ 野球ドリルライブラリエージェント is online")

    @commands.command(name='help')
    async def help(self, ctx):
        """ヘルプを表示 / Show help"""
        response = f"📖 **野球ドリルライブラリエージェント**\n\n"
        response += "**Features / 機能:**\n"
        response += "• ドリルライブラリ / Drill library\\n"
        response += "• 動画チュートリアル / Video tutorials\\n"
        response += "• 難易度別分類 / Difficulty-based classification\\n"
        response += "• 目的別ドリル検索 / Purpose-based drill search\\n"
        response += "• お気に入り機能 / Favorites\\n"
        await ctx.send(response)

if __name__ == '__main__':
    bot = BaseballDrillLibraryAgent()
    import os
    token = os.getenv('DISCORD_BOT_TOKEN')
    bot.run(token)
