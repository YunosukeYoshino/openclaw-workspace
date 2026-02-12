#!/usr/bin/env python3
"""
えっちなイラストレーター管理エージェント - Discord Botモジュール

Discordを介したエージェント操作インターフェース
"""

import discord
from discord.ext import commands
from typing import Optional
import asyncio

from db import EroticArtistAgentDB


class EroticArtistAgentBot(commands.Bot):
    """えっちなイラストレーター管理エージェント Discord Bot"""

    def __init__(self, db_path: str = None, command_prefix: str = "!"):
        """初期化"""
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(
            command_prefix=command_prefix,
            intents=intents,
            help_command=None
        )
        self.db = EroticArtistAgentDB(db_path)
        self.db.initialize()

    async def setup_hook(self):
        """Bot起動時の処理"""
        print(str(self.user) + " が起動しました")

    async def on_ready(self):
        """Bot準備完了時の処理"""
        activity = discord.Activity(
            type=discord.ActivityType.watching,
            name="えっちなコンテンツ"
        )
        await self.change_presence(activity=activity)
        print(str(self.user.name) + " が準備完了しました")

    async def on_command_error(self, ctx: commands.Context, error: Exception):
        """コマンドエラー処理"""
        if isinstance(error, commands.CommandNotFound):
            await ctx.send("❌ そのコマンドは存在しません")
        else:
            await ctx.send("❌ エラーが発生しました: " + str(error))


# Botインスタンス
bot = None


def get_bot(db_path: str = None, command_prefix: str = "!"):
    """Botインスタンス取得"""
    global bot
    if bot is None:
        bot = EroticArtistAgentBot(db_path, command_prefix)

        # コマンド登録
        @bot.command(name="追加", aliases=["add"])
        async def add_entry(ctx: commands.Context, title: str, *, description: str = ""):
            """エントリー追加"""
            entry_id = bot.db.add_entry(title=title, description=description, source="discord")
            embed = discord.Embed(
                title="✅ エントリー追加完了",
                description="ID: " + str(entry_id) + "\nタイトル: " + str(title),
                color=0x00ff00
            )
            await ctx.send(embed=embed)

        @bot.command(name="検索", aliases=["search", "find"])
        async def search_entries(ctx: commands.Context, *, query: str):
            """エントリー検索"""
            entries = bot.db.search_entries(query, limit=10)

            if not entries:
                await ctx.send("🔍 該当するエントリーが見つかりませんでした")
                return

            embed = discord.Embed(
                title="🔍 検索結果: " + str(query),
                description=str(len(entries)) + "件見つかりました",
                color=0x00aaff
            )

            for entry in entries[:5]:
                desc = entry.get("description", "")[:50] + "..." if len(entry.get("description", "")) > 50 else entry.get("description", "")
                embed.add_field(
                    name=str(entry['id']) + ": " + str(entry['title']),
                    value=desc or "説明なし",
                    inline=False
                )

            await ctx.send(embed=embed)

        @bot.command(name="一覧", aliases=["list", "ls"])
        async def list_entries(ctx: commands.Context, limit: int = 10):
            """エントリー一覧"""
            entries = bot.db.list_entries(limit=limit)

            if not entries:
                await ctx.send("📋 エントリーがまだありません")
                return

            embed = discord.Embed(
                title="📋 エントリー一覧 (最新" + str(limit) + "件)",
                color=0xffaa00
            )

            for entry in entries:
                desc = entry.get("description", "")[:30] + "..." if len(entry.get("description", "")) > 30 else entry.get("description", "")
                embed.add_field(
                    name=str(entry['id']) + ": " + str(entry['title']),
                    value=desc or "説明なし",
                    inline=False
                )

            await ctx.send(embed=embed)

        @bot.command(name="詳細", aliases=["detail", "info"])
        async def get_detail(ctx: commands.Context, entry_id: int):
            """エントリー詳細"""
            entry = bot.db.get_entry(entry_id)

            if not entry:
                await ctx.send("❌ ID " + str(entry_id) + " のエントリーが見つかりません")
                return

            embed = discord.Embed(
                title="📖 " + str(entry['title']),
                description=entry.get("description", "説明なし") or "説明なし",
                color=0xff00ff
            )
            embed.add_field(name="ソース", value=entry.get("source", "なし") or "なし", inline=True)
            embed.add_field(name="評価", value="⭐ " + str(entry.get('rating', 0)) or "⭐ 0", inline=True)
            if entry.get("tags"):
                embed.add_field(name="タグ", value=entry.get("tags"), inline=False)
            embed.add_field(name="作成日", value=entry.get("created_at", "")[:10], inline=True)

            await ctx.send(embed=embed)

        @bot.command(name="タグ検索", aliases=["tag"])
        async def search_by_tag(ctx: commands.Context, tag: str):
            """タグで検索"""
            entries = bot.db.get_entries_by_tag(tag, limit=10)

            if not entries:
                await ctx.send("🏷️ タグ「" + str(tag) + "」のエントリーが見つかりません")
                return

            embed = discord.Embed(
                title="🏷️ タグ「" + str(tag) + "」の結果",
                description=str(len(entries)) + "件見つかりました",
                color=0x00aaff
            )

            for entry in entries[:5]:
                embed.add_field(
                    name=str(entry['id']) + ": " + str(entry['title']),
                    value=entry.get("description", "")[:30] or "説明なし",
                    inline=False
                )

            await ctx.send(embed=embed)

        @bot.command(name="統計", aliases=["stats", "stat"])
        async def get_stats(ctx: commands.Context):
            """統計情報"""
            stats = bot.db.get_stats()

            embed = discord.Embed(
                title="📊 統計情報",
                color=0xffaa00
            )
            embed.add_field(name="総エントリー数", value=str(stats['total_entries']) + "件", inline=True)
            embed.add_field(name="平均評価", value="⭐ " + str(stats['average_rating']), inline=True)

            if stats.get("top_rated"):
                top_list = "\n".join([str(i+1) + ". " + str(r['title']) + " (⭐" + str(r['rating']) + ")" for i, r in enumerate(stats['top_rated'][:3])])
                embed.add_field(name="🏆 高評価TOP3", value=top_list, inline=False)

            await ctx.send(embed=embed)

        @bot.command(name="削除", aliases=["delete", "rm"])
        async def delete_entry(ctx: commands.Context, entry_id: int):
            """エントリー削除"""
            entry = bot.db.get_entry(entry_id)

            if not entry:
                await ctx.send("❌ ID " + str(entry_id) + " のエントリーが見つかりません")
                return

            if bot.db.delete_entry(entry_id):
                embed = discord.Embed(
                    title="🗑️ 削除完了",
                    description="ID " + str(entry_id) + ": " + str(entry['title']) + " を削除しました",
                    color=0xff0000
                )
                await ctx.send(embed=embed)
            else:
                await ctx.send("❌ 削除に失敗しました")

        @bot.command(name="ヘルプ", aliases=["help", "?"])
        async def show_help(ctx: commands.Context):
            """ヘルプ表示"""
            embed = discord.Embed(
                title="🤖 " + str(bot.user.name) + " コマンド一覧",
                description="えっちなイラストレーター管理エージェントの使い方",
                color=0x00aaff
            )

            commands_list = [
                ("!追加 <タイトル> [説明]", "エントリーを追加"),
                ("!検索 <キーワード>", "キーワードで検索"),
                ("!一覧 [件数]", "エントリー一覧を表示"),
                ("!詳細 <ID>", "指定IDの詳細を表示"),
                ("!タグ検索 <タグ名>", "タグで検索"),
                ("!統計", "統計情報を表示"),
                ("!削除 <ID>", "エントリーを削除"),
                ("!ヘルプ", "このヘルプを表示")
            ]

            for cmd, desc in commands_list:
                embed.add_field(name=cmd, value=desc, inline=False)

            await ctx.send(embed=embed)

    return bot


def run_bot(token: str, db_path: str = None, command_prefix: str = "!"):
    """Bot実行"""
    bot = get_bot(db_path, command_prefix)
    bot.run(token)


if __name__ == "__main__":
    import os

    # 環境変数からトークン取得
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        print("DISCORD_TOKEN 環境変数を設定してください")
        exit(1)

    run_bot(token)
