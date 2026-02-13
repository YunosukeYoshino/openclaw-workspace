#!/usr/bin/env python3
"""
野球ファン体験エージェント
Baseball Fan Experience Agent
"""

import discord
from discord.ext import commands
from db import init_db

class BaseballFanExperienceAgent(commands.Bot):
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
        await ctx.send(f"✅ 野球ファン体験エージェント is online")

    @commands.command(name='help')
    async def help(self, ctx):
        """ヘルプを表示 / Show help"""
        response = f"📖 **野球ファン体験エージェント**\n\n"
        response += "**Features / 機能:**\n"
        response += "• ファン体験イベントの案内 / Fan experience events\\n"
        response += "• 記念品・グッズ情報の収集 / Merchandise information\\n"
        response += "• スタジアムクイズ・ゲーム / Stadium quizzes and games\\n"
        response += "• AR/VR体験機能 / AR/VR experience features\\n"
        response += "• ファン参加型コンテンツ / Fan participation content\\n"
        await ctx.send(response)

if __name__ == '__main__':
    bot = BaseballFanExperienceAgent()
    import os
    token = os.getenv('DISCORD_BOT_TOKEN')
    bot.run(token)
