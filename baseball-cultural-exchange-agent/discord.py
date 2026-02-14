#!/usr/bin/env python3
"""
baseball-cultural-exchange-agent - Discord Botモジュール
"""

import discord
from discord.ext import commands
import logging
from typing import Optional
import asyncio

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BaseballCulturalExchangeAgentBot(commands.Bot):
    """baseball-cultural-exchange-agent Discord Bot"""

    def __init__(self, command_prefix: str = "!", token: Optional[str] = None):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix=command_prefix, intents=intents)

        self.token = token

    async def setup_hook(self):
        """Botセットアップ"""
        logger.info(f"Bot ready: {self.user}")

    async def on_ready(self):
        """Bot起動時"""
        logger.info(f"Bot is ready! Logged in as {self.user}")
        activity = discord.Activity(
            type=discord.ActivityType.watching,
            name="野球文化交流エージェント。国際的な文化交流の促進。"
        )
        await self.change_presence(activity=activity)

    async def on_message(self, message: discord.Message):
        """メッセージ受信時"""
        if message.author == self.user:
            return

        await self.process_commands(message)

    async def send_help(self, channel: discord.TextChannel):
        """ヘルプ送信"""
        embed = discord.Embed(
            title="baseball-cultural-exchange-agent",
            description="野球文化交流エージェント。国際的な文化交流の促進。",
            color=0x00ff00
        )

        embed.add_field(
            name="コマンド",
            value="`!status` - ステータス確認\n`!add <content>` - エントリー追加\n`!list` - エントリー一覧\n`!search <query>` - エントリー検索\n`!help` - ヘルプ表示",
            inline=False
        )

        await channel.send(embed=embed)

    async def send_status(self, channel: discord.TextChannel, status_data: dict):
        """ステータス送信"""
        embed = discord.Embed(
            title="ステータス",
            description=f"現在のステータス",
            color=0x00ff00
        )

        for key, value in status_data.items():
            embed.add_field(name=key, value=str(value), inline=False)

        await channel.send(embed=embed)

    async def send_entry(self, channel: discord.TextChannel, entry: dict):
        """エントリー送信"""
        embed = discord.Embed(
            title=entry.get('title', 'エントリー'),
            description=entry.get('content', '')[:2000],
            color=0x00ff00
        )

        if entry.get('metadata'):
            embed.add_field(
                name="メタデータ",
                value=f"```json\n{entry['metadata']}\n```",
                inline=False
            )

        embed.set_footer(text=f"ID: {entry.get('id')} | 作成: {entry.get('created_at')}")

        await channel.send(embed=embed)

    async def send_error(self, channel: discord.TextChannel, error: str):
        """エラー送信"""
        embed = discord.Embed(
            title="エラー",
            description=error,
            color=0xff0000
        )
        await channel.send(embed=embed)


class BaseballCulturalExchangeAgentCommands(commands.Cog):
    """baseball-cultural-exchange-agent コマンド"""

    def __init__(self, bot: BaseballCulturalExchangeAgentBot):
        self.bot = bot
        self.db = None  # DatabaseManagerをセット

    def set_db(self, db):
        """データベース設定"""
        self.db = db

    @commands.command(name='status')
    async def cmd_status(self, ctx: commands.Context):
        """ステータス確認"""
        if not self.db:
            await self.bot.send_error(ctx.channel, "データベースが未設定です")
            return

        stats = self.db.get_stats()
        await self.bot.send_status(ctx.channel, stats)

    @commands.command(name='add')
    async def cmd_add(self, ctx: commands.Context, *, content: str):
        """エントリー追加"""
        if not self.db:
            await self.bot.send_error(ctx.channel, "データベースが未設定です")
            return

        try:
            entry_id = self.db.add_entry(
                title=None,
                content=content,
                metadata={"author": str(ctx.author)}
            )

            await ctx.send(f"エントリーを追加しました (ID: {entry_id})")
        except Exception as e:
            await self.bot.send_error(ctx.channel, f"追加失敗: {e}")

    @commands.command(name='list')
    async def cmd_list(self, ctx: commands.Context, limit: int = 10):
        """エントリー一覧"""
        if not self.db:
            await self.bot.send_error(ctx.channel, "データベースが未設定です")
            return

        entries = self.db.list_entries(limit=limit)

        if not entries:
            await ctx.send("エントリーがありません")
            return

        for entry in entries:
            await self.bot.send_entry(ctx.channel, entry)

    @commands.command(name='search')
    async def cmd_search(self, ctx: commands.Context, *, query: str):
        """エントリー検索"""
        if not self.db:
            await self.bot.send_error(ctx.channel, "データベースが未設定です")
            return

        entries = self.db.search_entries(query, limit=10)

        if not entries:
            await ctx.send(f"検索結果: '{query}' - 見つかりませんでした")
            return

        for entry in entries:
            await self.bot.send_entry(ctx.channel, entry)

    @commands.command(name='help')
    async def cmd_help(self, ctx: commands.Context):
        """ヘルプ表示"""
        await self.bot.send_help(ctx.channel)


def create_bot(token: Optional[str] = None, command_prefix: str = "!") -> BaseballCulturalExchangeAgentBot:
    """Botインスタンス作成"""
    bot = BaseballCulturalExchangeAgentBot(command_prefix=command_prefix, token=token)

    # コグを追加
    bot.add_cog(BaseballCulturalExchangeAgentCommands(bot))

    return bot


def main():
    """メイン関数"""
    import os

    token = os.getenv("DISCORD_TOKEN")
    if not token:
        logger.error("DISCORD_TOKEN environment variable not set")
        return

    bot = create_bot(token=token)
    bot.run(token)


if __name__ == "__main__":
    main()
