"""
えっちコンテンツ行動アナリストエージェント - Discord Bot Integration
ユーザー行動パターンの分析・予測
"""

import discord
from discord.ext import commands
import logging
from pathlib import Path
from typing import Optional, List
from .db import Erotic_behavior_analyst_agentDB

logger = logging.getLogger('erotic-behavior-analyst-agent')

intents = discord.Intents.default()
intents.message_content = True

class Erotic_behavior_analyst_agentBot(commands.Bot):
    """Discord Bot for えっちコンテンツ行動アナリストエージェント"""

    def __init__(self, command_prefix: str = "!", db: Optional[Erotic_behavior_analyst_agentDB] = None):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix=command_prefix, intents=intents)
        self.db = db or Erotic_behavior_analyst_agentDB()

    async def setup_hook(self) -> None:
        """Bot起動時のセットアップ"""
        logger.info(f"Setting up {self.__class__.__name__}")
        await self.add_cog(Erotic_behavior_analyst_agentCommands(self))
        await self.tree.sync()

    async def on_ready(self) -> None:
        """Bot準備完了"""
        logger.info("self.user.name} is ready!")

class Erotic_behavior_analyst_agentCommands(commands.Cog):
    """コマンド定義"""

    def __init__(self, bot: Erotic_behavior_analyst_agentBot):
        self.bot = bot

    @commands.command()
    async def status(self, ctx: commands.Context) -> None:
        """ステータスを表示"""
        stats = self.bot.db.get_stats()
        embed = discord.Embed(
            title="📊 えっちコンテンツ行動アナリストエージェント Status",
            color=discord.Color.blue()
        )
        embed.add_field(name="Total Entries", value=stats["total_entries"], inline=True)
        embed.add_field(name="Total Tags", value=stats["total_tags"], inline=True)

        if stats["entries_by_category"]:
            category_text = "\n".join(
                f"{k}: {v}" for k, v in stats["entries_by_category"].items()
            )
            embed.add_field(name="By Category", value=category_text or "None", inline=False)

        await ctx.send(embed=embed)

    @commands.command()
    async def add(self, ctx: commands.Context, title: str, *, content: str) -> None:
        """エントリーを追加"""
        entry_id = self.bot.db.add_entry(title, content)
        await ctx.send(f"✅ Entry added! ID: {entry_id}")

    @commands.command()
    async def list(self, ctx: commands.Context, category: str = None) -> None:
        """エントリー一覧を表示"""
        entries = self.bot.db.get_entries(category=category, limit=10)

        if not entries:
            await ctx.send("📭 No entries found.")
            return

        title_text = "📝 Entries - " + category if category else "📝 Entries"
        embed = discord.Embed(
            title=title_text,
            color=discord.Color.green()
        )

        for entry in entries:
            title = entry["title"] or "Untitled"
            content = entry["content"][:100] + "..." if len(entry["content"]) > 100 else entry["content"]
            embed.add_field(
                name=f"{entry['id']}. {title}",
                value=content,
                inline=False
            )

        await ctx.send(embed=embed)

    @commands.command()
    async def search(self, ctx: commands.Context, *, query: str) -> None:
        """エントリーを検索"""
        entries = self.bot.db.search_entries(query, limit=10)

        if not entries:
            await ctx.send(f"🔍 No results for: {query}")
            return

        embed = discord.Embed(
            title=f"🔍 Search Results: {query}",
            color=discord.Color.purple()
        )

        for entry in entries:
            title = entry["title"] or "Untitled"
            content = entry["content"][:100] + "..." if len(entry["content"]) > 100 else entry["content"]
            embed.add_field(
                name=f"{entry['id']}. {title}",
                value=content,
                inline=False
            )

        await ctx.send(embed=embed)

async def run_discord_bot(token: str) -> None:
    """Discord Botを実行"""
    bot = Erotic_behavior_analyst_agentBot()
    await bot.start(token)

def create_bot(token: str) -> Erotic_behavior_analyst_agentBot:
    """Botインスタンスを作成"""
    return Erotic_behavior_analyst_agentBot(db=None)
