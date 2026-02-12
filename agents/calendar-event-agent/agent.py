#!/usr/bin/env python3
"""
Calendar Event Agent - カレンダーイベント管理エージェント
Calendar Event Agent - Manage calendar events
"""

import discord
from discord.ext import commands
from db import CalendarEventDatabase

class CalendarEventAgent(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix='!', intents=intents)
        self.db = CalendarEventDatabase()

    async def setup_hook(self):
        await self.add_command(self.add_event)
        await self.add_command(self.list_events)
        await self.add_command(self.show_event)
        await self.add_command(self.update_event)
        await self.add_command(self.delete_event)

    @commands.command(name='add-event')
    async def add_event(self, ctx, *, args: str):
        """イベントを追加 / Add an event"""
        try:
            parts = args.split('|', 6)
            if len(parts) < 3:
                await ctx.send("使い方: !add-event タイトル|開始日時|終了日時|場所|説明|カテゴリ|参加者\nUsage: !add-event title|start_time|end_time|location|description|category|attendees")
                return

            title = parts[0].strip()
            start_time = parts[1].strip()
            end_time = parts[2].strip() if len(parts) > 2 else ""
            location = parts[3].strip() if len(parts) > 3 else ""
            description = parts[4].strip() if len(parts) > 4 else ""
            category = parts[5].strip() if len(parts) > 5 else ""
            attendees = parts[6].strip() if len(parts) > 6 else ""

            record = {
                'title': title,
                'start_time': start_time,
                'end_time': end_time,
                'location': location,
                'description': description,
                'category': category,
                'attendees': attendees
            }

            self.db.add_event(record)
            await ctx.send(f"📅 イベントを追加しました！\n{title}\nEvent added! (ID: {record['id']})")
        except Exception as e:
            await ctx.send(f"❌ エラーが発生しました: {e}\nError occurred: {e}")

    @commands.command(name='list-events')
    async def list_events(self, ctx, category: str = None):
        """イベントを一覧表示 / List events"""
        try:
            events = self.db.get_all_events()

            if not events:
                await ctx.send("イベントが見つかりませんでした。\nNo events found.")
                return

            if category:
                events = [e for e in events if e.get('category') == category]

            response = "📅 イベントリスト / Event List\n\n"
            for e in events:
                response += f"📅 **{e['title']}** (ID: {e['id']})\n"
                response += f"   開始: {e['start_time']}\n"
                if e.get('end_time'):
                    response += f"   終了: {e['end_time']}\n"
                if e.get('location'):
                    response += f"   場所: {e['location']}\n"
                response += f"   作成: {e['created_at']}\n\n"

            await ctx.send(response[:2000])
        except Exception as e:
            await ctx.send(f"❌ エラーが発生しました: {e}\nError occurred: {e}")

    @commands.command(name='show-event')
    async def show_event(self, ctx, event_id: int):
        """イベントの詳細を表示 / Show event details"""
        try:
            event = self.db.get_event(event_id)

            if not event:
                await ctx.send(f"イベントが見つかりません (ID: {event_id})\nEvent not found (ID: {event_id})")
                return

            response = f"📅 **{event['title']}** (ID: {event['id']})\n\n"
            response += f"開始 / Start: {event['start_time']}\n"
            if event.get('end_time'):
                response += f"終了 / End: {event['end_time']}\n"
            if event.get('location'):
                response += f"場所 / Location: {event['location']}\n"
            if event.get('category'):
                response += f"カテゴリ / Category: {event['category']}\n"
            if event.get('description'):
                response += f"説明 / Description: {event['description']}\n"
            if event.get('attendees'):
                response += f"参加者 / Attendees: {event['attendees']}\n"
            response += f"作成日 / Created: {event['created_at']}"

            await ctx.send(response)
        except Exception as e:
            await ctx.send(f"❌ エラーが発生しました: {e}\nError occurred: {e}")

    @commands.command(name='update-event')
    async def update_event(self, ctx, event_id: int, *, args: str):
        """イベントを更新 / Update an event"""
        try:
            parts = args.split('|', 6)
            updates = {}
            if len(parts) > 0 and parts[0].strip():
                updates['title'] = parts[0].strip()
            if len(parts) > 1 and parts[1].strip():
                updates['start_time'] = parts[1].strip()
            if len(parts) > 2 and parts[2].strip():
                updates['end_time'] = parts[2].strip()
            if len(parts) > 3 and parts[3].strip():
                updates['location'] = parts[3].strip()
            if len(parts) > 4 and parts[4].strip():
                updates['description'] = parts[4].strip()
            if len(parts) > 5 and parts[5].strip():
                updates['category'] = parts[5].strip()
            if len(parts) > 6 and parts[6].strip():
                updates['attendees'] = parts[6].strip()

            self.db.update_event(event_id, updates)
            await ctx.send(f"✅ イベントを更新しました (ID: {event_id})\nEvent updated (ID: {event_id})")
        except Exception as e:
            await ctx.send(f"❌ エラーが発生しました: {e}\nError occurred: {e}")

    @commands.command(name='delete-event')
    async def delete_event(self, ctx, event_id: int):
        """イベントを削除 / Delete an event"""
        try:
            self.db.delete_event(event_id)
            await ctx.send(f"🗑️ イベントを削除しました (ID: {event_id})\nEvent deleted (ID: {event_id})")
        except Exception as e:
            await ctx.send(f"❌ エラーが発生しました: {e}\nError occurred: {e}")

if __name__ == '__main__':
    bot = CalendarEventAgent()
    import os
    token = os.getenv('DISCORD_BOT_TOKEN')
    bot.run(token)
