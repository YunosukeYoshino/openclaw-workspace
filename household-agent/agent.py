#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Household Agent - Discord Bot
家事管理エージェント - Discord ボット
"""

import discord
from discord.ext import commands
import sqlite3
from datetime import datetime
import os
from db import HouseholdDB

class HouseholdAgent(commands.Bot):
    """Household Management Discord Bot"""

    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix='!hh ', intents=intents)
        self.db = HouseholdDB()

    async def setup_hook(self):
        """Setup hook when bot starts"""
        print(f'{self.user} has connected to Discord!')

    async def on_ready(self):
        """Called when bot is ready"""
        print(f'Logged in as {self.user.name} (ID: {self.user.id})')
        print('------')
        activity = discord.Activity(type=discord.ActivityType.watching, name="household chores")
        await self.change_presence(activity=activity)

    async def on_command_error(self, ctx, error):
        """Handle command errors"""
        if isinstance(error, commands.CommandNotFound):
            return
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"⚠️ 必要な引数が不足しています: {error.param.name}")
        else:
            print(f'Error: {error}')
            await ctx.send("❌ エラーが発生しました。")

# Bot instance
bot = HouseholdAgent()

@bot.command(name='summary', aliases=['概要', 'サマリー'])
async def summary(ctx):
    """Show household summary"""
    summary = bot.db.get_summary()
    embed = discord.Embed(
        title="🏠 家事管理サマリー / Household Summary",
        color=discord.Color.blue()
    )
    embed.add_field(name="📋 未完了の家事 / Pending Chores", value=summary['pending_chores'], inline=True)
    embed.add_field(name="🔧 修理中 / Open Repairs", value=summary['open_repairs'], inline=True)
    embed.add_field(name="📅 今週のメンテナンス / Upcoming Maintenance", value=summary['upcoming_maintenance'], inline=True)
    embed.add_field(name="📦 在庫切れ間近 / Low Stock", value=summary['low_stock_items'], inline=True)
    embed.set_footer(text=f"Requested by {ctx.author.display_name}")
    await ctx.send(embed=embed)

@bot.command(name='chore', aliases=['家事', 'タスク'])
async def add_chore(ctx, name: str, category: str, *, description: str = None):
    """Add a new chore"""
    chore_id = bot.db.add_chore(name, category, description)
    await ctx.send(f"✅ 家事タスクを追加しました (ID: {chore_id}): {name}")

@bot.command(name='chores', aliases=['家事一覧', 'タスク一覧'])
async def list_chores(ctx, status: str = None):
    """List all chores or filter by status"""
    chores = bot.db.get_chores(status=status)

    if not chores:
        await ctx.send("📭 家事タスクがありません。")
        return

    embed = discord.Embed(
        title=f"📋 家事タスク一覧 / Chores ({len(chores)})",
        color=discord.Color.green()
    )

    for chore in chores[:10]:  # Limit to 10
        status_emoji = {
            'pending': '⏳',
            'in_progress': '🔄',
            'completed': '✅',
            'skipped': '⏭️'
        }.get(chore['status'], '❓')

        due_str = chore['due_date'] or '期限なし'
        embed.add_field(
            name=f"{status_emoji} {chore['name']} (優先度: {chore['priority']})",
            value=f"カテゴリ: {chore['category']} | 期限: {due_str}",
            inline=False
        )

    await ctx.send(embed=embed)

@bot.command(name='complete', aliases=['完了', 'finish'])
async def complete_chore(ctx, chore_id: int):
    """Mark a chore as completed"""
    success = bot.db.update_chore_status(chore_id, 'completed')
    if success:
        await ctx.send(f"✅ 家事タスク {chore_id} を完了しました！")
    else:
        await ctx.send(f"❌ 家事タスク {chore_id} が見つかりません。")

@bot.command(name='repair', aliases=['修理', 'rep'])
async def add_repair(ctx, item: str, issue: str, *, description: str = None):
    """Add a new repair record"""
    repair_id = bot.db.add_repair(item, issue, description=description)
    await ctx.send(f"🔧 修理記録を追加しました (ID: {repair_id}): {item} - {issue}")

@bot.command(name='repairs', aliases=['修理一覧'])
async def list_repairs(ctx, status: str = None):
    """List all repairs"""
    repairs = bot.db.get_repairs(status=status)

    if not repairs:
        await ctx.send("📭 修理記録がありません。")
        return

    embed = discord.Embed(
        title=f"🔧 修理一覧 / Repairs ({len(repairs)})",
        color=discord.Color.orange()
    )

    for repair in repairs[:10]:
        severity_color = {
            'minor': '🟢',
            'moderate': '🟡',
            'critical': '🔴'
        }.get(repair['severity'], '⚪')

        status_emoji = {
            'open': '📝',
            'in_progress': '🔨',
            'completed': '✅',
            'cancelled': '❌'
        }.get(repair['status'], '❓')

        embed.add_field(
            name=f"{status_emoji} {repair['item']}",
            value=f"{severity_color} 重要度: {repair['severity']} | 問題: {repair['issue'][:50]}",
            inline=False
        )

    await ctx.send(embed=embed)

@bot.command(name='maintenance', aliases=['メンテナンス', 'maint'])
async def add_maintenance(ctx, item: str, task: str, *, details: str = None):
    """Add a new maintenance task"""
    maint_id = bot.db.add_maintenance(item, task, notes=details)
    await ctx.send(f"📅 メンテナンスタスクを追加しました (ID: {maint_id}): {item} - {task}")

@bot.command(name='maintenances', aliases=['メンテナンス一覧'])
async def list_maintenance(ctx):
    """List all maintenance tasks"""
    tasks = bot.db.get_maintenance()

    if not tasks:
        await ctx.send("📭 メンテナンスタスクがありません。")
        return

    embed = discord.Embed(
        title=f"📅 メンテナンス一覧 / Maintenance ({len(tasks)})",
        color=discord.Color.purple()
    )

    for task in tasks[:10]:
        next_due = task['next_due'] or '未定'
        embed.add_field(
            name=f"🔧 {task['item']}",
            value=f"タスク: {task['task']}\n次回予定: {next_due}",
            inline=False
        )

    await ctx.send(embed=embed)

@bot.command(name='supply', aliases=['用品', '在庫'])
async def add_supply(ctx, name: str, category: str, quantity: int = 0, *, unit: str = None):
    """Add a supply item"""
    supply_id = bot.db.add_supply(name, category, quantity, unit)
    await ctx.send(f"📦 用品を追加しました (ID: {supply_id}): {name} ({quantity}{unit or ''})")

@bot.command(name='supplies', aliases=['用品一覧', '在庫一覧'])
async def list_supplies(ctx, low_stock: bool = False):
    """List all supplies or low stock items"""
    supplies = bot.db.get_supplies(low_stock=low_stock)

    if not supplies:
        await ctx.send("📭 用品がありません。" if not low_stock else "✅ 在庫切れのアイテムはありません。")
        return

    title = "📦 在庫切れ間近 / Low Stock Supplies" if low_stock else "📦 用品一覧 / All Supplies"
    embed = discord.Embed(
        title=f"{title} ({len(supplies)})",
        color=discord.Color.yellow()
    )

    for supply in supplies[:15]:
        status = "⚠️ 在庫少" if supply['quantity'] <= (supply['minimum_quantity'] or 0) else "✅"
        embed.add_field(
            name=f"{status} {supply['name']}",
            value=f"カテゴリ: {supply['category'] or 'N/A'} | 数量: {supply['quantity']}{supply['unit'] or ''}",
            inline=True
        )

    await ctx.send(embed=embed)

@bot.command(name='cleaning', aliases=['掃除'])
async def add_cleaning(ctx, area: str, task: str, frequency: str):
    """Add cleaning task to schedule"""
    task_id = bot.db.add_cleaning_task(area, task, frequency)
    await ctx.send(f"🧹 掃除タスクを追加しました (ID: {task_id}): {area} - {task}")

@bot.command(name='cleanings', aliases=['掃除一覧'])
async def list_cleaning(ctx):
    """List cleaning schedule"""
    tasks = bot.db.get_cleaning_schedule()

    if not tasks:
        await ctx.send("📭 掃除スケジュールがありません。")
        return

    embed = discord.Embed(
        title=f"🧹 掃除スケジュール / Cleaning Schedule ({len(tasks)})",
        color=discord.Color.teal()
    )

    for task in tasks[:10]:
        freq_map = {
            'daily': '毎日',
            'weekly': '毎週',
            'monthly': '毎月'
        }
        embed.add_field(
            name=f"{task['area']}",
            value=f"{task['task']} ({freq_map.get(task['frequency'], task['frequency'])})",
            inline=False
        )

    await ctx.send(embed=embed)

@bot.command(name='help', aliases=['ヘルプ', '使い方'])
async def help_command(ctx):
    """Show help"""
    embed = discord.Embed(
        title="🏠 Household Agent - ヘルプ",
        description="家事管理を簡単に！/ Manage your household easily!",
        color=discord.Color.blue()
    )

    embed.add_field(name="📋 サマリー", value="`!hh summary` - 全体状況を表示", inline=False)
    embed.add_field(name="📝 家事タスク", value="`!hh chore <名前> <カテゴリ>` - タスク追加\n`!hh chores [ステータス]` - タスク一覧\n`!hh complete <ID>` - タスク完了", inline=False)
    embed.add_field(name="🔧 修理", value="`!hh repair <アイテム> <問題>` - 修理追加\n`!hh repairs [ステータス]` - 修理一覧", inline=False)
    embed.add_field(name="📅 メンテナンス", value="`!hh maintenance <アイテム> <タスク>` - 追加\n`!hh maintenances` - 一覧", inline=False)
    embed.add_field(name="📦 用品", value="`!hh supply <名前> <カテゴリ> [数量]` - 追加\n`!hh supplies [low]` - 在庫一覧", inline=False)
    embed.add_field(name="🧹 掃除", value="`!hh cleaning <場所> <タスク> <頻度>` - 追加\n`!hh cleanings` - スケジュール", inline=False)

    embed.set_footer(text="コマンドは `!hh` で始まります")
    await ctx.send(embed=embed)

def main():
    """Run the bot"""
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        print("Error: DISCORD_TOKEN environment variable not set")
        return

    bot.run(token)

if __name__ == '__main__':
    main()
