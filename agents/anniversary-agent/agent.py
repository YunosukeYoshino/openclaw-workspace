#!/usr/bin/env python3
"""
Anniversary Agent - 記念日管理エージェント
Anniversary Agent - Manage anniversaries and celebrations
"""

import discord
from discord.ext import commands
from db import anniversary_agentDB

class AnniversaryAgent(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix='!', intents=intents)
        self.db = anniversary_agentDB()

    async def setup_hook(self):
        await self.add_command(self.add_anniversary)
        await self.add_command(self.list_anniversaries)
        await self.add_command(self.show_anniversary)
        await self.add_command(self.delete_anniversary)
        await self.add_command(self.upcoming)

    @commands.command(name='add-anniversary')
    async def add_anniversary(self, ctx, *, args: str):
        """記念日を追加 / Add an anniversary"""
        try:
            parts = args.split('|', 3)
            if len(parts) < 3:
                await ctx.send("使い方: !add-anniversary 名前|日付|説明|リマインダー日前\nUsage: !add-anniversary name|date|description|reminder_days")
                return

            name = parts[0].strip()
            date = parts[1].strip()
            description = parts[2].strip() if len(parts) > 2 else ""
            reminder_days = int(parts[3].strip()) if len(parts) > 3 else 7

            record = {
                'name': name,
                'date': date,
                'description': description,
                'reminder_days': reminder_days
            }

            self.db.add_record(record)
            await ctx.send(f"✅ 記念日を追加しました！\n{name} - {date}\nAnniversary added! (ID: {record['id']})")
        except Exception as e:
            await ctx.send(f"❌ エラーが発生しました: {e}\nError occurred: {e}")

    @commands.command(name='list-anniversaries')
    async def list_anniversaries(self, ctx):
        """記念日を一覧表示 / List anniversaries"""
        try:
            records = self.db.get_all_records()

            if not records:
                await ctx.send("記念日が見つかりませんでした。\nNo anniversaries found.")
                return

            response = "📅 記念日リスト / Anniversary List\n\n"
            for r in records:
                response += f"🎊 **{r['name']}** - {r['date']}\n"
                if r.get('description'):
                    response += f"   {r['description'][:50]}...\n"
                response += f"   リマインダー: {r.get('reminder_days', 7)}日前\n\n"

            await ctx.send(response[:2000])
        except Exception as e:
            await ctx.send(f"❌ エラーが発生しました: {e}\nError occurred: {e}")

    @commands.command(name='show-anniversary')
    async def show_anniversary(self, ctx, anniversary_id: int):
        """記念日の詳細を表示 / Show anniversary details"""
        try:
            record = self.db.get_record(anniversary_id)

            if not record:
                await ctx.send(f"記念日が見つかりません (ID: {anniversary_id})\nAnniversary not found (ID: {anniversary_id})")
                return

            response = f"🎊 **{record['name']}**\n"
            response += f"日付 / Date: {record['date']}\n"
            if record.get('description'):
                response += f"説明 / Description: {record['description']}\n"
            response += f"リマインダー / Reminder: {record.get('reminder_days', 7)}日前\n"
            response += f"作成日 / Created: {record['created_at']}"

            await ctx.send(response)
        except Exception as e:
            await ctx.send(f"❌ エラーが発生しました: {e}\nError occurred: {e}")

    @commands.command(name='delete-anniversary')
    async def delete_anniversary(self, ctx, anniversary_id: int):
        """記念日を削除 / Delete an anniversary"""
        try:
            self.db.delete_record(anniversary_id)
            await ctx.send(f"🗑️ 記念日を削除しました (ID: {anniversary_id})\nAnniversary deleted (ID: {anniversary_id})")
        except Exception as e:
            await ctx.send(f"❌ エラーが発生しました: {e}\nError occurred: {e}")

    @commands.command(name='upcoming-anniversaries')
    async def upcoming(self, ctx, days: int = 30):
        """近日の記念日を表示 / Show upcoming anniversaries"""
        try:
            await ctx.send(f"📅 近日の記念日（{days}日以内）/ Upcoming anniversaries (within {days} days)\n\nこの機能は実装中です...")
        except Exception as e:
            await ctx.send(f"❌ エラーが発生しました: {e}\nError occurred: {e}")

if __name__ == '__main__':
    bot = AnniversaryAgent()
    import os
    token = os.getenv('DISCORD_BOT_TOKEN')
    bot.run(token)
