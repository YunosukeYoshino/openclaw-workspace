#!/usr/bin/env python3
"""
野球スカウティングプロエージェント - データベースモジュール
Baseball Scouting Pro Agent - Database Module

SQLite データベース管理
"""

import sqlite3
import json
from datetime import datetime


class BaseballExpertDatabase:
    """野球エキスパートデータベース"""

    def __init__(self, db_path=None):
        if db_path is None:
            db_path = os.path.join(
                os.path.dirname(__file__),
                "baseball_expert.db"
            )
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        """データベース初期化"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        self._create_tables(cursor)
        conn.commit()
        conn.close()

    def _create_tables(self, cursor):
        """テーブル作成"""
        cursor.execute("""
CREATE TABLE IF NOT EXISTS players (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    data TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);""")

        cursor.execute("""
CREATE TABLE IF NOT EXISTS scouting_reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    data TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);""")

        cursor.execute("""
CREATE TABLE IF NOT EXISTS evaluations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    data TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);""")

    def insert(self, table, data):
        """データ挿入"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            f"INSERT INTO {table} (data) VALUES (?)",
            (data,)
        )
        conn.commit()
        conn.close()

    def get_all(self, table, limit=100):
        """全データ取得"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            f"SELECT * FROM {table} ORDER BY created_at DESC LIMIT ?",
            (limit,)
        )
        rows = cursor.fetchall()
        conn.close()
        return rows

    def get_by_id(self, table, entry_id):
        """ID指定で取得"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            f"SELECT * FROM {table} WHERE id = ?",
            (entry_id,)
        )
        row = cursor.fetchone()
        conn.close()
        return row

    def search(self, table, query):
        """検索"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            f"SELECT * FROM {table} WHERE data LIKE ? ORDER BY created_at DESC",
            (f"%{query}%",)
        )
        rows = cursor.fetchall()
        conn.close()
        return rows

    def delete(self, table, entry_id):
        """削除"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            f"DELETE FROM {table} WHERE id = ?",
            (entry_id,)
        )
        conn.commit()
        conn.close()

    def get_stats(self, table):
        """統計情報取得"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        conn.close()
        return {"count": count}

    def cleanup_old_entries(self, table, days=30):
        """古いエントリを削除"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(f"""
            DELETE FROM {table}
            WHERE created_at < datetime('now', '-{days} days')
        """)
        deleted = cursor.rowcount
        conn.commit()
        conn.close()
        return deleted
