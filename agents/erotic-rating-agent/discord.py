#!/usr/bin/env python3
"""
えっちコンテンツ評価レビューエージェント - Discord Botモジュール

Discordを介したエージェント操作インターフェース
"""

import discord
from discord.ext import commands
from typing import Optional
import asyncio

from db import EroticRatingAgentDB


class EroticRatingAgentBot(commands.Bot):
    """えっちコンテンツ評価レビューエージェント Discord Bot"""

    def __init__(self, db_path: str = None, command_prefix: str = "!"):
        """初期化"""
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(
            command_prefix=command_prefix,
            intents=intents,
            help_command=None
        )
        self.db = EroticRatingAgentDB(db_path)
        self.db.initialize()

    async def setup_hook(self):
        """Bot起動時の処理"""
        print(str(self.user) + " が起動しました")

    async def on_ready(self):
        """Bot準備完了時の処理"""
        activity = discord.Activity(
            type=discord.ActivityType.watching,
            name="評価レビュー"
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
        bot = EroticRatingAgentBot(db_path, command_prefix)

        # コマンド登録
        @bot.command(name="評価追加", aliases=["rateadd"])
        async def add_rating(ctx: commands.Context, title: str, overall: int, *, artist: str = ""):
            """評価追加"""
            entry_id = bot.db.add_rating(title=title, artist=artist,
                                        overall_rating=overall, source="discord")
            embed = discord.Embed(
                title="⭐ 評価追加完了",
                description="ID: " + str(entry_id) + "\nタイトル: " + str(title) + "\n評価: " + str(overall) + "/5",
                color=0xffd700
            )
            await ctx.send(embed=embed)

        @bot.command(name="詳細評価", aliases=["ratedetail"])
        async def add_detailed_rating(ctx: commands.Context, title: str, overall: int,
                                    art: int, story: int, erotic: int):
            """詳細評価追加"""
            entry_id = bot.db.add_rating(
                title=title,
                overall_rating=overall,
                art_quality=art,
                story_quality=story,
                erotic_quality=erotic,
                source="discord"
            )
            stars = "⭐" * overall
            embed = discord.Embed(
                title="⭐ 詳細評価追加完了",
                description="ID: " + str(entry_id) + "\nタイトル: " + str(title) + "\n総合: " + stars,
                color=0xffd700
            )
            embed.add_field(name="画質", value="⭐" * art, inline=True)
            embed.add_field(name="ストーリー", value="⭐" * story, inline=True)
            embed.add_field(name="エロさ", value="⭐" * erotic, inline=True)
            await ctx.send(embed=embed)

        @bot.command(name="評価検索", aliases=["ratesearch"])
        async def search_ratings(ctx: commands.Context, *, query: str):
            """評価検索"""
            entries = bot.db.search_ratings(query, limit=10)

            if not entries:
                await ctx.send("🔍 該当する評価が見つかりませんでした")
                return

            embed = discord.Embed(
                title="🔍 評価検索結果: " + str(query),
                description=str(len(entries)) + "件見つかりました",
                color=0xffd700
            )

            for entry in entries[:5]:
                stars = "⭐" * entry.get("overall_rating", 0)
                embed.add_field(
                    name=str(entry['id']) + ": " + str(entry['title']) + " " + stars,
                    value=entry.get("description", "")[:50] or "説明なし",
                    inline=False
                )

            await ctx.send(embed=embed)

        @bot.command(name="評価一覧", aliases=["ratelist"])
        async def list_ratings(ctx: commands.Context, limit: int = 10):
            """評価一覧"""
            entries = bot.db.list_ratings(limit=limit)

            if not entries:
                await ctx.send("📋 評価がまだありません")
                return

            embed = discord.Embed(
                title="📋 評価一覧 (最新" + str(limit) + "件)",
                color=0xffd700
            )

            for entry in entries:
                stars = "⭐" * entry.get("overall_rating", 0)
                artist = entry.get("artist", "") or "不明"
                embed.add_field(
                    name=str(entry['id']) + ": " + str(entry['title']) + " " + stars,
                    value=artist,
                    inline=False
                )

            await ctx.send(embed=embed)

        @bot.command(name="評価詳細", aliases=["showrate"])
        async def get_detail(ctx: commands.Context, rating_id: int):
            """評価詳細"""
            entry = bot.db.get_rating(rating_id)

            if not entry:
                await ctx.send("❌ ID " + str(rating_id) + " の評価が見つかりません")
                return

            overall = "⭐" * entry.get("overall_rating", 0)
            art = "⭐" * entry.get("art_quality", 0) if entry.get("art_quality") else "-"
            story = "⭐" * entry.get("story_quality", 0) if entry.get("story_quality") else "-"
            erotic = "⭐" * entry.get("erotic_quality", 0) if entry.get("erotic_quality") else "-"
            tech = "⭐" * entry.get("technical_quality", 0) if entry.get("technical_quality") else "-"
            recommended = "✅ おすすめ" if entry.get("is_recommended") else "❌ 非おすすめ"

            embed = discord.Embed(
                title="⭐ " + str(entry['title']),
                description=entry.get("description", "説明なし") or "説明なし",
                color=0xffd700
            )
            embed.add_field(name="アーティスト", value=entry.get("artist", "不明") or "不明", inline=True)
            embed.add_field(name="総合評価", value=overall, inline=True)
            embed.add_field(name="おすすめ", value=recommended, inline=True)
            embed.add_field(name="画質", value=art, inline=True)
            embed.add_field(name="ストーリー", value=story, inline=True)
            embed.add_field(name="エロさ", value=erotic, inline=True)
            embed.add_field(name="技術", value=tech, inline=True)
            if entry.get("tags"):
                embed.add_field(name="タグ", value=entry.get("tags"), inline=False)
            if entry.get("review_text"):
                embed.add_field(name="レビュー", value=entry.get("review_text")[:500], inline=False)
            embed.add_field(name="作成日", value=entry.get("created_at", "")[:10], inline=True)

            await ctx.send(embed=embed)

        @bot.command(name="高評価", aliases=["toprated"])
        async def get_top_rated(ctx: commands.Context, limit: int = 10):
            """高評価順に取得"""
            entries = bot.db.get_top_rated(limit=limit)

            if not entries:
                await ctx.send("📋 高評価の評価がまだありません")
                return

            embed = discord.Embed(
                title="🏆 高評価TOP" + str(limit),
                color=0xffd700
            )

            for i, entry in enumerate(entries, 1):
                stars = "⭐" * entry.get("overall_rating", 0)
                embed.add_field(
                    name=str(i) + ". " + str(entry['title']) + " " + stars,
                    value="アーティスト: " + (entry.get("artist", "不明") or "不明"),
                    inline=False
                )

            await ctx.send(embed=embed)

        @bot.command(name="おすすめ", aliases=["recommended"])
        async def get_recommended(ctx: commands.Context, limit: int = 10):
            """おすすめ取得"""
            entries = bot.db.get_recommended(limit=limit)

            if not entries:
                await ctx.send("📋 おすすめの評価がまだありません")
                return

            embed = discord.Embed(
                title="💖 おすすめ作品",
                color=0xffd700
            )

            for entry in entries:
                stars = "⭐" * entry.get("overall_rating", 0)
                embed.add_field(
                    name=str(entry['id']) + ": " + str(entry['title']) + " " + stars,
                    value="アーティスト: " + (entry.get("artist", "不明") or "不明"),
                    inline=False
                )

            await ctx.send(embed=embed)

        @bot.command(name="統計", aliases=["stats"])
        async def get_stats(ctx: commands.Context):
            """統計情報"""
            stats = bot.db.get_stats()

            embed = discord.Embed(
                title="📊 統計情報",
                color=0xffd700
            )
            embed.add_field(name="総評価数", value=str(stats['total_ratings']) + "件", inline=True)
            embed.add_field(name="平均総合評価", value="⭐ " + str(stats['average_overall']), inline=True)
            embed.add_field(name="平均画質", value="⭐ " + str(stats['average_art_quality']), inline=True)
            embed.add_field(name="平均ストーリー", value="⭐ " + str(stats['average_story_quality']), inline=True)
            embed.add_field(name="平均エロさ", value="⭐ " + str(stats['average_erotic_quality']), inline=True)
            embed.add_field(name="おすすめ数", value=str(stats['recommended_count']) + "件", inline=True)

            await ctx.send(embed=embed)

        @bot.command(name="評価削除", aliases=["ratedel"])
        async def delete_rating(ctx: commands.Context, rating_id: int):
            """評価削除"""
            entry = bot.db.get_rating(rating_id)

            if not entry:
                await ctx.send("❌ ID " + str(rating_id) + " の評価が見つかりません")
                return

            if bot.db.delete_rating(rating_id):
                embed = discord.Embed(
                    title="🗑️ 削除完了",
                    description="ID " + str(rating_id) + ": " + str(entry['title']) + " を削除しました",
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
                description="えっちコンテンツ評価レビューエージェントの使い方",
                color=0xffd700
            )

            commands_list = [
                ("!評価追加 <タイトル> <総合評価> [アーティスト]", "評価を追加"),
                ("!詳細評価 <タイトル> <総合> <画質> <ストーリー> <エロさ>", "詳細評価を追加"),
                ("!評価検索 <キーワード>", "キーワードで検索"),
                ("!評価一覧 [件数]", "評価一覧を表示"),
                ("!評価詳細 <ID>", "指定IDの詳細を表示"),
                ("!高評価 [件数]", "高評価順に表示"),
                ("!おすすめ [件数]", "おすすめを表示"),
                ("!統計", "統計情報を表示"),
                ("!評価削除 <ID>", "評価を削除"),
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
