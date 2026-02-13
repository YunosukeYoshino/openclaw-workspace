#!/usr/bin/env python3
"""
えっちプライバシーガードエージェント
Erotic Privacy Guard Agent
"""

import discord
from discord.ext import commands
from db import init_db

class EroticPrivacyGuardAgent(commands.Bot):
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
        await ctx.send(f"✅ えっちプライバシーガードエージェント is online")

    @commands.command(name='help')
    async def help(self, ctx):
        """ヘルプを表示 / Show help"""
        response = f"📖 **えっちプライバシーガードエージェント**\n\n"
        response += "**Features / 機能:**\n"
        response += "• 閲覧履歴の暗号化 / Encrypted browsing history\\n"
        response += "• 検索履歴の保護 / Search history protection\\n"
        response += "• 自動削除機能 / Auto-delete functionality\\n"
        response += "• プライベートモード / Private mode\\n"
        response += "• 追跡防止機能 / Tracking prevention\\n"
        await ctx.send(response)

if __name__ == '__main__':
    bot = EroticPrivacyGuardAgent()
    import os
    token = os.getenv('DISCORD_BOT_TOKEN')
    bot.run(token)
