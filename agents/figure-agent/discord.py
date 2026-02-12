#!/usr/bin/env python3
"""
figure-agent Discord Bot
Discord bot interface for figure-agent
"""

import discord
from discord.ext import commands
from typing import Optional
import os

class FigureAgentBot(commands.Bot):
    """Discord Bot for figure-agent"""

    def __init__(self, command_prefix: str = "!"):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix=command_prefix, intents=intents)
        self.agent_name = "figure-agent"

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
            description="Creative Content Management Agent",
            color=discord.Color.orange()
        )
        embed.add_field(name="Description", value="Creative content and artwork management", inline=False)
        embed.add_field(name="Commands", value="`!add`, `!list`, `!search`, `!gallery`", inline=False)
        await ctx.send(embed=embed)

    @commands.command()
    async def add(self, ctx, title: str, creator: str, *, url: str = ""):
        """コンテンツを追加する"""
        await ctx.send(f"Adding content: {{title}} by {{creator}}")
        # データベースに追加する処理をここに実装

    @commands.command()
    async def list(self, ctx, creator: Optional[str] = None):
        """コンテンツリストを表示する"""
        if creator:
            await ctx.send(f"Listing content by {{creator}}")
        else:
            await ctx.send("Listing all content")
        # データベースから取得する処理をここに実装

    @commands.command()
    async def search(self, ctx, *, query: str):
        """コンテンツを検索する"""
        await ctx.send(f"Searching for: {{query}}")
        # 検索処理をここに実装

    @commands.command()
    async def gallery(self, ctx):
        """ギャラリーを表示する"""
        await ctx.send("Opening gallery...")
        # ギャラリーを表示する処理をここに実装

def main():
    """Botを起動する"""
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        print("DISCORD_TOKEN environment variable is required")
        return

    bot = FigureAgentBot()
    bot.run(token)

if __name__ == "__main__":
    main()
