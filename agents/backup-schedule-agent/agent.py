#!/usr/bin/env python3
"""
Backup Schedule Agent - バックアップスケジュールエージェント
Backup Schedule Agent - Manage backup schedules and jobs
"""

import discord
from discord.ext import commands
from db import BackupScheduleDB

class BackupScheduleAgent(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix='!', intents=intents)
        self.db = BackupScheduleDB()

    async def setup_hook(self):
        await self.add_command(self.add_schedule)
        await self.add_command(self.list_schedules)
        await self.add_command(self.show_schedule)
        await self.add_command(self.enable_schedule)
        await self.add_command(self.disable_schedule)
        await self.add_command(self.run_backup)
        await self.add_command(self.list_jobs)
        await self.add_command(self.list_logs)
        await self.add_command(self.stats)

    @commands.command(name='add-schedule')
    async def add_schedule(self, ctx, *, args: str):
        """スケジュールを追加 / Add a schedule"""
        try:
            parts = args.split('|', 7)
            if len(parts) < 4:
                await ctx.send("使い方: !add-schedule 名前|タイプ|パス|スケジュールタイプ|スケジュール値|バックアップタイプ|圧縮|保存日数\nUsage: !add-schedule name|type|path|schedule_type|schedule_value|backup_type|compress|retention_days")
                return

            name = parts[0].strip()
            target_type = parts[1].strip()
            path = parts[2].strip()
            schedule_type = parts[3].strip()
            schedule_value = parts[4].strip() if len(parts) > 4 else None
            backup_type = parts[5].strip() if len(parts) > 5 else 'full'
            compress = parts[6].strip().lower() == 'true' if len(parts) > 6 else True
            retention_days = int(parts[7].strip()) if len(parts) > 7 else 30

            schedule_id = self.db.add_schedule(name, target_type, path, schedule_type,
                                               schedule_value, backup_type, compress, retention_days)

            await ctx.send(f"✅ スケジュールを追加しました！ (ID: {schedule_id})\nSchedule added! (ID: {schedule_id})")
        except Exception as e:
            await ctx.send(f"❌ エラーが発生しました: {e}\nError occurred: {e}")

    @commands.command(name='list-schedules')
    async def list_schedules(self, ctx):
        """スケジュールを一覧表示 / List schedules"""
        try:
            schedules = self.db.get_all_schedules(enabled_only=False)

            if not schedules:
                await ctx.send("スケジュールが見つかりませんでした。\nNo schedules found.")
                return

            response = "📅 スケジュールリスト / Schedule List\n\n"
            for s in schedules:
                status = "✅" if s['enabled'] else "❌"
                response += f"{status} **{s['name']}** (ID: {s['id']})\n"
                response += f"   タイプ: {s['target_type']} | {s['schedule_type']}\n"
                response += f"   パス: {s['path']}\n\n"

            await ctx.send(response[:2000])
        except Exception as e:
            await ctx.send(f"❌ エラーが発生しました: {e}\nError occurred: {e}")

    @commands.command(name='show-schedule')
    async def show_schedule(self, ctx, schedule_id: int):
        """スケジュールの詳細を表示 / Show schedule details"""
        try:
            schedule = self.db.get_schedule(schedule_id)

            if not schedule:
                await ctx.send(f"スケジュールが見つかりません (ID: {schedule_id})\nSchedule not found (ID: {schedule_id})")
                return

            status = "有効 / Enabled" if schedule['enabled'] else "無効 / Disabled"

            response = f"📅 **{schedule['name']}** (ID: {schedule['id']})\n"
            response += f"タイプ / Type: {schedule['target_type']}\n"
            response += f"パス / Path: {schedule['path']}\n"
            response += f"スケジュール / Schedule: {schedule['schedule_type']}"
            if schedule['schedule_value']:
                response += f" {schedule['schedule_value']}"
            response += "\n"
            response += f"バックアップタイプ / Backup Type: {schedule['backup_type']}\n"
            response += f"圧縮 / Compress: {schedule['compress']}\n"
            response += f"保存日数 / Retention: {schedule['retention_days']}日\n"
            response += f"ステータス / Status: {status}\n"
            response += f"作成日 / Created: {schedule['created_at']}"

            await ctx.send(response)
        except Exception as e:
            await ctx.send(f"❌ エラーが発生しました: {e}\nError occurred: {e}")

    @commands.command(name='enable-schedule')
    async def enable_schedule(self, ctx, schedule_id: int):
        """スケジュールを有効化 / Enable a schedule"""
        try:
            self.db.update_schedule(schedule_id, enabled=True)
            await ctx.send(f"✅ スケジュールを有効にしました (ID: {schedule_id})\nSchedule enabled (ID: {schedule_id})")
        except Exception as e:
            await ctx.send(f"❌ エラーが発生しました: {e}\nError occurred: {e}")

    @commands.command(name='disable-schedule')
    async def disable_schedule(self, ctx, schedule_id: int):
        """スケジュールを無効化 / Disable a schedule"""
        try:
            self.db.update_schedule(schedule_id, enabled=False)
            await ctx.send(f"❌ スケジュールを無効にしました (ID: {schedule_id})\nSchedule disabled (ID: {schedule_id})")
        except Exception as e:
            await ctx.send(f"❌ エラーが発生しました: {e}\nError occurred: {e}")

    @commands.command(name='run-backup')
    async def run_backup(self, ctx, schedule_id: int):
        """バックアップを実行 / Run backup"""
        try:
            job_id = self.db.add_job(schedule_id)
            await ctx.send(f"🔄 バックアップジョブを開始しました (ID: {job_id})\nBackup job started (ID: {job_id})")
        except Exception as e:
            await ctx.send(f"❌ エラーが発生しました: {e}\nError occurred: {e}")

    @commands.command(name='list-jobs')
    async def list_jobs(self, ctx, schedule_id: int = None, limit: int = 10):
        """ジョブを一覧表示 / List jobs"""
        try:
            jobs = self.db.get_jobs(schedule_id=schedule_id, limit=limit)

            if not jobs:
                await ctx.send("ジョブが見つかりませんでした。\nNo jobs found.")
                return

            response = "📋 ジョブリスト / Job List\n\n"
            for j in jobs:
                status_emoji = "✅" if j['success'] else "❌"
                response += f"{status_emoji} **Job {j['id']}** - {j['status']}\n"
                response += f"   スケジュールID: {j['schedule_id']}\n"
                if j['completed_at']:
                    response += f"   完了: {j['completed_at']}\n"
                if j['backup_size']:
                    response += f"   サイズ: {j['backup_size']} bytes\n"
                response += f"   開始: {j['started_at']}\n\n"

            await ctx.send(response[:2000])
        except Exception as e:
            await ctx.send(f"❌ エラーが発生しました: {e}\nError occurred: {e}")

    @commands.command(name='list-logs')
    async def list_logs(self, ctx, schedule_id: int = None, limit: int = 10):
        """ログを一覧表示 / List logs"""
        try:
            logs = self.db.get_logs(schedule_id=schedule_id, limit=limit)

            if not logs:
                await ctx.send("ログが見つかりませんでした。\nNo logs found.")
                return

            response = "📝 ログ / Logs\n\n"
            for l in logs:
                emoji = {"info": "ℹ️", "warning": "⚠️", "error": "❌", "debug": "🔍"}.get(l['log_level'], "📄")
                response += f"{emoji} **{l['log_level'].upper()}** - {l['message']}\n"
                if l['schedule_id']:
                    response += f"   スケジュールID: {l['schedule_id']}\n"
                response += f"   時間: {l['timestamp']}\n\n"

            await ctx.send(response[:2000])
        except Exception as e:
            await ctx.send(f"❌ エラーが発生しました: {e}\nError occurred: {e}")

    @commands.command(name='backup-stats')
    async def stats(self, ctx):
        """統計情報を表示 / Show statistics"""
        try:
            schedules = self.db.get_all_schedules()
            jobs = self.db.get_jobs(limit=100)

            enabled = sum(1 for s in schedules if s['enabled'])
            success = sum(1 for j in jobs if j['success'])
            failed = sum(1 for j in jobs if not j['success'])

            response = "📊 統計情報 / Statistics\n\n"
            response += f"スケジュール / Schedules:\n"
            response += f"  総数 / Total: {len(schedules)}\n"
            response += f"  有効 / Enabled: {enabled}\n"
            response += f"  無効 / Disabled: {len(schedules) - enabled}\n"
            response += f"\nジョブ / Jobs:\n"
            response += f"  総数 / Total: {len(jobs)}\n"
            response += f"  成功 / Success: {success}\n"
            response += f"  失敗 / Failed: {failed}"

            await ctx.send(response)
        except Exception as e:
            await ctx.send(f"❌ エラーが発生しました: {e}\nError occurred: {e}")

if __name__ == '__main__':
    bot = BackupScheduleAgent()
    import os
    token = os.getenv('DISCORD_BOT_TOKEN')
    bot.run(token)
