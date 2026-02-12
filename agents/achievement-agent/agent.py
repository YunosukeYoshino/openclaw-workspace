#!/usr/bin/env python3
"""
Achievement Agent - 実績・達成記録エージェント
Achievement Agent - Track accomplishments and milestones
"""

import discord
from discord.ext import commands
import sqlite3
from datetime import datetime
from pathlib import Path

from db import Database

class AchievementAgent(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix='!', intents=intents)
        self.db = Database()

    async def setup_hook(self):
        await self.add_command(self.add_achievement)
        await self.add_command(self.list_achievements)
        await self.add_command(self.show_achievement)
        await self.add_command(self.complete_achievement)
        await self.add_command(self.delete_achievement)
        await self.add_command(self.stats)

    @commands.command(name='add-achievement')
    async def add_achievement(self, ctx, *, args: str):
        """実績を追加 / Add an achievement"""
        try:
            parts = args.split('|', 2)
            if len(parts) < 2:
                await ctx.send("使い方: !add-achievement タイトル|カテゴリ|説明\nUsage: !add-achievement title|category|description")
                return

            title = parts[0].strip()
            category = parts[1].strip()
            description = parts[2].strip() if len(parts) > 2 else ""

            achievement_id = self.db.add_achievement(
                title=title,
                category=category,
                description=description
            )

            await ctx.send(f"✅ 実績を追加しました！ (ID: {achievement_id})\nAchievement added! (ID: {achievement_id})")
        except Exception as e:
            await ctx.send(f"❌ エラーが発生しました: {e}\nError occurred: {e}")

    @commands.command(name='list-achievements')
    async def list_achievements(self, ctx, category: str = None):
        """実績を一覧表示 / List achievements"""
        try:
            achievements = self.db.get_achievements(category=category)

            if not achievements:
                await ctx.send("実績が見つかりませんでした。\nNo achievements found.")
                return

            response = "📊 実績リスト / Achievement List\n\n"
            for a in achievements:
                status = "✅" if a['completed'] else "⬜"
                response += f"{status} **{a['title']}** [{a['category']}]\n"
                if a['description']:
                    response += f"   {a['description'][:50]}...\n"
                response += f"   作成: {a['created_at']}\n\n"

            await ctx.send(response[:2000])
        except Exception as e:
            await ctx.send(f"❌ エラーが発生しました: {e}\nError occurred: {e}")

    @commands.command(name='show-achievement')
    async def show_achievement(self, ctx, achievement_id: int):
        """実績の詳細を表示 / Show achievement details"""
        try:
            achievement = self.db.get_achievement(achievement_id)

            if not achievement:
                await ctx.send(f"実績が見つかりません (ID: {achievement_id})\nAchievement not found (ID: {achievement_id})")
                return

            status = "✅ 達成 / Completed" if achievement['completed'] else "⬜ 未達成 / Incomplete"

            response = f"🏆 **{achievement['title']}**\n"
            response += f"カテゴリ / Category: {achievement['category']}\n"
            response += f"ステータス / Status: {status}\n"
            if achievement['description']:
                response += f"説明 / Description: {achievement['description']}\n"
            if achievement['completed_at']:
                response += f"達成日 / Completed: {achievement['completed_at']}\n"
            response += f"作成日 / Created: {achievement['created_at']}"

            await ctx.send(response)
        except Exception as e:
            await ctx.send(f"❌ エラーが発生しました: {e}\nError occurred: {e}")

    @commands.command(name='complete-achievement')
    async def complete_achievement(self, ctx, achievement_id: int):
        """実績を達成としてマーク / Mark achievement as completed"""
        try:
            success = self.db.mark_completed(achievement_id)

            if not success:
                await ctx.send(f"実績が見つかりません (ID: {achievement_id})\nAchievement not found (ID: {achievement_id})")
                return

            await ctx.send(f"🎉 おめでとうございます！実績を達成しました！ (ID: {achievement_id})\nCongratulations! Achievement completed! (ID: {achievement_id})")
        except Exception as e:
            await ctx.send(f"❌ エラーが発生しました: {e}\nError occurred: {e}")

    @commands.command(name='delete-achievement')
    async def delete_achievement(self, ctx, achievement_id: int):
        """実績を削除 / Delete an achievement"""
        try:
            success = self.db.delete_achievement(achievement_id)

            if not success:
                await ctx.send(f"実績が見つかりません (ID: {achievement_id})\nAchievement not found (ID: {achievement_id})")
                return

            await ctx.send(f"🗑️ 実績を削除しました (ID: {achievement_id})\nAchievement deleted (ID: {achievement_id})")
        except Exception as e:
            await ctx.send(f"❌ エラーが発生しました: {e}\nError occurred: {e}")

    @commands.command(name='achievement-stats')
    async def stats(self, ctx):
        """統計情報を表示 / Show statistics"""
        try:
            stats = self.db.get_stats()

            response = "📈 統計情報 / Statistics\n\n"
            response += f"総実績数 / Total: {stats['total']}\n"
            response += f"達成済み / Completed: {stats['completed']}\n"
            response += f"未達成 / Incomplete: {stats['incomplete']}\n"
            if stats['total'] > 0:
                response += f"達成率 / Completion: {(stats['completed'] / stats['total'] * 100):.1f}%\n"
            response += f"\nカテゴリ別 / By Category:\n"
            for cat, count in stats['by_category'].items():
                response += f"  {cat}: {count}\n"

            await ctx.send(response)
        except Exception as e:
            await ctx.send(f"❌ エラーが発生しました: {e}\nError occurred: {e}")

if __name__ == '__main__':
    bot = AchievementAgent()
    import os
    token = os.getenv('DISCORD_BOT_TOKEN')
    bot.run(token)
