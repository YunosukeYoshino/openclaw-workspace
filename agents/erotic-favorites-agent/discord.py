#!/usr/bin/env python3
"""
お気に入りのえっちな作品コレクションエージェント - Discord Botモジュール

Discordを介したエージェント操作インターフェース
"""

import discord
from discord.ext import commands
from typing import Optional
import asyncio

from db import EroticFavoritesAgentDB


class EroticFavoritesAgentBot(commands.Bot):
    """お気に入りのえっちな作品コレクションエージェント Discord Bot"""

    def __init__(self, db_path: str = None, command_prefix: str = "!"):
        """初期化"""
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(
            command_prefix=command_prefix,
            intents=intents,
            help_command=None
        )
        self.db = EroticFavoritesAgentDB(db_path)
        self.db.initialize()

    async def setup_hook(self):
        """Bot起動時の処理"""
        print(str(self.user) + " が起動しました")

    async def on_ready(self):
        """Bot準備完了時の処理"""
        activity = discord.Activity(
            type=discord.ActivityType.watching,
            name="お気に入りコレクション"
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
        bot = EroticFavoritesAgentBot(db_path, command_prefix)

        # コマンド登録
        @bot.command(name="お気に入り追加", aliases=["favadd"])
        async def add_favorite(ctx: commands.Context, title: str, *, artist: str = ""):
            """お気に入り追加"""
            entry_id = bot.db.add_favorite(title=title, artist=artist, source="discord")
            embed = discord.Embed(
                title="❤️ お気に入り追加完了",
                description="ID: " + str(entry_id) + "\nタイトル: " + str(title),
                color=0xff69b4
            )
            await ctx.send(embed=embed)

        @bot.command(name="お気に入り検索", aliases=["favsearch"])
        async def search_favorites(ctx: commands.Context, *, query: str):
            """お気に入り検索"""
            entries = bot.db.search_favorites(query, limit=10)

            if not entries:
                await ctx.send("🔍 該当するお気に入りが見つかりませんでした")
                return

            embed = discord.Embed(
                title="🔍 お気に入り検索結果: " + str(query),
                description=str(len(entries)) + "件見つかりました",
                color=0xff69b4
            )

            for entry in entries[:5]:
                artist = entry.get("artist", "") or "不明"
                embed.add_field(
                    name=str(entry['id']) + ": " + str(entry['title']) + " by " + str(artist),
                    value=entry.get("description", "")[:50] or "説明なし",
                    inline=False
                )

            await ctx.send(embed=embed)

        @bot.command(name="お気に入り一覧", aliases=["favlist"])
        async def list_favorites(ctx: commands.Context, limit: int = 10):
            """お気に入り一覧"""
            entries = bot.db.list_favorites(limit=limit)

            if not entries:
                await ctx.send("📋 お気に入りがまだありません")
                return

            embed = discord.Embed(
                title="📋 お気に入り一覧 (最新" + str(limit) + "件)",
                color=0xff69b4
            )

            for entry in entries:
                rank = "⭐" * min(entry.get("favorite_rank", 0), 5)
                artist = entry.get("artist", "") or "不明"
                embed.add_field(
                    name=str(entry['id']) + ": " + str(entry['title']) + " " + rank,
                    value=artist + "\n" + (entry.get("category", "") or ""),
                    inline=False
                )

            await ctx.send(embed=embed)

        @bot.command(name="お気に入り詳細", aliases=["favdetail"])
        async def get_detail(ctx: commands.Context, favorite_id: int):
            """お気に入り詳細"""
            entry = bot.db.get_favorite(favorite_id)

            if not entry:
                await ctx.send("❌ ID " + str(favorite_id) + " のお気に入りが見つかりません")
                return

            rank = "⭐" * min(entry.get("favorite_rank", 0), 5)
            visibility = "🌍 公開" if entry.get("is_public") else "🔒 非公開"

            embed = discord.Embed(
                title="❤️ " + str(entry['title']),
                description=entry.get("description", "説明なし") or "説明なし",
                color=0xff69b4
            )
            embed.add_field(name="アーティスト", value=entry.get("artist", "不明") or "不明", inline=True)
            embed.add_field(name="カテゴリ", value=entry.get("category", "なし") or "なし", inline=True)
            embed.add_field(name="評価", value=rank or "未評価", inline=True)
            embed.add_field(name="公開設定", value=visibility, inline=True)
            if entry.get("tags"):
                embed.add_field(name="タグ", value=entry.get("tags"), inline=False)
            if entry.get("notes"):
                embed.add_field(name="メモ", value=entry.get("notes"), inline=False)
            embed.add_field(name="作成日", value=entry.get("created_at", "")[:10], inline=True)

            await ctx.send(embed=embed)

        @bot.command(name="カテゴリ一覧", aliases=["categories"])
        async def list_categories(ctx: commands.Context):
            """カテゴリ一覧"""
            entries = bot.db.list_favorites(limit=1000)
            categories = {}
            for entry in entries:
                cat = entry.get("category", "未分類") or "未分類"
                categories[cat] = categories.get(cat, 0) + 1

            if not categories:
                await ctx.send("📂 カテゴリがまだありません")
                return

            embed = discord.Embed(
                title="📂 カテゴリ一覧",
                color=0xff69b4
            )

            for cat, count in sorted(categories.items(), key=lambda x: -x[1])[:10]:
                embed.add_field(name=cat, value=str(count) + "件", inline=True)

            await ctx.send(embed=embed)

        @bot.command(name="コレクション作成", aliases=["newcoll"])
        async def create_collection(ctx: commands.Context, name: str, *, description: str = ""):
            """コレクション作成"""
            coll_id = bot.db.create_collection(name=name, description=description)
            embed = discord.Embed(
                title="📁 コレクション作成完了",
                description="ID: " + str(coll_id) + "\n名前: " + str(name),
                color=0xff69b4
            )
            await ctx.send(embed=embed)

        @bot.command(name="コレクション一覧", aliases=["colllist"])
        async def list_collections(ctx: commands.Context):
            """コレクション一覧"""
            collections = bot.db.list_collections()

            if not collections:
                await ctx.send("📁 コレクションがまだありません")
                return

            embed = discord.Embed(
                title="📁 コレクション一覧",
                color=0xff69b4
            )

            for coll in collections:
                embed.add_field(
                    name=str(coll['id']) + ": " + str(coll['name']),
                    value=str(coll.get('item_count', 0)) + "件",
                    inline=False
                )

            await ctx.send(embed=embed)

        @bot.command(name="コレクション追加", aliases=["addtocoll"])
        async def add_to_collection(ctx: commands.Context, collection_id: int, favorite_id: int):
            """コレクションに追加"""
            if bot.db.add_to_collection(collection_id, favorite_id):
                await ctx.send("✅ コレクションに追加しました")
            else:
                await ctx.send("❌ 追加に失敗しました")

        @bot.command(name="統計", aliases=["stats"])
        async def get_stats(ctx: commands.Context):
            """統計情報"""
            stats = bot.db.get_stats()

            embed = discord.Embed(
                title="📊 統計情報",
                color=0xff69b4
            )
            embed.add_field(name="総お気に入り数", value=str(stats['total_favorites']) + "件", inline=True)
            embed.add_field(name="公開", value=str(stats['public_favorites']) + "件", inline=True)
            embed.add_field(name="非公開", value=str(stats['private_favorites']) + "件", inline=True)
            embed.add_field(name="コレクション数", value=str(stats['total_collections']) + "件", inline=True)
            embed.add_field(name="トップカテゴリ", value=stats['top_category'], inline=True)
            embed.add_field(name="トップアーティスト", value=stats['top_artist'], inline=True)

            await ctx.send(embed=embed)

        @bot.command(name="お気に入り削除", aliases=["favdel"])
        async def delete_favorite(ctx: commands.Context, favorite_id: int):
            """お気に入り削除"""
            entry = bot.db.get_favorite(favorite_id)

            if not entry:
                await ctx.send("❌ ID " + str(favorite_id) + " のお気に入りが見つかりません")
                return

            if bot.db.delete_favorite(favorite_id):
                embed = discord.Embed(
                    title="🗑️ 削除完了",
                    description="ID " + str(favorite_id) + ": " + str(entry['title']) + " を削除しました",
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
                description="お気に入りのえっちな作品コレクションエージェントの使い方",
                color=0xff69b4
            )

            commands_list = [
                ("!お気に入り追加 <タイトル> [アーティスト]", "お気に入りを追加"),
                ("!お気に入り検索 <キーワード>", "キーワードで検索"),
                ("!お気に入り一覧 [件数]", "お気に入り一覧を表示"),
                ("!お気に入り詳細 <ID>", "指定IDの詳細を表示"),
                ("!カテゴリ一覧", "カテゴリ一覧を表示"),
                ("!コレクション作成 <名前> [説明]", "コレクションを作成"),
                ("!コレクション一覧", "コレクション一覧を表示"),
                ("!コレクション追加 <コレID> <お気に入りID>", "コレクションに追加"),
                ("!統計", "統計情報を表示"),
                ("!お気に入り削除 <ID>", "お気に入りを削除"),
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
