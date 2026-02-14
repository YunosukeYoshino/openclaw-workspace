#!/usr/bin/env python3
"""
Database Manager for baseball-contract-manager-agent
"""

import sqlite3
from datetime import datetime
from typing import List, Optional

class DatabaseManager:
    def __init__(self, db_path: str = "baseball-contract-manager-agent.db"):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS records (id INTEGER PRIMARY KEY AUTOINCREMENT, content TEXT NOT NULL, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
        conn.commit()
        conn.close()
    
    def add_record(self, content: str) -> int:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("INSERT INTO records (content) VALUES (?)", (content,))
        conn.commit()
        record_id = c.lastrowid
        conn.close()
        return record_id
    
    def get_record(self, record_id: int) -> Optional[dict]:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT * FROM records WHERE id = ?", (record_id,))
        row = c.fetchone()
        conn.close()
        if row:
            return {"id": row[0], "content": row[1], "created_at": row[2]}
        return None
    
    def list_records(self, limit: int = 100) -> List[dict]:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT * FROM records ORDER BY created_at DESC LIMIT ?", (limit,))
        rows = c.fetchall()
        conn.close()
        return [{"id": r[0], "content": r[1], "created_at": r[2]} for r in rows]

if __name__ == "__main__":
    db = DatabaseManager()
    print("Database initialized")
