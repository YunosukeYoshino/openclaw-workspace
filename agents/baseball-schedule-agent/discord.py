#!/usr/bin/env python3
"""
baseball-schedule-agent - Discord Bot Module
Baseball Schedule Agent - 試合スケジュール管理エージェント

機能:
- 試合スケジュールの管理\n- カレンダー連携\n- 試合リマインダー\n- シーズン日程の追跡
"""

import logging
from .db import BaseballDB

logger = logging.getLogger(__name__)

class BaseballDiscordBot:
    def __init__(self, db_path=None):
        self.db = BaseballDB(db_path)
        logger.info("""baseball-schedule-agent initialized""")

    def process_command(self, command: str) -> str:
        """Discordコマンドを処理する"""
        command = command.strip().lower()

        if command.startswith("追加"):
            return self.add_record(command[2:].strip())
        elif command.startswith("検索"):
            return self.search_records(command[2:].strip())
        elif command.startswith("一覧"):
            return self.list_records()
        elif command == "ヘルプ":
            return self.show_help()
        else:
            return self.show_help()

    def add_record(self, content: str) -> str:
        """記録を追加する"""
        try:
            self.db.add_record(
                title=f"Record {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                content=content
            )
            return "✅ 記録を追加しました"
        except Exception as e:
            logger.error(f"Error adding record: {e}")
            return f"❌ エラーが発生しました: {e}"

    def search_records(self, query_str: str) -> str:
        """記録を検索する"""
        try:
            records = self.db.search_records(query_str)
            if not records:
                return "🔍 該当する記録が見つかりませんでした"
            result = "📋 検索結果:\n"
            for record in records[:10]:
                result += f"- {record[1]}: {record[2][:50]}...\n"
            return result
        except Exception as e:
            logger.error(f"Error searching records: {e}")
            return f"❌ エラーが発生しました: {e}"

    def list_records(self) -> str:
        """全記録を一覧表示する"""
        try:
            records = self.db.get_all_records()
            if not records:
                return "📭 記録がありません"
            result = f"📋 全記録 ({len(records)}件):\n"
            for record in records[:20]:
                result += f"- {record[1]}\n"
            return result
        except Exception as e:
            logger.error(f"Error listing records: {e}")
            return f"❌ エラーが発生しました: {e}"

    def show_help(self) -> str:
        """ヘルプを表示する"""
        return f"""📚 baseball-schedule-agent ヘルプ

Baseball Schedule Agent - 試合スケジュール管理エージェント

コマンド:
- 追加 <内容> - 記録を追加
- 検索 <キーワード> - 記録を検索
- 一覧 - 全記録を表示
- ヘルプ - このヘルプを表示

機能:
- 試合スケジュールの管理\n- カレンダー連携\n- 試合リマインダー\n- シーズン日程の追跡
"""
