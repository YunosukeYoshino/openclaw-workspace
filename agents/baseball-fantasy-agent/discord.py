#!/usr/bin/env python3
"""
ファンタジー野球管理エージェント - Discord Bot モジュール
"""

import discord
from discord.ext import commands
from typing import Optional
import re


class BaseballFantasyAgentBot(commands.Bot):
    """ファンタジー野球管理エージェント Discord Bot"""

    def __init__(self, command_prefix: str = "!"):
        """初期化"""
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix=command_prefix, intents=intents)

    async def setup_hook(self):
        """ボットの準備"""
        print(f"Logged in as {self.user}")

    async def on_ready(self):
        """準備完了時の処理"""
        print(f"{self.__class__.__name__} is ready!")
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="baseball stats"
            )
        )


bot = BaseballFantasyAgentBot()


@bot.command(name="stats")
async def show_stats(ctx, player_name: Optional[str] = None):
    """統計を表示"""
    # TODO: データベースから統計を取得して表示
    if player_name:
        await ctx.send(f"Searching for stats of: {player_name}")
    else:
        await ctx.send("Usage: !stats <player_name>")


@bot.command(name="add")
async def add_stat(ctx, player_id: str, player_name: str, *args):
    """統計を追加"""
    # TODO: データベースに統計を追加
    await ctx.send(f"Adding stat for {player_name} (ID: {player_id})")


@bot.command(name="update")
async def update_stat(ctx, player_id: str, *args):
    """統計を更新"""
    # TODO: データベースの統計を更新
    await ctx.send(f"Updating stat for player ID: {player_id}")


@bot.command(name="search")
async def search_stats(ctx, query: str):
    """統計を検索"""
    # TODO: データベースを検索
    await ctx.send(f"Searching for: {query}")


@bot.command(name="summary")
async def show_summary(ctx):
    """サマリーを表示"""
    # TODO: 統計のサマリーを表示
    await ctx.send("Generating summary...")


@bot.command(name="help")
async def show_help(ctx):
    """ヘルプを表示"""
    help_text = """
**ファンタジー野球管理エージェント Commands:**

`!stats <player_name>` - 選手の統計を表示
`!add <player_id> <player_name> [stats...]` - 統計を追加
`!update <player_id> [stats...]` - 統計を更新
`!search <query>` - 統計を検索
`!summary` - サマリーを表示
`!help` - このヘルプを表示
"""
    await ctx.send(help_text)


def main():
    """メイン関数"""
    import os
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        print("DISCORD_TOKEN environment variable not set")
        return
    bot.run(token)


if __name__ == "__main__":
    main()
