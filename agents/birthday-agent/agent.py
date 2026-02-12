#!/usr/bin/env python3
"""
Birthday Agent - 誕生日管理エージェント
Birthday Agent - Track and manage birthdays
"""

import discord
from discord.ext import commands
from db import birthday_agentDB

class BirthdayAgent(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix='!', intents=intents)
        self.db = birthday_agentDB()

    async def setup_hook(self):
        await self.add_command(self.add_birthday)
        await self.add_command(self.list_birthdays)
        await self.add_command(self.show_birthday)
        await self.add_command(self.update_birthday)
        await self.add_command(self.delete_birthday)
        await self.add_command(self.upcoming)

    @commands.command(name='add-birthday')
    async def add_birthday(self, ctx, *, args: str):
        """誕生日を追加 / Add a birthday"""
        try:
            parts = args.split('|', 4)
            if len(parts) < 3:
                await ctx.send("使い方: !add-birthday 名前|日付|メモ|関係|リマインダー日前\nUsage: !add-birthday name|date|notes|relationship|reminder_days")
                return

            name = parts[0].strip()
            date = parts[1].strip()
            notes = parts[2].strip() if len(parts) > 2 else ""
            relationship = parts[3].strip() if len(parts) > 3 else ""
            reminder_days = int(parts[4].strip()) if len(parts) > 4 else 7

            record = {
                'name': name,
                'date': date,
                'notes': notes,
                'relationship': relationship,
                'reminder_days': reminder_days
            }

            self.db.add_record(record)
            await ctx.send(f"🎂 誕生日を追加しました！\n{name} - {date}\nBirthday added! (ID: {record['id']})")
        except Exception as e:
            await ctx.send(f"❌ エラーが発生しました: {e}\nError occurred: {e}")

    @commands.command(name='list-birthdays')
    async def list_birthdays(self, ctx):
        """誕生日を一覧表示 / List birthdays"""
        try:
            records = self.db.get_all_records()

            if not records:
                await ctx.send("誕生日が見つかりませんでした。\nNo birthdays found.")
                return

            response = "📅 誕生日リスト / Birthday List\n\n"
            for r in records:
                response += f"🎂 **{r['name']}** - {r['date']}\n"
                if r.get('relationship'):
                    response += f"   関係: {r['relationship']}\n"
                if r.get('notes'):
                    response += f"   {r['notes'][:30]}...\n"
                if r.get('reminder_days'):
                    response += f"   リマインダー: {r['reminder_days']}日前\n"
                response += f"   作成: {r['created_at']}\n\n"

            await ctx.send(response[:2000])
        except Exception as e:
            await ctx.send(f"❌ エラーが発生しました: {e}\nError occurred: {e}")

    @commands.command(name='show-birthday')
    async def show_birthday(self, ctx, birthday_id: int):
        """誕生日の詳細を表示 / Show birthday details"""
        try:
            record = self.db.get_record(birthday_id)

            if not record:
                await ctx.send(f"誕生日が見つかりません (ID: {birthday_id})\nBirthday not found (ID: {birthday_id})")
                return

            response = f"🎂 **{record['name']}**\n"
            response += f"日付 / Date: {record['date']}\n"
            if record.get('relationship'):
                response += f"関係 / Relationship: {record['relationship']}\n"
            if record.get('notes'):
                response += f"メモ / Notes: {record['notes']}\n"
            if record.get('reminder_days'):
                response += f"リマインダー / Reminder: {record['reminder_days']}日前\n"
            response += f"作成日 / Created: {record['created_at']}"

            await ctx.send(response)
        except Exception as e:
            await ctx.send(f"❌ エラーが発生しました: {e}\nError occurred: {e}")

    @commands.command(name='update-birthday')
    async def update_birthday(self, ctx, birthday_id: int, *, args: str):
        """誕生日を更新 / Update a birthday"""
        try:
            parts = args.split('|', 4)
            updates = {}
            if len(parts) > 0 and parts[0].strip():
                updates['name'] = parts[0].strip()
            if len(parts) > 1 and parts[1].strip():
                updates['date'] = parts[1].strip()
            if len(parts) > 2 and parts[2].strip():
                updates['notes'] = parts[2].strip()
            if len(parts) > 3 and parts[3].strip():
                updates['relationship'] = parts[3].strip()
            if len(parts) > 4 and parts[4].strip():
                updates['reminder_days'] = int(parts[4].strip())

            self.db.update_record(birthday_id, updates)
            await ctx.send(f"✅ 誕生日を更新しました (ID: {birthday_id})\nBirthday updated (ID: {birthday_id})")
        except Exception as e:
            await ctx.send(f"❌ エラーが発生しました: {e}\nError occurred: {e}")

    @commands.command(name='delete-birthday')
    async def delete_birthday(self, ctx, birthday_id: int):
        """誕生日を削除 / Delete a birthday"""
        try:
            self.db.delete_record(birthday_id)
            await ctx.send(f"🗑️ 誕生日を削除しました (ID: {birthday_id})\nBirthday deleted (ID: {birthday_id})")
        except Exception as e:
            await ctx.send(f"❌ エラーが発生しました: {e}\nError occurred: {e}")

    @commands.command(name='upcoming-birthdays')
    async def upcoming(self, ctx, days: int = 30):
        """近日の誕生日を表示 / Show upcoming birthdays"""
        try:
            await ctx.send(f"📅 近日の誕生日（{days}日以内）/ Upcoming birthdays (within {days} days)\n\nこの機能は実装中です...")
        except Exception as e:
            await ctx.send(f"❌ エラーが発生しました: {e}\nError occurred: {e}")

if __name__ == '__main__':
    bot = BirthdayAgent()
    import os
    token = os.getenv('DISCORD_BOT_TOKEN')
    bot.run(token)
