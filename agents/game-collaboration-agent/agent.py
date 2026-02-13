#!/usr/bin/env python3
"""
game-collaboration-agent エージェント
game-collaboration-agent - AIエージェント
"""

import sqlite3
from pathlib import Path

class GameCollaborationAgent:
    def __init__(self, db_path=None):
        self.db_path = db_path or Path(__file__).parent / "game-collaboration-agent.db"
        self.db_path = str(self.db_path)
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                content TEXT,
                category TEXT,
                tags TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()

    def add_entry(self, title, content, category=None, tags=None):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO entries (title, content, category, tags)
            VALUES (?, ?, ?, ?)
        """, (title, content, category, tags))
        conn.commit()
        conn.close()
        return cursor.lastrowid

    def get_entries(self, category=None):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        if category:
            cursor.execute("SELECT * FROM entries WHERE category = ? ORDER BY created_at DESC", (category,))
        else:
            cursor.execute("SELECT * FROM entries ORDER BY created_at DESC")
        rows = cursor.fetchall()
        conn.close()
        return rows

    def get_entry(self, entry_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM entries WHERE id = ?", (entry_id,))
        row = cursor.fetchone()
        conn.close()
        return row

    def update_entry(self, entry_id, title=None, content=None, category=None, tags=None):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        updates = []
        values = []
        if title:
            updates.append("title = ?")
            values.append(title)
        if content:
            updates.append("content = ?")
            values.append(content)
        if category:
            updates.append("category = ?")
            values.append(category)
        if tags:
            updates.append("tags = ?")
            values.append(tags)
        values.append(entry_id)
        if updates:
            cursor.execute(f"UPDATE entries SET {', '.join(updates)}, updated_at = CURRENT_TIMESTAMP WHERE id = ?", values)
            conn.commit()
        conn.close()

    def delete_entry(self, entry_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM entries WHERE id = ?", (entry_id,))
        conn.commit()
        conn.close()

if __name__ == "__main__":
    agent = GameCollaborationAgent()
    print(f"{name} エージェントが初期化されました。")
