#!/usr/bin/env python3
"""
game-social-agent - SQLite Database Module
ゲーム関連データの管理
"""

import sqlite3
from datetime import datetime
from pathlib import Path

class GameDB:
    def __init__(self, db_path=None):
        if db_path is None:
            db_path = Path(__file__).parent / ""game-social-agent.db""
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                category TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()
        conn.close()

    def add_record(self, title, content, category=None):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO records (title, content, category) VALUES (?, ?, ?)",
            (title, content, category)
        )

        conn.commit()
        conn.close()

    def get_all_records(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM records ORDER BY created_at DESC")
        records = cursor.fetchall()

        conn.close()
        return records

    def search_records(self, query):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM records WHERE title LIKE ? OR content LIKE ?",
            (f"%{query}%", f"%{query}%")
        )
        records = cursor.fetchall()

        conn.close()
        return records

    def get_by_category(self, category):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM records WHERE category = ? ORDER BY created_at DESC",
            (category,)
        )
        records = cursor.fetchall()

        conn.close()
        return records
