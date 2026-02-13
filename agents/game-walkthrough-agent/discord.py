#!/usr/bin/env python3
"""
ゲーム攻略・Walkthroughエージェント - Discord Bot モジュール
"""

import discord
from discord.ext import commands
from typing import Optional


class GameWalkthroughAgentBot(commands.Bot):
    """ゲーム攻略・Walkthroughエージェント Discord Bot"""

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
                name="game info"
            )
        )


bot = GameWalkthroughAgentBot()


@bot.command(name="search")
async def search_info(ctx, query: str):
    """情報を検索"""
    # TODO: データベースから情報を検索して表示
    await ctx.send(f"Searching for: {query}")


@bot.command(name="add")
async def add_info(ctx, game_id: str, *args):
    """情報を追加"""
    # TODO: データベースに情報を追加
    await ctx.send(f"Adding info for game: {game_id}")


@bot.command(name="list")
async def list_info(ctx, game_title: Optional[str] = None):
    """情報を一覧表示"""
    # TODO: データベースから情報を一覧表示
    if game_title:
        await ctx.send(f"Listing info for: {game_title}")
    else:
        await ctx.send("Usage: !list <game_title>")


@bot.command(name="update")
async def update_info(ctx, entry_id: int, *args):
    """情報を更新"""
    # TODO: データベースの情報を更新
    await ctx.send(f"Updating info ID: {entry_id}")


@bot.command(name="delete")
async def delete_info(ctx, entry_id: int):
    """情報を削除"""
    # TODO: データベースの情報を削除
    await ctx.send(f"Deleting info ID: {entry_id}")


@bot.command(name="help")
async def show_help(ctx):
    """ヘルプを表示"""
    help_text = """
**ゲーム攻略・Walkthroughエージェント Commands:**

`!search <query>` - 情報を検索
`!add <game_id> [data...]` - 情報を追加
`!list <game_title>` - 情報を一覧表示
`!update <entry_id> [data...]` - 情報を更新
`!delete <entry_id>` - 情報を削除
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
