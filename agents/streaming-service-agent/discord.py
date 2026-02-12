#!/usr/bin/env python3
"""
streaming-service-agent - Discord Bot Module

Discord bot for streaming-service-agent - Netflix、Amazon Prime、Disney+などの視聴記録
"""

import discord
from discord.ext import commands
import re
from typing import Optional, List
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))
from db import Database


class DiscordBot(commands.Bot):
    """Discord bot for streaming-service-agent"""

    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.reactions = True

        super().__init__(
            command_prefix='!',
            intents=intents,
            description="Viewing history for Netflix, Amazon Prime, Disney+, etc."
        )

        self.db = Database()

    async def on_ready(self):
        """Bot is ready"""
        print(f'{self.user} has connected to Discord!')
        print(f'Guilds: {len(self.guilds)}')

    async def on_message(self, message: discord.Message):
        """Handle incoming messages"""
        if message.author == self.user:
            return

        await self._process_natural_language(message)
        await super().on_message(message)

    async def _process_natural_language(self, message: discord.Message):
        """Process natural language messages"""
        content = message.content.lower()

        add_patterns = [
            r'(追加|add|記録|track|登録)\s*(.+)',
            r'(見た|watched|読んだ|read|聞いた|listened)\s*(.+)'
        ]

        for pattern in add_patterns:
            match = re.search(pattern, content)
            if match:
                title = match.group(2).strip()
                if len(title) > 2:
                    record_id = self.db.add_record(
                        title=title,
                        status='completed',
                        start_date=message.created_at.isoformat()
                    )
                    await message.reply(f'記録しました: {title} (ID: {record_id})')
                    return

        list_patterns = [
            r'(一覧|list|全|all|what|what\s+do|show)',
            r'(見てる|watching|読んでる|reading|聞いてる|listening)'
        ]

        for pattern in list_patterns:
            if re.search(pattern, content):
                records = self.db.list_records()
                if records:
                    response = "**一覧**:\n"
                    for i, record in enumerate(records[:10], 1):
                        status_emoji = {'watching': '👀', 'completed': '✅', 'planned': '📋'}
                        emoji = status_emoji.get(record['status'], '📌')
                        response += f"{i}. {emoji} {record['title']}\n"
                    if len(records) > 10:
                        response += f"\n...他 {len(records) - 10}件"
                else:
                    response = "記録がまだありません。"
                await message.reply(response)
                return

        help_patterns = [r'(help|ヘルプ|使い方|how|使う)']
        for pattern in help_patterns:
            if re.search(pattern, content):
                await self._send_help(message)
                return

    async def _send_help(self, message: discord.Message):
        """Send help message"""
        help_text = "**" + agent_info['name_ja'] + "** - " + agent_info['description'] + "

"
        help_text += "**コマンド**:
"
        help_text += "- `!add <タイトル>` - 追加
"
        help_text += "- `!list` - 一覧
"
        help_text += "- `!update <ID> [status|rating]` - 更新
"
        help_text += "- `!delete <ID>` - 削除
"
        help_text += "- `!stats` - 統計

"
        help_text += "**自然言語**:
"
        help_text += '- "○○を追加" "○○を見た" - 記録追加
'
        help_text += '- "一覧" "何見てる？" - 一覧表示'
        await message.reply(help_text)

    @commands.command()
    async def add(self, ctx, *, title: str):
        """Add a record"""
        record_id = self.db.add_record(title=title)
        await ctx.send(f'追加しました: {title} (ID: {record_id})')

    @commands.command()
    async def list(self, ctx, status: Optional[str] = None):
        """List records"""
        records = self.db.list_records(status=status)

        if not records:
            await ctx.send("記録がまだありません。")
            return

        response = "**一覧**:\n"
        for i, record in enumerate(records[:10], 1):
            status_emoji = {'watching': '👀', 'completed': '✅', 'planned': '📋'}
            emoji = status_emoji.get(record['status'], '📌')
            response += f"{i}. {emoji} {record['title']}"
            if record['rating'] > 0:
                response += f" ⭐{record['rating']}"
            response += "\n"

        if len(records) > 10:
            response += f"\n...他 {len(records) - 10}件"

        await ctx.send(response)

    @commands.command()
    async def update(self, ctx, record_id: int, **kwargs):
        """Update a record"""
        success = self.db.update_record(record_id, **kwargs)
        if success:
            await ctx.send(f"ID {record_id} を更新しました。")
        else:
            await ctx.send(f"ID {record_id} が見つかりません。")

    @commands.command()
    async def delete(self, ctx, record_id: int):
        """Delete a record"""
        success = self.db.delete_record(record_id)
        if success:
            await ctx.send(f"ID {record_id} を削除しました。")
        else:
            await ctx.send(f"ID {record_id} が見つかりません。")

    @commands.command()
    async def stats(self, ctx):
        """Show statistics"""
        stats = self.db.get_statistics()
        response = "**統計**\n"
        response += f"- 総数: {stats['total']}\n"
        response += f"- 平均評価: {stats['average_rating']}\n\n"
        response += "**ステータス別**:\n"
        for status, count in stats['by_status'].items():
            response += f"- {status}: {count}\n"
        await ctx.send(response)

    def close(self):
        """Close database connection"""
        self.db.close()


def main():
    """Main function"""
    import os
    token = os.environ.get('DISCORD_TOKEN')

    if not token:
        print("Error: DISCORD_TOKEN environment variable not set")
        return

    bot = DiscordBot()
    bot.run(token)


if __name__ == '__main__':
    main()
