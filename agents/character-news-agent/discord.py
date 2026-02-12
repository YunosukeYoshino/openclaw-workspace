#!/usr/bin/env python3
"""
character-news-agent Discord Bot
Discord bot interface for character-news-agent
"""

import discord
from discord.ext import commands
from typing import Optional
import os

class CharacterNewsAgentBot(commands.Bot):
    """Discord Bot for character-news-agent"""

    def __init__(self, command_prefix: str = "!"):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix=command_prefix, intents=intents)
        self.agent_name = "character-news-agent"

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
            description="Anime/Game Character Agent",
            color=discord.Color.blue()
        )
        embed.add_field(name="Description", value="Character tracking and management", inline=False)
        embed.add_field(name="Commands", value="`!add`, `!list`, `!search`, `!stats`", inline=False)
        await ctx.send(embed=embed)

    @commands.command()
    async def add(self, ctx, name: str, source: str, *, description: str = ""):
        """キャラクターを追加する"""
        await ctx.send(f"Adding character: {{name}} from {{source}}")
        # データベースに追加する処理をここに実装

    @commands.command()
    async def list(self, ctx, source: Optional[str] = None):
        """キャラクターリストを表示する"""
        await ctx.send(f"Listing characters{{' from ' + source if source else ''}}")
        # データベースから取得する処理をここに実装

    @commands.command()
    async def search(self, ctx, *, query: str):
        """キャラクターを検索する"""
        await ctx.send(f"Searching for: {{query}}")
        # 検索処理をここに実装

    @commands.command()
    async def stats(self, ctx):
        """統計情報を表示する"""
        await ctx.send("Statistics:")
        # 統計情報を表示する処理をここに実装

def main():
    """Botを起動する"""
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        print("DISCORD_TOKEN environment variable is required")
        return

    bot = CharacterNewsAgentBot()
    bot.run(token)

if __name__ == "__main__":
    main()
