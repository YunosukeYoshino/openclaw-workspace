#!/usr/bin/env python3
"""
野球スキル評価エージェント
Baseball Skill Assessment Agent
"""

import discord
from discord.ext import commands
from db import init_db

class BaseballSkillAssessmentAgent(commands.Bot):
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
        await ctx.send(f"✅ 野球スキル評価エージェント is online")

    @commands.command(name='help')
    async def help(self, ctx):
        """ヘルプを表示 / Show help"""
        response = f"📖 **野球スキル評価エージェント**\n\n"
        response += "**Features / 機能:**\n"
        response += "• スキル評価テスト / Skill assessment tests\\n"
        response += "• 成長記録 / Growth records\\n"
        response += "• 比較分析 / Comparative analysis\\n"
        response += "• レーダーチャート表示 / Radar chart visualization\\n"
        response += "• 評価レポート / Assessment reports\\n"
        await ctx.send(response)

if __name__ == '__main__':
    bot = BaseballSkillAssessmentAgent()
    import os
    token = os.getenv('DISCORD_BOT_TOKEN')
    bot.run(token)
