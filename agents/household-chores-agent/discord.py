#!/usr/bin/env python3
"""
household-chores-agent - Discord Bot Module

Discord bot for household-chores-agent - 家事タスクの管理・スケジュール・リマインダー
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
    """Discord bot for household-chores-agent"""

    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True

        super().__init__(
            command_prefix='!',
            intents=intents,
            description="Household chores management, scheduling, and reminders"
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
            r'(家事|chore|追加|add|やる|do)\s*(.+)',
            r'(掃除|cleaning|洗濯|laundry)\s*(.+)'
        ]

        for pattern in add_patterns:
            match = re.search(pattern, content)
            if match:
                title = match.group(2).strip()
                if len(title) > 2:
                    chore_id = self.db.add_chore(title=title)
                    await message.reply(f'家事を追加しました: {title} (ID: {chore_id})')
                    return

        list_patterns = [
            r'(一覧|list|全|all|what|show)',
            r'(家事|chores|やること|todo)'
        ]

        for pattern in list_patterns:
            if re.search(pattern, content):
                chores = self.db.list_chores(status='pending')
                if chores:
                    response = "**家事一覧**:\n"
                    for i, chore in enumerate(chores[:10], 1):
                        priority_emoji = {3: '🔴', 2: '🟡', 1: '🟢'}
                        emoji = priority_emoji.get(chore['priority'], '⚪')
                        response += f"{i}. {emoji} {chore['title']}\n"
                else:
                    response = "家事がまだありません。"
                await message.reply(response)
                return

    @commands.command()
    async def add(self, ctx, *, title: str):
        chore_id = self.db.add_chore(title=title)
        await ctx.send(f'追加しました: {title} (ID: {chore_id})')

    @commands.command()
    async def list(self, ctx, status: Optional[str] = None):
        chores = self.db.list_chores(status=status)
        if not chores:
            await ctx.send("家事がまだありません。")
            return

        response = "**家事一覧**:\n"
        for i, chore in enumerate(chores[:10], 1):
            priority_emoji = {3: '🔴', 2: '🟡', 1: '🟢'}
            emoji = priority_emoji.get(chore['priority'], '⚪')
            response += f"{i}. {emoji} {chore['title']}\n"
        await ctx.send(response)

    @commands.command()
    async def done(self, ctx, chore_id: int):
        from datetime import datetime
        success = self.db.update_chore(chore_id, status='completed', completed_date=datetime.now().isoformat())
        if success:
            await ctx.send(f"ID {chore_id} を完了にしました。")
        else:
            await ctx.send(f"ID {chore_id} が見つかりません。")

    @commands.command()
    async def delete(self, ctx, chore_id: int):
        success = self.db.delete_chore(chore_id)
        if success:
            await ctx.send(f"ID {chore_id} を削除しました。")
        else:
            await ctx.send(f"ID {chore_id} が見つかりません。")

    @commands.command()
    async def stats(self, ctx):
        stats = self.db.get_statistics()
        response = "**統計**\n"
        response += f"- 未完了家事: {stats['pending_chores']}\n"
        response += f"- 必要な買い物: {stats['needed_shopping_items']}\n"
        response += f"- 未払い請求: {stats['pending_bill_amount']}円\n"
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
