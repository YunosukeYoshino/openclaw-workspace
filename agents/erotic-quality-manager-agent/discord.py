#!/usr/bin/env python3
# erotic-quality-manager-agent Discord ボット

import logging
import discord
from discord.ext import commands

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Erotic_quality_manager_agentDiscordBot(commands.Bot):
    # erotic-quality-manager-agent Discord ボット

    def __init__(self, db):
        # 初期化
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents, help_command=None)
        self.db = db

    async def setup_hook(self):
        # ボット起動時の設定
        await self.add_cog(Erotic_quality_manager_agentCommands(self))

    async def on_ready(self):
        # 準備完了時のイベント
        logger.info("Logged in as %s", self.user.name)


class Erotic_quality_manager_agentCommands(commands.Cog):
    # erotic-quality-manager-agent コマンド

    def __init__(self, bot: commands.Bot):
        # 初期化
        self.bot = bot

    @commands.command(name="erotic_quality_manager_agent")
    async def erotic_quality_manager_agent(self, ctx: commands.Context, action: str = "list", *, args: str = ""):
        # メインコマンド
        if action == "list":
            entries = self.bot.db.list_entries(limit=20)
            if not entries:
                await ctx.send("エントリーがありません")
                return
            embed = discord.Embed(title="Erotic Quality Manager Agent 一覧", color=discord.Color.blue())
            for entry in entries[:10]:
                title = entry.get("title") or "タイトルなし"
                content = entry.get("content", "")[:50]
                embed.add_field(name=f"{title} (ID: {entry['id']})", value=f"{content}...", inline=False)
            await ctx.send(embed=embed)
        elif action == "add":
            if not args:
                await ctx.send(f"使用方法: !erotic_quality_manager_agent add <内容>")
                return
            entry_id = self.bot.db.add_entry(title=None, content=args, status="active", priority=0)
            await ctx.send(f"エントリーを追加しました (ID: {entry_id})")
        elif action == "search":
            if not args:
                await ctx.send(f"使用方法: !erotic_quality_manager_agent search <キーワード>")
                return
            entries = self.bot.db.search_entries(args, limit=10)
            if not entries:
                await ctx.send("一致するエントリーがありません")
                return
            embed = discord.Embed(title=f"「{args}」の検索結果", color=discord.Color.green())
            for entry in entries:
                title = entry.get("title") or "タイトルなし"
                content = entry.get("content", "")[:50]
                embed.add_field(name=f"{title} (ID: {entry['id']})", value=f"{content}...", inline=False)
            await ctx.send(embed=embed)
        else:
            await ctx.send(f"不明なアクションです: {action}\\n使用可能なアクション: list, add, search")

    @commands.command(name="erotic_quality_manager_agent_status")
    async def erotic_quality_manager_agent_status(self, ctx: commands.Context):
        # ステータス確認
        entries = self.bot.db.list_entries(status="active")
        embed = discord.Embed(title="Erotic Quality Manager Agent ステータス", color=discord.Color.gold())
        embed.add_field(name="アクティブエントリー", value=str(len(entries)))
        await ctx.send(embed=embed)

    @commands.command(name="erotic_quality_manager_agent_delete")
    async def erotic_quality_manager_agent_delete(self, ctx: commands.Context, entry_id: int):
        # エントリー削除
        if self.bot.db.delete_entry(entry_id):
            await ctx.send(f"エントリーを削除しました (ID: {entry_id})")
        else:
            await ctx.send(f"エントリーが見つかりません (ID: {entry_id})")
