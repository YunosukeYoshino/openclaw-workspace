#!/usr/bin/env python3
"""
家事管理エージェント
Household Management Agent
Discordボットによる家事・メンテナンス管理
"""

import discord
from discord.ext import commands
import re
from datetime import datetime
from db import HouseholdDatabase


class HouseholdAgent(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = HouseholdDatabase()

    @commands.command(aliases=['addchore', '家事追加', 'タスク追加'])
    async def add_chore(self, ctx, *, message: str = None):
        """家事タスクを追加 / Add chore"""
        if not message:
            await ctx.send("```\n使用方法: !addchore <タスク名> <カテゴリ> [詳細]\n例: !addchore 掃除 毎週 日曜:掃除機 洗濉機\n```")
            return

        parts = message.split()
        name = parts[0]

        category = None
        for part in parts[1:]:
            if part in ['掃除', '洗濯', '料理', '買い物', '片付け', 'クリーニング',
                        'cleaning', 'laundry', 'cooking', 'shopping', 'organizing']:
                category = part
                break

        if not category:
            category = 'その他'

        kwargs = {'notes': message}
        freq_match = re.search(r'(毎週|毎日|毎月|weekly|daily|monthly)', message.lower())
        if freq_match:
            kwargs['frequency'] = freq_match.group(1)
            kwargs['recurring'] = True

        priority_match = re.search(r'(優先度|priority)[:：]\s*(高|中|低|high|medium|low)', message.lower())
        if priority_match:
            p = priority_match.group(2)
            kwargs['priority'] = 'high' if p in ['高', 'high'] else ('low' if p in ['低', 'low'] else 'medium')

        try:
            chore_id = self.db.add_chore(name, category, **kwargs)
            await ctx.send(f"✅ 家事タスクを追加しました\nID: {chore_id}\n名前: {name}\nカテゴリ: {category}")
        except Exception as e:
            await ctx.send(f"❌ エラー: {e}")

    @commands.command(aliases=['listchores', '家事一覧', 'タスク一覧'])
    async def list_chores(self, ctx):
        """家事一覧を表示 / List chores"""
        chores = self.db.get_chores(status='pending')

        if not chores:
            await ctx.send("📭 未完了の家事はありません")
            return

        msg = "🏠 **未完了の家事タスク**\n\n"
        for chore in chores[:15]:
            priority_emoji = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}.get(chore['priority'], '⚪')
            recurring = " 🔁" if chore['recurring'] else ""
            msg += f"{priority_emoji} {chore['name']} ({chore['category']}){recurring}\n"

        if len(chores) > 15:
            msg += f"\n...他 {len(chores) - 15} 件"

        await ctx.send(msg)

    @commands.command(aliases=['complete', '完了', 'done'])
    async def complete_chore(self, ctx, chore_id: int = None):
        """家事を完了にする / Complete chore"""
        if not chore_id:
            await ctx.send("❌ タスクIDを指定してください")
            return

        if self.db.complete_chore(chore_id):
            await ctx.send(f"✅ タスクID {chore_id} を完了にしました")
        else:
            await ctx.send("❌ タスクが見つかりません")

    @commands.command(aliases=['maintenance', 'メンテナンス'])
    async def add_maintenance(self, ctx, *, message: str = None):
        """メンテナンスを追加 / Add maintenance"""
        if not message:
            await ctx.send("```\n使用方法: !maintenance <アイテム> <種類> [詳細]\n例: !maintenance エアコン 点検 毎年5月\n```")
            return

        parts = message.split()
        item = parts[0]
        type_ = parts[1] if len(parts) > 1 else '点検'

        kwargs = {'notes': message}
        date_match = re.search(r'(\d{4}-\d{2}-\d{2}|\d{1,2}/\d{1,2})', message)
        if date_match:
            kwargs['scheduled_date'] = date_match.group(0)

        try:
            maint_id = self.db.add_maintenance(item, type_, **kwargs)
            await ctx.send(f"✅ メンテナンスを追加しました\nID: {maint_id}\nアイテム: {item}\n種類: {type_}")
        except Exception as e:
            await ctx.send(f"❌ エラー: {e}")

    @commands.command(aliases=['listmaintenance', 'メンテ一覧'])
    async def list_maintenance(self, ctx):
        """メンテナンス一覧を表示 / List maintenance"""
        items = self.db.get_maintenance(status='scheduled')

        if not items:
            await ctx.send("📭 予定されたメンテナンスはありません")
            return

        msg = "🔧 **メンテナンス予定**\n\n"
        for item in items:
            date = item['scheduled_date'] or "未設定"
            msg += f"• {item['item']} - {item['type']} ({date})\n"

        await ctx.send(msg)

    @commands.command(aliases=['stats', '統計'])
    async def show_stats(self, ctx):
        """統計情報を表示 / Show statistics"""
        summary = self.db.get_summary()

        msg = "📊 **家事管理統計**\n\n"
        msg += f"📋 未完了タスク: {summary['pending_chores']} 件\n"
        msg += f"🔧 メンテナンス予定: {summary['scheduled_maintenance']} 件\n"
        msg += f"🪑 家具・備品: {summary['total_furniture']} 点\n"

        await ctx.send(msg)

    @commands.command(aliases=['help', 'help_household'])
    async def household_help(self, ctx):
        """ヘルプを表示 / Show help"""
        help_text = """
🏠 **家事管理エージェント ヘルプ**

**タスク管理:**
  `!addchore <名前> [カテゴリ]` - 家事タスク追加
  `!listchores` - 未完了タスク一覧
  `!complete <ID>` - タスク完了

**メンテナンス:**
  `!maintenance <アイテム> <種類>` - メンテナンス追加
  `!listmaintenance` - メンテナンス一覧

**その他:**
  `!stats` - 統計情報
        """
        await ctx.send(help_text)


def setup(bot):
    bot.add_cog(HouseholdAgent(bot))
