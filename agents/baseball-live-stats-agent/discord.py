#!/usr/bin/env python3
"""
野球ライブ統計エージェント - Discord Bot Module

Provides real-time statistics during live baseball games
"""

import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional
from pathlib import Path

class Baseball_Live_Stats_AgentDiscord(commands.Cog):
    """野球ライブ統計エージェント Discord Cog"""

    def __init__(self, bot):
        self.bot = bot
        from .db import Baseball_Live_Stats_AgentDB
        self.db = Baseball_Live_Stats_AgentDB()

    def cog_load(self):
        """Cogが読み込まれたとき"""
        print(f"✅ {野球ライブ統計エージェント} Discord Cog の準備完了")

    def cog_unload(self):
        """Cogがアンロードされるとき"""
        print(f"👋 {野球ライブ統計エージェント} Discord Cog をアンロード")

    @commands.Cog.listener()
    async def on_ready(self):
        """Botが起動したとき"""
        print(f"🚀 {野球ライブ統計エージェント} Discord Cog が起動しました！")

    @commands.command(name="help")
    async def cmd_help(self, ctx: commands.Context):
        """ヘルプを表示"""
        embed = discord.Embed(
            title="野球ライブ統計エージェント",
            description="野球ライブ中継中のリアルタイム統計を提供します",
            color=discord.Color.blue()
        )
        commands_text = "\n".join([f"• {cmd}" for cmd in ['stats game <game_id> - Get live game stats', 'stats player <player> - Get player stats', 'stats pitching - Show pitching stats', 'stats batting - Show batting stats']])
        features_text = "\n".join([f"• {feat}" for feat in ['Real-time pitch data', 'Live player statistics', 'Game probability tracking', 'Historical comparison', 'Stat alerts']])
        embed.add_field(name="📋 コマンド", value=commands_text, inline=False)
        embed.add_field(name="🎯 主な機能", value=features_text, inline=False)
        embed.set_footer(text="baseball live stats")
        await ctx.send(embed=embed)

    @commands.command(name="stats")
    async def cmd_stats(self, ctx: commands.Context):
        """統計を表示"""
        stats = self.db.get_stats()
        embed = discord.Embed(title="📊 データベース統計", color=discord.Color.green())
        for key, value in stats.items():
            embed.add_field(name=key.capitalize(), value=str(value), inline=True)
        await ctx.send(embed=embed)

    @commands.command(name="add")
    async def cmd_add(self, ctx: commands.Context, title: str, *, content: str):
        """エントリーを追加"""
        entry_id = self.db.add_entry(title, content)
        embed = discord.Embed(
            title="✅ エントリー追加",
            description=f"ID: {entry_id}",
            color=discord.Color.green()
        )
        embed.add_field(name="タイトル", value=title, inline=False)
        embed.add_field(name="内容", value=content[:500], inline=False)
        await ctx.send(embed=embed)

    @commands.command(name="list")
    async def cmd_list(self, ctx: commands.Context, entry_type: Optional[str] = None, limit: int = 10):
        """エントリーを一覧表示"""
        entries = self.db.list_entries(entry_type=entry_type, limit=limit)
        if not entries:
            embed = discord.Embed(
                title="📋 エントリー一覧",
                description="エントリーが見つかりません",
                color=discord.Color.orange()
            )
            await ctx.send(embed=embed)
            return
        embed = discord.Embed(title=f"📋 エントリー一覧 ({len(entries)}件)", color=discord.Color.blue())
        for entry in entries[:10]:
            title = entry['title'][:50] + "..." if len(entry['title']) > 50 else entry['title']
            embed.add_field(
                name=f"ID {entry['id']}: {title}",
                value=f"Type: {entry['type']} | Created: {entry['created_at']}",
                inline=False
            )
        await ctx.send(embed=embed)

    @commands.command(name="search")
    async def cmd_search(self, ctx: commands.Context, query: str):
        """エントリーを検索"""
        entries = self.db.list_entries()
        filtered = [e for e in entries if query.lower() in e['title'].lower() or query.lower() in e['content'].lower()]
        if not filtered:
            embed = discord.Embed(
                title="🔍 検索結果",
                description=f"「{query}」に一致するエントリーが見つかりません",
                color=discord.Color.orange()
            )
            await ctx.send(embed=embed)
            return
        embed = discord.Embed(title=f"🔍 検索結果: {query} ({len(filtered)}件)", color=discord.Color.blue())
        for entry in filtered[:10]:
            title = entry['title'][:50] + "..." if len(entry['title']) > 50 else entry['title']
            embed.add_field(
                name=f"ID {entry['id']}: {title}",
                value=f"Type: {entry['type']}",
                inline=False
            )
        await ctx.send(embed=embed)

async def setup(bot):
    """Cogをセットアップ"""
    await bot.add_cog(Baseball_Live_Stats_AgentDiscord(bot))
    print(f"✅ {野球ライブ統計エージェント} Discord Cog をセットアップしました")

def main():
    """メイン関数"""
    print("野球ライブ統計エージェント Discord Bot Module")
    print("Use this module as a Cog in your Discord bot")

if __name__ == "__main__":
    main()
