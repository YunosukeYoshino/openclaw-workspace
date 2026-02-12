#!/usr/bin/env python3
"""
Software Agent 77 - Database Module
SQLiteベースのデータベース管理モジュール
"""

import sqlite3
import json
import os
from datetime import datetime
from typing import Optional, List, Dict, Any
from contextlib import contextmanager

DATABASE_PATH = os.path.join(os.path.dirname(__file__), "agent_77.db")


class Database:
    """データベース管理クラス"""

    def __init__(self, db_path: str = DATABASE_PATH):
        self.db_path = db_path
        self._init_database()

    @contextmanager
    def _get_connection(self):
        """データベース接続のコンテキストマネージャ"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def _init_database(self):
        """データベースとテーブルの初期化"""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # ユーザーテーブル
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    discord_id TEXT UNIQUE NOT NULL,
                    username TEXT NOT NULL,
                    language TEXT DEFAULT 'ja',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # メッセージ履歴テーブル
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    discord_id TEXT NOT NULL,
                    channel_id TEXT NOT NULL,
                    content TEXT NOT NULL,
                    language TEXT,
                    intent TEXT,
                    metadata TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (discord_id) REFERENCES users(discord_id) ON DELETE CASCADE
                )
            """)

            # 会話コンテキストテーブル
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS contexts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    discord_id TEXT NOT NULL,
                    channel_id TEXT NOT NULL,
                    context_data TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (discord_id) REFERENCES users(discord_id) ON DELETE CASCADE
                )
            """)

            # 知識ベーステーブル
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS knowledge (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT NOT NULL,
                    question TEXT NOT NULL,
                    answer TEXT NOT NULL,
                    language TEXT NOT NULL,
                    keywords TEXT,
                    usage_count INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # タスクテーブル
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    discord_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT,
                    status TEXT DEFAULT 'pending',
                    priority INTEGER DEFAULT 0,
                    due_date TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (discord_id) REFERENCES users(discord_id) ON DELETE CASCADE
                )
            """)

            # インデックスの作成
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_messages_discord_id
                ON messages(discord_id)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_messages_channel_id
                ON messages(channel_id)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_messages_created_at
                ON messages(created_at)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_contexts_discord_channel
                ON contexts(discord_id, channel_id)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_knowledge_language
                ON knowledge(language)
            """)

            conn.commit()

    def add_or_update_user(self, discord_id: str, username: str, language: str = 'ja') -> int:
        """ユーザーの追加または更新"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO users (discord_id, username, language, updated_at)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            """, (discord_id, username, language))
            conn.commit()
            return cursor.lastrowid

    def get_user(self, discord_id: str) -> Optional[Dict[str, Any]]:
        """ユーザー情報の取得"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM users WHERE discord_id = ?
            """, (discord_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def save_message(self, discord_id: str, channel_id: str, content: str,
                     language: str = None, intent: str = None,
                     metadata: Dict[str, Any] = None) -> int:
        """メッセージの保存"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO messages (discord_id, channel_id, content, language, intent, metadata)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (discord_id, channel_id, content, language, intent,
                  json.dumps(metadata) if metadata else None))
            conn.commit()
            return cursor.lastrowid

    def get_recent_messages(self, discord_id: str, channel_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """最近のメッセージ履歴の取得"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM messages
                WHERE discord_id = ? AND channel_id = ?
                ORDER BY created_at DESC
                LIMIT ?
            """, (discord_id, channel_id, limit))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def save_context(self, discord_id: str, channel_id: str, context_data: Dict[str, Any]) -> int:
        """会話コンテキストの保存"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO contexts (discord_id, channel_id, context_data, updated_at)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            """, (discord_id, channel_id, json.dumps(context_data)))
            conn.commit()
            return cursor.lastrowid

    def get_context(self, discord_id: str, channel_id: str) -> Optional[Dict[str, Any]]:
        """会話コンテキストの取得"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM contexts
                WHERE discord_id = ? AND channel_id = ?
            """, (discord_id, channel_id))
            row = cursor.fetchone()
            if row:
                context = dict(row)
                context['context_data'] = json.loads(context['context_data'])
                return context
            return None

    def add_knowledge(self, category: str, question: str, answer: str,
                     language: str = 'ja', keywords: List[str] = None) -> int:
        """知識の追加"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO knowledge (category, question, answer, language, keywords)
                VALUES (?, ?, ?, ?, ?)
            """, (category, question, answer, language,
                  json.dumps(keywords) if keywords else None))
            conn.commit()
            return cursor.lastrowid

    def search_knowledge(self, query: str, language: str = None) -> List[Dict[str, Any]]:
        """知識の検索"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            if language:
                cursor.execute("""
                    SELECT * FROM knowledge
                    WHERE language = ? AND (
                        question LIKE ? OR
                        keywords LIKE ? OR
                        category LIKE ?
                    )
                    ORDER BY usage_count DESC
                """, (language, f'%{query}%', f'%{query}%', f'%{query}%'))
            else:
                cursor.execute("""
                    SELECT * FROM knowledge
                    WHERE question LIKE ? OR keywords LIKE ? OR category LIKE ?
                    ORDER BY usage_count DESC
                """, (f'%{query}%', f'%{query}%', f'%{query}%'))
            rows = cursor.fetchall()
            results = [dict(row) for row in rows]
            # 使用回数を増やす
            if results:
                cursor.execute("""
                    UPDATE knowledge SET usage_count = usage_count + 1
                    WHERE id IN (%s)
                """ % ','.join(str(r['id']) for r in results))
                conn.commit()
            return results

    def add_task(self, discord_id: str, title: str, description: str = None,
                priority: int = 0, due_date: str = None) -> int:
        """タスクの追加"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO tasks (discord_id, title, description, priority, due_date)
                VALUES (?, ?, ?, ?, ?)
            """, (discord_id, title, description, priority, due_date))
            conn.commit()
            return cursor.lastrowid

    def get_tasks(self, discord_id: str, status: str = None) -> List[Dict[str, Any]]:
        """タスクの一覧取得"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            if status:
                cursor.execute("""
                    SELECT * FROM tasks
                    WHERE discord_id = ? AND status = ?
                    ORDER BY priority DESC, created_at ASC
                """, (discord_id, status))
            else:
                cursor.execute("""
                    SELECT * FROM tasks
                    WHERE discord_id = ?
                    ORDER BY priority DESC, created_at ASC
                """, (discord_id,))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def update_task_status(self, task_id: int, status: str) -> bool:
        """タスクステータスの更新"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE tasks
                SET status = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (status, task_id))
            conn.commit()
            return cursor.rowcount > 0

    def get_stats(self) -> Dict[str, Any]:
        """データベース統計情報の取得"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            stats = {}

            cursor.execute("SELECT COUNT(*) as count FROM users")
            stats['total_users'] = cursor.fetchone()['count']

            cursor.execute("SELECT COUNT(*) as count FROM messages")
            stats['total_messages'] = cursor.fetchone()['count']

            cursor.execute("SELECT COUNT(*) as count FROM knowledge")
            stats['total_knowledge'] = cursor.fetchone()['count']

            cursor.execute("SELECT COUNT(*) as count FROM tasks WHERE status = 'pending'")
            stats['pending_tasks'] = cursor.fetchone()['count']

            cursor.execute("SELECT COUNT(*) as count FROM tasks WHERE status = 'completed'")
            stats['completed_tasks'] = cursor.fetchone()['count']

            return stats


# グローバルデータベースインスタンス
_db_instance = None


def get_database() -> Database:
    """データベースインスタンスの取得（シングルトン）"""
    global _db_instance
    if _db_instance is None:
        _db_instance = Database()
    return _db_instance
