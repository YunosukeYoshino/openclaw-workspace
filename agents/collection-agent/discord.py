#!/usr/bin/env python3
"""
collection-agent - Discord Bot Module

Discord bot for collection-agent - コレクションアイテムの管理・カタログ化
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
    """Discord bot for collection-agent"""

    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True

        super().__init__(
            command_prefix='!',
            intents=intents,
            description="Collection item management and cataloging"
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
            r'(追加|add|作成|create|start)\s*(.+)',
            r'(始めた|started|始める|開始)\s*(.+)'
        ]

        for pattern in add_patterns:
            match = re.search(pattern, content)
            if match:
                title = match.group(2).strip()
                if len(title) > 2:
                    project_id = self.db.add_project(title=title)
                    await message.reply(f'プロジェクトを追加しました: {title} (ID: {project_id})')
                    return

        list_patterns = [
            r'(一覧|list|全|all|what|show)',
            r'(見てる|進行中|doing|working on)'
        ]

        for pattern in list_patterns:
            if re.search(pattern, content):
                projects = self.db.list_projects()
                if projects:
                    response = "**プロジェクト一覧**:\n"
                    for i, project in enumerate(projects[:10], 1):
                        status_emoji = {'planned': '📋', 'in_progress': '🔨', 'completed': '✅'}
                        emoji = status_emoji.get(project['status'], '📌')
                        response += f"{i}. {emoji} {project['title']}\n"
                else:
                    response = "プロジェクトがまだありません。"
                await message.reply(response)
                return

    @commands.command()
    async def add(self, ctx, *, title: str):
        project_id = self.db.add_project(title=title)
        await ctx.send(f'追加しました: {title} (ID: {project_id})')

    @commands.command()
    async def list(self, ctx, status: Optional[str] = None):
        projects = self.db.list_projects(status=status)
        if not projects:
            await ctx.send("プロジェクトがまだありません。")
            return

        response = "**プロジェクト一覧**:\n"
        for i, project in enumerate(projects[:10], 1):
            status_emoji = {'planned': '📋', 'in_progress': '🔨', 'completed': '✅'}
            emoji = status_emoji.get(project['status'], '📌')
            response += f"{i}. {emoji} {project['title']}\n"
        await ctx.send(response)

    @commands.command()
    async def update(self, ctx, project_id: int, **kwargs):
        success = self.db.update_project(project_id, **kwargs)
        if success:
            await ctx.send(f"ID {project_id} を更新しました。")
        else:
            await ctx.send(f"ID {project_id} が見つかりません。")

    @commands.command()
    async def stats(self, ctx):
        stats = self.db.get_statistics()
        response = "**統計**\n"
        response += f"- プロジェクト: {stats['total_projects']}\n"
        response += f"- アイテム: {stats['total_items']}\n"
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
