#!/usr/bin/env python3
"""
goal-setting-agent - Discord Bot Module

Discord bot for goal-setting-agent - 目標の設定・追跡・達成記録
"""

import discord
from discord.ext import commands
import re
from typing import Optional
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))
from db import Database


class DiscordBot(commands.Bot):
    """Discord bot for goal-setting-agent"""

    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True

        super().__init__(
            command_prefix='!',
            intents=intents,
            description="Goal setting, tracking, and achievement recording"
        )

        self.db = Database()

    async def on_ready(self):
        print(f'{self.user} has connected to Discord!')

    async def on_message(self, message: discord.Message):
        if message.author == self.user:
            return

        await self._process_natural_language(message)
        await super().on_message(message)

    async def _process_natural_language(self, message: discord.Message):
        content = message.content.lower()

        add_patterns = [
            r'(タスク|task|追加|add|作成|create)\s*(.+)',
            r'(やる|to do|する|do)\s*(.+)'
        ]

        for pattern in add_patterns:
            match = re.search(pattern, content)
            if match:
                title = match.group(2).strip()
                if len(title) > 2:
                    task_id = self.db.add_task(title=title)
                    await message.reply(f'タスクを追加しました: {title} (ID: {task_id})')
                    return

        list_patterns = [
            r'(一覧|list|全|all|what|show)',
            r'(タスク|tasks|todo|やること)'
        ]

        for pattern in list_patterns:
            if re.search(pattern, content):
                tasks = self.db.list_tasks(status='pending')
                if tasks:
                    response = "**タスク一覧**:\n"
                    for i, task in enumerate(tasks[:10], 1):
                        priority_emoji = {3: '🔴', 2: '🟡', 1: '🟢'}
                        emoji = priority_emoji.get(task['priority'], '⚪')
                        response += f"{i}. {emoji} {task['title']}\n"
                else:
                    response = "タスクがまだありません。"
                await message.reply(response)
                return

    @commands.command()
    async def add(self, ctx, *, title: str):
        task_id = self.db.add_task(title=title)
        await ctx.send(f'追加しました: {title} (ID: {task_id})')

    @commands.command()
    async def list(self, ctx, status: Optional[str] = None):
        tasks = self.db.list_tasks(status=status)
        if not tasks:
            await ctx.send("タスクがまだありません。")
            return

        response = "**タスク一覧**:\n"
        for i, task in enumerate(tasks[:10], 1):
            priority_emoji = {3: '🔴', 2: '🟡', 1: '🟢'}
            emoji = priority_emoji.get(task['priority'], '⚪')
            response += f"{i}. {emoji} {task['title']}\n"
        await ctx.send(response)

    @commands.command()
    async def done(self, ctx, task_id: int):
        from datetime import datetime
        success = self.db.update_task(task_id, status='completed', completed_date=datetime.now().isoformat())
        if success:
            await ctx.send(f"ID {task_id} を完了にしました。")
        else:
            await ctx.send(f"ID {task_id} が見つかりません。")

    @commands.command()
    async def delete(self, ctx, task_id: int):
        success = self.db.delete_task(task_id)
        if success:
            await ctx.send(f"ID {task_id} を削除しました。")
        else:
            await ctx.send(f"ID {task_id} が見つかりません。")

    @commands.command()
    async def stats(self, ctx):
        stats = self.db.get_statistics()
        response = "**統計**\n"
        response += f"- 未完了タスク: {stats['pending_tasks']}\n"
        response += f"- 完了タスク: {stats['completed_tasks']}\n"
        response += f"- 総作業時間: {stats['total_hours']}時間\n"
        response += f"- セッション数: {stats['total_sessions']}\n"
        await ctx.send(response)

    def close(self):
        self.db.close()


def main():
    import os
    token = os.environ.get('DISCORD_TOKEN')
    if not token:
        print("Error: DISCORD_TOKEN environment variable not set")
        return
    bot = DiscordBot()
    bot.run(token)


if __name__ == '__main__':
    main()
