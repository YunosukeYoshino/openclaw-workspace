#!/usr/bin/env python3
"""
Calendar Integration Agent - カレンダー連携エージェント
Calendar Integration Agent - Integrate with external calendars
"""

import discord
from discord.ext import commands
from db import CalendarIntegrationDB

class CalendarIntegrationAgent(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix='!', intents=intents)
        self.db = CalendarIntegrationDB()

    async def setup_hook(self):
        await self.add_command(self.add_source)
        await self.add_command(self.list_sources)
        await self.add_command(self.show_source)
        await self.add_command(self.enable_source)
        await self.add_command(self.disable_source)
        await self.add_command(self.sync)
        await self.add_command(self.sync_logs)
        await self.add_command(self.synced_events)

    @commands.command(name='add-calendar-source')
    async def add_source(self, ctx, *, args: str):
        """カレンダーソースを追加 / Add a calendar source"""
        try:
            parts = args.split('|', 2)
            if len(parts) < 2:
                await ctx.send("使い方: !add-calendar-source 名前|タイプ|設定\nUsage: !add-calendar-source name|type|config")
                return

            name = parts[0].strip()
            source_type = parts[1].strip()
            config = parts[2].strip() if len(parts) > 2 else ""

            source_id = self.db.add_source(name, source_type, config)

            await ctx.send(f"✅ カレンダーソースを追加しました！ (ID: {source_id})\nCalendar source added! (ID: {source_id})")
        except Exception as e:
            await ctx.send(f"❌ エラーが発生しました: {e}\nError occurred: {e}")

    @commands.command(name='list-calendar-sources')
    async def list_sources(self, ctx):
        """カレンダーソースを一覧表示 / List calendar sources"""
        try:
            sources = self.db.get_all_sources()

            if not sources:
                await ctx.send("カレンダーソースが見つかりませんでした。\nNo calendar sources found.")
                return

            response = "📅 カレンダーソースリスト / Calendar Source List\n\n"
            for s in sources:
                status = "✅" if s['enabled'] else "❌"
                response += f"{status} **{s['name']}** (ID: {s['id']})\n"
                response += f"   タイプ: {s['source_type']}\n"
                if s['last_sync']:
                    response += f"   最後の同期: {s['last_sync']}\n"
                response += f"   作成: {s['created_at']}\n\n"

            await ctx.send(response[:2000])
        except Exception as e:
            await ctx.send(f"❌ エラーが発生しました: {e}\nError occurred: {e}")

    @commands.command(name='show-calendar-source')
    async def show_source(self, ctx, source_id: int):
        """カレンダーソースの詳細を表示 / Show calendar source details"""
        try:
            source = self.db.get_source(source_id)

            if not source:
                await ctx.send(f"カレンダーソースが見つかりません (ID: {source_id})\nCalendar source not found (ID: {source_id})")
                return

            status = "有効 / Enabled" if source['enabled'] else "無効 / Disabled"

            response = f"📅 **{source['name']}** (ID: {source['id']})\n"
            response += f"タイプ / Type: {source['source_type']}\n"
            response += f"ステータス / Status: {status}\n"
            if source['last_sync']:
                response += f"最後の同期 / Last Sync: {source['last_sync']}\n"
            response += f"作成日 / Created: {source['created_at']}"

            await ctx.send(response)
        except Exception as e:
            await ctx.send(f"❌ エラーが発生しました: {e}\nError occurred: {e}")

    @commands.command(name='enable-calendar-source')
    async def enable_source(self, ctx, source_id: int):
        """カレンダーソースを有効化 / Enable a calendar source"""
        try:
            self.db.update_source(source_id, enabled=True)
            await ctx.send(f"✅ カレンダーソースを有効にしました (ID: {source_id})\nCalendar source enabled (ID: {source_id})")
        except Exception as e:
            await ctx.send(f"❌ エラーが発生しました: {e}\nError occurred: {e}")

    @commands.command(name='disable-calendar-source')
    async def disable_source(self, ctx, source_id: int):
        """カレンダーソースを無効化 / Disable a calendar source"""
        try:
            self.db.update_source(source_id, enabled=False)
            await ctx.send(f"❌ カレンダーソースを無効にしました (ID: {source_id})\nCalendar source disabled (ID: {source_id})")
        except Exception as e:
            await ctx.send(f"❌ エラーが発生しました: {e}\nError occurred: {e}")

    @commands.command(name='sync-calendar')
    async def sync(self, ctx, source_id: int):
        """カレンダーを同期 / Sync calendar"""
        try:
            log_id = self.db.add_sync_log(source_id, 'started')
            await ctx.send(f"🔄 カレンダー同期を開始しました (ID: {log_id})\nCalendar sync started (ID: {log_id})")
        except Exception as e:
            await ctx.send(f"❌ エラーが発生しました: {e}\nError occurred: {e}")

    @commands.command(name='sync-logs')
    async def sync_logs(self, ctx, source_id: int = None, limit: int = 10):
        """同期ログを表示 / Show sync logs"""
        try:
            logs = self.db.get_sync_logs(source_id=source_id, limit=limit)

            if not logs:
                await ctx.send("同期ログが見つかりませんでした。\nNo sync logs found.")
                return

            response = "📝 同期ログ / Sync Logs\n\n"
            for l in logs:
                status_emoji = {"completed": "✅", "started": "🔄", "failed": "❌"}.get(l['status'], "📄")
                response += f"{status_emoji} **Log {l['id']}** - {l['status']}\n"
                response += f"   ソースID: {l['source_id']}\n"
                if l['events_synced']:
                    response += f"   同期イベント: {l['events_synced']}\n"
                if l['error_message']:
                    response += f"   エラー: {l['error_message']}\n"
                response += f"   時間: {l['sync_timestamp']}\n\n"

            await ctx.send(response[:2000])
        except Exception as e:
            await ctx.send(f"❌ エラーが発生しました: {e}\nError occurred: {e}")

    @commands.command(name='synced-events')
    async def synced_events(self, ctx, source_id: int = None):
        """同期イベントを表示 / Show synced events"""
        try:
            events = self.db.get_synced_events(source_id=source_id)

            if not events:
                await ctx.send("同期イベントが見つかりませんでした。\nNo synced events found.")
                return

            response = "📅 同期イベント / Synced Events\n\n"
            for e in events:
                response += f"📅 **{e['title']}**\n"
                response += f"   外部ID: {e['external_event_id']}\n"
                response += f"   開始: {e['start_time']}\n"
                if e['end_time']:
                    response += f"   終了: {e['end_time']}\n"
                response += f"   同期: {e['synced_at']}\n\n"

            await ctx.send(response[:2000])
        except Exception as e:
            await ctx.send(f"❌ エラーが発生しました: {e}\nError occurred: {e}")

if __name__ == '__main__':
    bot = CalendarIntegrationAgent()
    import os
    token = os.getenv('DISCORD_BOT_TOKEN')
    bot.run(token)
