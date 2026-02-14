#!/usr/bin/env python3
"""
野球博物館エージェント - データベース管理
SQLiteベースのデータ永続化
"""

import sqlite3
from datetime import datetime
from typing import Optional, Dict, Any, List
from contextlib import contextmanager
import json

class BaseballMuseumAgentDB:
    """野球博物館エージェント データベースクラス"""

    def __init__(self, db_path: str = "data/baseball-museum-agent.db"):
        self.db_path = db_path
        self._init_db()

    @contextmanager
    def _get_connection(self):
        """データベース接続のコンテキストマネージャ"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def _init_db(self):
        """データベース初期化"""
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    type TEXT NOT NULL,
                    title TEXT,
                    content TEXT NOT NULL,
                    metadata TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_id TEXT UNIQUE NOT NULL,
                    status TEXT DEFAULT 'pending',
                    result TEXT,
                    error TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

    def insert_record(self, record_type: str, title: str, content: str,
                       metadata: Optional[Dict[str, Any]] = None) -> int:
        """レコード挿入"""
        metadata_json = json.dumps(metadata) if metadata else None
        with self._get_connection() as conn:
            cursor = conn.execute(
                'INSERT INTO records (type, title, content, metadata) VALUES (?, ?, ?, ?)',
                (record_type, title, content, metadata_json)
            )
            return cursor.lastrowid

    def get_record(self, record_id: int) -> Optional[Dict[str, Any]]:
        """レコード取得"""
        with self._get_connection() as conn:
            row = conn.execute('SELECT * FROM records WHERE id = ?', (record_id,)).fetchone()
            if row:
                return dict(row)
        return None

    def list_records(self, record_type: Optional[str] = None,
                    limit: int = 100) -> List[Dict[str, Any]]:
        """レコード一覧"""
        with self._get_connection() as conn:
            if record_type:
                rows = conn.execute(
                    'SELECT * FROM records WHERE type = ? ORDER BY created_at DESC LIMIT ?',
                    (record_type, limit)
                ).fetchall()
            else:
                rows = conn.execute(
                    'SELECT * FROM records ORDER BY created_at DESC LIMIT ?',
                    (limit,)
                ).fetchall()
            return [dict(row) for row in rows]

    def insert_task(self, task_id: str, status: str = "pending") -> int:
        """タスク挿入"""
        with self._get_connection() as conn:
            cursor = conn.execute(
                'INSERT INTO tasks (task_id, status) VALUES (?, ?)',
                (task_id, status)
            )
            return cursor.lastrowid

    def update_task(self, task_id: str, status: str,
                   result: Optional[str] = None, error: Optional[str] = None):
        """タスク更新"""
        completed_at = datetime.now().isoformat() if status == "completed" else None
        with self._get_connection() as conn:
            conn.execute(
                'UPDATE tasks SET status = ?, result = ?, error = ?, completed_at = ? WHERE task_id = ?',
                (status, result, error, completed_at, task_id)
            )

    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """タスク取得"""
        with self._get_connection() as conn:
            row = conn.execute('SELECT * FROM tasks WHERE task_id = ?', (task_id,)).fetchone()
            if row:
                return dict(row)
        return None

    def set_setting(self, key: str, value: str):
        """設定保存"""
        with self._get_connection() as conn:
            conn.execute(
                'INSERT INTO settings (key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value = ?, updated_at = CURRENT_TIMESTAMP',
                (key, value, value)
            )

    def get_setting(self, key: str) -> Optional[str]:
        """設定取得"""
        with self._get_connection() as conn:
            row = conn.execute('SELECT value FROM settings WHERE key = ?', (key,)).fetchone()
            if row:
                return row['value']
        return None

async def main():
    """動作確認"""
    db = BaseballMuseumAgentDB()

    record_id = db.insert_record(
        record_type="sample",
        title="Sample Record",
        content="This is a sample record for 野球博物館エージェント"
    )
    print(f"Inserted record: {record_id}")

    record = db.get_record(record_id)
    print(f"Retrieved record: {record}")

    db.insert_task("task_001")
    db.update_task("task_001", "completed", result="Success")

    task = db.get_task("task_001")
    print(f"Task status: {task}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
