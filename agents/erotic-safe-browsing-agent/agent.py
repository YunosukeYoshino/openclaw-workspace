#!/usr/bin/env python3
"""
えっちセーフブラウジングエージェント
Erotic Safe Browsing Agent
"""

import discord
from discord.ext import commands
from db import init_db

class EroticSafeBrowsingAgent(commands.Bot):
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
        await ctx.send(f"✅ えっちセーフブラウジングエージェント is online")

    @commands.command(name='help')
    async def help(self, ctx):
        """ヘルプを表示 / Show help"""
        response = f"📖 **えっちセーフブラウジングエージェント**\n\n"
        response += "**Features / 機能:**\n"
        response += "• 安全なサイト判定 / Safe site detection\\n"
        response += "• 詐欺サイト検出 / Scam site detection\\n"
        response += "• マルウェアスキャン / Malware scanning\\n"
        response += "• フィッシング対策 / Phishing protection\\n"
        response += "• 安全なダウンロード / Safe downloads\\n"
        await ctx.send(response)

if __name__ == '__main__':
    bot = EroticSafeBrowsingAgent()
    import os
    token = os.getenv('DISCORD_BOT_TOKEN')
    bot.run(token)
