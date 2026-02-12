#!/usr/bin/env python3
"""
vtuber-ranking-agent Discord Bot
Discord bot interface for vtuber-ranking-agent
"""

import discord
from discord.ext import commands
from typing import Optional
import os

class VtuberRankingAgentBot(commands.Bot):
    """Discord Bot for vtuber-ranking-agent"""

    def __init__(self, command_prefix: str = "!"):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix=command_prefix, intents=intents)
        self.agent_name = "vtuber-ranking-agent"

    async def on_ready(self):
        """Bot起動時の処理"""
        print(f'{{self.user.name}} has connected to Discord!')

    async def on_message(self, message: discord.Message):
        """メッセージ受信時の処理"""
        if message.author == self.user:
            return

        await self.process_commands(message)

    @commands.command()
    async def info(self, ctx):
        """エージェント情報を表示する"""
        embed = discord.Embed(
            title=f"{{self.agent_name}}",
            description="VTuber Management Agent",
            color=discord.Color.purple()
        )
        embed.add_field(name="Description", value="VTuber tracking and management", inline=False)
        embed.add_field(name="Commands", value="`!add`, `!list`, `!search`, `!upcoming`", inline=False)
        await ctx.send(embed=embed)

    @commands.command()
    async def add(self, ctx, name: str, *, description: str = ""):
        """VTuberを追加する"""
        await ctx.send(f"Adding VTuber: {{name}}")
        # データベースに追加する処理をここに実装

    @commands.command()
    async def list(self, ctx):
        """VTuberリストを表示する"""
        await ctx.send("Listing VTubers")
        # データベースから取得する処理をここに実装

    @commands.command()
    async def search(self, ctx, *, query: str):
        """VTuberを検索する"""
        await ctx.send(f"Searching for: {{query}}")
        # 検索処理をここに実装

    @commands.command()
    async def upcoming(self, ctx, days: int = 7):
        """近日の配信を表示する"""
        await ctx.send(f"Upcoming streams in next {{days}} days")
        # 近日の配信を表示する処理をここに実装

def main():
    """Botを起動する"""
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        print("DISCORD_TOKEN environment variable is required")
        return

    bot = VtuberRankingAgentBot()
    bot.run(token)

if __name__ == "__main__":
    main()
