#!/usr/bin/env python3
"""
えっちAI動画生成エージェント - Discord Bot Integration
"""

import discord
from discord.ext import commands
from typing import Optional, List, Dict, Any
import json

from db import (
    create_entry,
    get_entry,
    list_entries,
    search_entries,
    update_entry,
    delete_entry,
    add_tag_to_entry,
    remove_tag_from_entry,
    get_all_tags,
    get_entries_by_tag,
    get_stats,
)


class EroticAiVideoGenAgentDiscordBot(commands.Bot):
    """えっちAI動画生成エージェント - Discord Bot"""

    def __init__(self, command_prefix: str = "!", intents: Optional[discord.Intents] = None):
        if intents is None:
            intents = discord.Intents.default()
            intents.message_content = True

        super().__init__(command_prefix=command_prefix, intents=intents)
        self.prefix = command_prefix

    async def setup_hook(self):
        print(f"{self.__class__.__name__} のセットアップ中...")

    async def on_ready(self):
        print(f"{self.user} がログインしました！")
        print(f"サーバー数: {len(self.guilds)}")

    async def on_message(self, message: discord.Message):
        if message.author == self.user:
            return
        await self.process_commands(message)

    @commands.command()
    async def stats(self, ctx: commands.Context):
        stats_data = get_stats()

        embed = discord.Embed(title=f"えっちAI動画生成エージェント 統計情報", color=discord.Color.blue())
        embed.add_field(name="総エントリー数", value=stats_data["total_entries"], inline=True)
        embed.add_field(name="アクティブエントリー", value=stats_data["active_entries"], inline=True)
        embed.add_field(name="総タグ数", value=stats_data["total_tags"], inline=True)

        await ctx.send(embed=embed)

    @commands.command()
    async def list(self, ctx: commands.Context, limit: int = 10):
        entries = list_entries(limit=limit)

        if not entries:
            await ctx.send("エントリーが見つかりませんでした。")
            return

        embed = discord.Embed(title="エントリーリスト (最新" + str(len(entries)) + "件)", color=discord.Color.green())

        for entry in entries[:10]:
            title = entry["title"][:50] + "..." if len(entry["title"]) > 50 else entry["title"]
            status_emoji = "✅" if entry["status"] == "active" else "📦"
            embed.add_field(name=status_emoji + " #" + str(entry["id"]) + " - " + title,
                           value="作成: " + entry["created_at"], inline=False)

        await ctx.send(embed=embed)

    @commands.command()
    async def search(self, ctx: commands.Context, *, query: str):
        if not query:
            await ctx.send("検索キーワードを指定してください。")
            return

        entries = search_entries(query, limit=10)

        if not entries:
            await ctx.send("検索結果が見つかりませんでした。")
            return

        embed = discord.Embed(title="検索結果: " + query, color=discord.Color.orange())

        for entry in entries[:5]:
            content = entry["content"][:200] + "..." if len(entry["content"]) > 200 else entry["content"]
            embed.add_field(name="#" + str(entry["id"]) + " - " + entry["title"], value=content, inline=False)

        await ctx.send(embed=embed)

    @commands.command()
    async def add(self, ctx: commands.Context, title: str, *, content: str = ""):
        if not title:
            await ctx.send("タイトルを指定してください。")
            return

        if not content:
            content = "詳細なし"

        entry_id = create_entry(title=title, content=content)

        embed = discord.Embed(title="エントリーを作成しました", color=discord.Color.green())
        embed.add_field(name="ID", value=entry_id, inline=True)
        embed.add_field(name="タイトル", value=title, inline=False)

        await ctx.send(embed=embed)

    @commands.command()
    async def show(self, ctx: commands.Context, entry_id: int):
        entry = get_entry(entry_id)

        if not entry:
            await ctx.send("エントリー #" + str(entry_id) + " が見つかりませんでした。")
            return

        status_emoji = "✅" if entry["status"] == "active" else "📦"

        embed = discord.Embed(title=status_emoji + " " + entry["title"], color=discord.Color.blue())
        embed.add_field(name="ID", value=entry["id"], inline=True)
        embed.add_field(name="ステータス", value=entry["status"], inline=True)

        await ctx.send(embed=embed)

    @commands.command()
    async def tags(self, ctx: commands.Context):
        tags = get_all_tags()

        if not tags:
            await ctx.send("タグがありません。")
            return

        embed = discord.Embed(title="タグ一覧 (" + str(len(tags)) + "件)", color=discord.Color.purple())
        embed.add_field(name="タグ", value=", ".join(tags[:30]), inline=False)

        await ctx.send(embed=embed)


def run_bot(token: str):
    bot = EroticAiVideoGenAgentDiscordBot(command_prefix="!")
    bot.run(token)


if __name__ == "__main__":
    import os
    token = os.environ.get("DISCORD_BOT_TOKEN")
    if not token:
        print("DISCORD_BOT_TOKEN環境変数を設定してください。")
    else:
        run_bot(token)
