#!/usr/bin/env python3
"""
野球スタジアム検索・情報エージェント
Baseball Stadium Finder and Information Agent
"""

import discord
from discord.ext import commands
from db import init_db

class BaseballStadiumFinderAgent(commands.Bot):
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
        await ctx.send(f"✅ 野球スタジアム検索・情報エージェント is online")

    @commands.command(name='help')
    async def help(self, ctx):
        """ヘルプを表示 / Show help"""
        response = f"📖 **野球スタジアム検索・情報エージェント**\n\n"
        response += "**Features / 機能:**\n"
        response += "• スタジアム検索・フィルタリング機能 / Stadium search and filtering\\n"
        response += "• 座席エリア情報の提供 / Seat area information\\n"
        response += "• アクセス方法・交通手段の提案 / Access and transportation\\n"
        response += "• 周辺施設情報 / Nearby facilities\\n"
        response += "• チケット価格帯の比較 / Ticket price comparison\\n"
        await ctx.send(response)

if __name__ == '__main__':
    bot = BaseballStadiumFinderAgent()
    import os
    token = os.getenv('DISCORD_BOT_TOKEN')
    bot.run(token)
