#!/usr/bin/env python3
"""
野球トレンド追跡エージェント - データベースモジュール

SQLiteデータベース操作モジュール
"""

import sqlite3
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime
from contextlib import contextmanager
import logging

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BaseballTrendTrackerAgentDB:
    """野球トレンド追跡エージェント データベースクラス"""

    def __init__(self, db_path: str = "baseball-trend-tracker-agent.db"):
        """初期化

        Args:
            db_path: データベースファイルパス
        """
        self.db_path = db_path

    @contextmanager
    def get_connection(self):
        """データベース接続コンテキストマネージャー"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            conn.close()

    def initialize_db(self):
        """データベース初期化"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # エントリーテーブル作成
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT,
                    content TEXT NOT NULL,
                    tags TEXT,
                    priority INTEGER DEFAULT 0,
                    status TEXT DEFAULT 'active',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # trends_テーブル作成
            
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS trends (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                description TEXT,
                url TEXT,
                entry_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (entry_id) REFERENCES entries(id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS topics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                description TEXT,
                url TEXT,
                entry_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (entry_id) REFERENCES entries(id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS analytics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                description TEXT,
                url TEXT,
                entry_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (entry_id) REFERENCES entries(id)
            )
        """)

            logger.info("Database initialized")

    def execute_query(self, query: str, params: Tuple = (), fetch: bool = True) -> Optional[List[Dict]]:
        """クエリ実行

        Args:
            query: SQLクエリ
            params: パラメータ
            fetch: 結果を取得するかどうか

        Returns:
            クエリ結果（fetch=Trueの場合）
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            if fetch:
                return [dict(row) for row in cursor.fetchall()]
            return None

    def add_entry(self, title: str, content: str, tags: Optional[str] = None, priority: int = 0) -> int:
        """エントリー追加

        Args:
            title: タイトル
            content: コンテンツ
            tags: タグ
            priority: 優先度

        Returns:
            エントリーID
        """
        result = self.execute_query(
            "INSERT INTO entries (title, content, tags, priority) VALUES (?, ?, ?, ?) RETURNING id",
            (title, content, tags, priority)
        )
        entry_id = result[0]['id'] if result else None
        logger.info(f"Entry added: {title} (ID: {entry_id})")
        return entry_id

    def get_entry(self, entry_id: int) -> Optional[Dict]:
        """エントリー取得

        Args:
            entry_id: エントリーID

        Returns:
            エントリーデータ
        """
        result = self.execute_query("SELECT * FROM entries WHERE id = ?", (entry_id,))
        return result[0] if result else None

    def list_entries(self, limit: int = 100, status: str = None) -> List[Dict]:
        """エントリーリスト取得

        Args:
            limit: 取得件数
            status: ステータスフィルタ

        Returns:
            エントリーリスト
        """
        if status:
            return self.execute_query(
                "SELECT * FROM entries WHERE status = ? ORDER BY created_at DESC LIMIT ?",
                (status, limit)
            )
        return self.execute_query(
            "SELECT * FROM entries ORDER BY created_at DESC LIMIT ?",
            (limit,)
        )

    def update_entry(self, entry_id: int, **kwargs) -> bool:
        """エントリー更新

        Args:
            entry_id: エージェントID
            **kwargs: 更新フィールド

        Returns:
            成功時True
        """
        valid_fields = ['title', 'content', 'tags', 'priority', 'status']
        update_fields = {k: v for k, v in kwargs.items() if k in valid_fields}
        if not update_fields:
            return False

        update_fields['updated_at'] = str(datetime.now())
        set_clause = ', '.join([f"{k} = ?" for k in update_fields.keys()])
        values = list(update_fields.values()) + [entry_id]

        self.execute_query(f"UPDATE entries SET {set_clause} WHERE id = ?", tuple(values), fetch=False)
        logger.info(f"Entry updated: ID {entry_id}")
        return True

    def delete_entry(self, entry_id: int) -> bool:
        """エントリー削除

        Args:
            entry_id: エージェントID

        Returns:
            成功時True
        """
        result = self.execute_query("DELETE FROM entries WHERE id = ? RETURNING id", (entry_id,))
        if result:
            logger.info(f"Entry deleted: ID {entry_id}")
            return True
        return False

    def search_entries(self, query: str) -> List[Dict]:
        """エントリー検索

        Args:
            query: 検索クエリ

        Returns:
            検索結果
        """
        return self.execute_query(
            "SELECT * FROM entries WHERE title LIKE ? OR content LIKE ? OR tags LIKE ?",
            (f"%{query}%", f"%{query}%", f"%{query}%")
        )

    def get_stats(self) -> Dict[str, int]:
        """統計情報取得

        Returns:
            統計情報
        """
        active = self.execute_query("SELECT COUNT(*) as count FROM entries WHERE status = 'active'")[0]['count']
        total = self.execute_query("SELECT COUNT(*) as count FROM entries")[0]['count']
        return {"active": active, "total": total}

    def get_trends(self, limit: int = 100) -> List[Dict]:
        """trendsリスト取得

        Args:
            limit: 取得件数

        Returns:
            trendsリスト
        """
        return self.execute_query(
            f"SELECT * FROM trends ORDER BY created_at DESC LIMIT ?",
            (limit,)
        )

    def add_trends(self, **kwargs) -> int:
        """trends追加

        Returns:
            追加したID
        """
        # trends_テーブルにデータを追加するロジック
        # 各エージェントの要件に合わせて実装
        pass


def main():
    """メイン関数"""
    db = BaseballTrendTrackerAgentDB()
    db.initialize_db()
    print(f"{db.__class__.__name__} initialized")
    print(f"Stats: {db.get_stats()}")


if __name__ == "__main__":
    main()
