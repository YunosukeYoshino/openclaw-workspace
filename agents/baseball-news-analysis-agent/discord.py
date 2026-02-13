#!/usr/bin/env python3
"""
野球ニュース分析エージェント - Discord Botモジュール

Discord Bot連携モジュール
"""

import discord
from discord.ext import commands
from typing import Optional, List
import logging

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BaseballNewsAnalysisAgentDiscord:
    """野球ニュース分析エージェント Discord Botクラス"""

    def __init__(self, agent_instance, token: Optional[str] = None):
        """初期化

        Args:
            agent_instance: エージェントインスタンス
            token: Discord Botトークン
        """
        self.agent = agent_instance
        self.token = token
        self.bot = commands.Bot(command_prefix='!', intents=discord.Intents.default())
        self._setup_commands()

    def _setup_commands(self):
        """コマンド設定"""

        @self.bot.command(name='add_news-analysis')
        async def add_entry(ctx, title: str, *, content: str):
            """エントリー追加コマンド"""
            entry_id = self.agent.add_entry(title, content)
            await ctx.send(f"✅ エントリー追加完了 (ID: {entry_id})")

        @self.bot.command(name='list_news-analysis')
        async def list_entries(ctx, limit: int = 10):
            """エントリーリスト表示コマンド"""
            entries = self.agent.list_entries(limit=limit)
            if not entries:
                await ctx.send("📋 エントリーがありません")
                return

            msg = "**📋 エントリーリスト**\n\n"
            for entry in entries:
                msg += f"**ID {entry['id']}**: {entry.get('title', 'No title')}\n"
                msg += f"{entry.get('content', '')[:50]}...\n\n"
            await ctx.send(msg[:2000])

        @self.bot.command(name='get_news-analysis')
        async def get_entry(ctx, entry_id: int):
            """エントリー取得コマンド"""
            entry = self.agent.get_entry(entry_id)
            if not entry:
                await ctx.send(f"❌ エントリーが見つかりません (ID: {entry_id})")
                return

            msg = f"**📝 エントリー ID {entry['id']}**\n\n"
            msg += f"**タイトル**: {entry.get('title', 'No title')}\n"
            msg += f"**コンテンツ**: {entry.get('content', '')}\n"
            if entry.get('tags'):
                msg += f"**タグ**: {entry['tags']}\n"
            await ctx.send(msg)

        @self.bot.command(name='search_news-analysis')
        async def search_entries(ctx, *, query: str):
            """エントリー検索コマンド"""
            entries = self.agent.search_entries(query)
            if not entries:
                await ctx.send(f"🔍 検索結果なし: {query}")
                return

            msg = f"**🔍 検索結果: {query}**\n\n"
            for entry in entries[:10]:
                msg += f"**ID {entry['id']}**: {entry.get('title', 'No title')}\n"
            await ctx.send(msg)

        @self.bot.command(name='stats_news-analysis')
        async def get_stats(ctx):
            """統計情報表示コマンド"""
            stats = self.agent.get_stats()
            msg = f"**📊 統計情報**\n"
            msg += f"📝 総エントリー: {stats['total']}\n"
            msg += f"✅ アクティブ: {stats['active']}\n"
            await ctx.send(msg)

    def run(self):
        """Bot実行"""
        if not self.token:
            logger.warning("Discord Bot token not set")
            return

        logger.info("Starting Discord Bot...")
        self.bot.run(self.token)


def main():
    """メイン関数"""
    from agent import BaseballNewsAnalysisAgent

    agent = BaseballNewsAnalysisAgent()
    discord_bot = BaseballNewsAnalysisAgentDiscord(agent)
    discord_bot.run()


if __name__ == "__main__":
    main()
