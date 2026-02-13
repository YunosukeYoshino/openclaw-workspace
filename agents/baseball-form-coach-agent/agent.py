#!/usr/bin/env python3
"""
野球フォームコーチエージェント
Baseball Form Coach Agent
"""

import discord
from discord.ext import commands
from db import init_db

class BaseballFormCoachAgent(commands.Bot):
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
        await ctx.send(f"✅ 野球フォームコーチエージェント is online")

    @commands.command(name='help')
    async def help(self, ctx):
        """ヘルプを表示 / Show help"""
        response = f"📖 **野球フォームコーチエージェント**\n\n"
        response += "**Features / 機能:**\n"
        response += "• フォーム分析 / Form analysis\\n"
        response += "• 改善提案 / Improvement recommendations\\n"
        response += "• ビデオフィードバック / Video feedback\\n"
        response += "• 進捗追跡 / Progress tracking\\n"
        response += "• コーチングチャット / Coaching chat\\n"
        await ctx.send(response)

if __name__ == '__main__':
    bot = BaseballFormCoachAgent()
    import os
    token = os.getenv('DISCORD_BOT_TOKEN')
    bot.run(token)
