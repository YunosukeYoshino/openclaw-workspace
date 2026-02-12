#!/usr/bin/env python3
"""
audio-summarizer Discord Bot
audio-summarizer - AIエージェント
"""

import logging
import os

from discord.ext import commands
from discord import Intents

from agent import AudioSummarizer

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Discord Bot設定
TOKEN = os.getenv('DISCORD_TOKEN')
intents = Intents.default()
intents.message_content = True

class AudioSummarizerBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='!', intents=intents)
        self.agent = AudioSummarizer()

    async def on_ready(self):
        logger.info(f'{self.user.name} has connected to Discord!')

    async def on_message(self, message):
        if message.author == self.user:
            return

        content = message.content.lower()

        if content.startswith('!'):
            await self.process_commands(message)
        else:
            await self._natural_language_command(message)

    async def _natural_language_command(self, message):
        """自然言語コマンドを解析して適切な処理を実行"""
        content = message.content.lower()

        # 追加
        if '追加' in content or 'add' in content or '登録' in content or '記録' in content:
            parts = content.split(' ', 1)
            title = parts[1].split('を')[0] if len(parts) > 1 and 'を' in parts[1] else (parts[1] if len(parts) > 1 else "無題")
            title = title.strip() if title else "無題"
            entry_content = content[content.find('を') + 1:] if 'を' in content else (parts[1] if len(parts) > 1 else content)

            self.agent.add_entry(title, entry_content)
            await message.reply(f'✅ エントリー「{title}」を追加しました！')

        # 一覧
        elif '一覧' in content or 'list' in content or '表示' in content:
            entries = self.agent.get_entries()
            if entries:
                msg = "📋 エントリー一覧:\n"
                for entry in entries[:10]:
                    msg += f"- **{entry[1]}** ({entry[6]})\n"
                if len(entries) > 10:
                    msg += f"\n... 他 {len(entries) - 10} 件"
                await message.reply(msg)
            else:
                await message.reply("📭 エントリーはありません。")

        # 検索
        elif '検索' in content or 'search' in content:
            parts = content.split(' ', 1)
            category = parts[1] if len(parts) > 1 else None
            if category:
                entries = self.agent.get_entries(category)
                if entries:
                    msg = f"🔍 カテゴリ「{category}」の検索結果:\n"
                    for entry in entries:
                        msg += f"- **{entry[1]}**: {entry[2][:50]}...\n"
                    await message.reply(msg)
                else:
                    await message.reply(f"📭 カテゴリ「{category}」のエントリーはありません。")

        # 削除
        elif '削除' in content or 'delete' in content:
            import re
            match = re.search(r'\d+', content)
            if match:
                entry_id = int(match.group())
                self.agent.delete_entry(entry_id)
                await message.reply(f'🗑️ エントリー #{entry_id} を削除しました！')
            else:
                await message.reply("❌ 削除するエントリー番号を指定してください。")

def main():
    token = os.getenv('DISCORD_TOKEN', TOKEN)
    if not token:
        logger.error("DISCORD_TOKEN が設定されていません。")
        return

    bot = AudioSummarizerBot()
    bot.run(token)

if __name__ == "__main__":
    main()
