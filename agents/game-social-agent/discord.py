#!/usr/bin/env python3
"""
game-social-agent - Discord Bot Module
Game Social Agent - ゲームソーシャル管理エージェント

機能:
- フレンド・チーム管理\n- オンラインイベントの記録\n- マッチング履歴の管理\n- ソーシャル機能の活用
"""

import logging
from .db import GameDB

logger = logging.getLogger(__name__)

class GameDiscordBot:
    def __init__(self, db_path=None):
        self.db = GameDB(db_path)
        logger.info("""game-social-agent initialized""")

    def process_command(self, command: str) -> str:
        """Discordコマンドを処理する"""
        command = command.strip().lower()

        if command.startswith("追加"):
            return self.add_record(command[2:].strip())
        elif command.startswith("検索"):
            return self.search_records(command[2:].strip())
        elif command.startswith("一覧"):
            return self.list_records()
        elif command.startswith("カテゴリ"):
            return self.list_by_category(command[4:].strip())
        elif command == "ヘルプ":
            return self.show_help()
        else:
            return self.show_help()

    def add_record(self, content: str) -> str:
        """記録を追加する"""
        try:
            # コンテンツを解析してタイトルとカテゴリを抽出
            parts = content.split("|", 1)
            if len(parts) == 2:
                title, rest = parts
                rest_parts = rest.split("|", 1)
                if len(rest_parts) == 2:
                    category, content_text = rest_parts
                else:
                    category = None
                    content_text = rest
            else:
                title = f"Record {datetime.now().strftime('%Y-%m-%d %H:%M')}"
                category = None
                content_text = content

            self.db.add_record(title.strip(), content_text.strip(), category.strip() if category else None)
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
                category_str = f"[{record[3]}]" if record[3] else ""
                result += f"- {category_str}{record[1]}: {record[2][:50]}...\n"
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
                category_str = f"[{record[3]}]" if record[3] else ""
                result += f"- {category_str}{record[1]}\n"
            return result
        except Exception as e:
            logger.error(f"Error listing records: {e}")
            return f"❌ エラーが発生しました: {e}"

    def list_by_category(self, category: str) -> str:
        """カテゴリ別に記録を表示する"""
        try:
            if not category:
                return "❌ カテゴリを指定してください"
            records = self.db.get_by_category(category)
            if not records:
                return f"📭 カテゴリ '{category}' の記録がありません"
            result = f"📋 [{category}] 記録 ({len(records)}件):\n"
            for record in records[:20]:
                result += f"- {record[1]}\n"
            return result
        except Exception as e:
            logger.error(f"Error listing by category: {e}")
            return f"❌ エラーが発生しました: {e}"

    def show_help(self) -> str:
        """ヘルプを表示する"""
        return f"""📚 game-social-agent ヘルプ

Game Social Agent - ゲームソーシャル管理エージェント

コマンド:
- 追加 <内容> - 記録を追加
- 検索 <キーワード> - 記録を検索
- 一覧 - 全記録を表示
- カテゴリ <名前> - カテゴリ別表示
- ヘルプ - このヘルプを表示

記録追加フォーマット:
タイトル | カテゴリ | 内容

機能:
- フレンド・チーム管理\n- オンラインイベントの記録\n- マッチング履歴の管理\n- ソーシャル機能の活用
"""
