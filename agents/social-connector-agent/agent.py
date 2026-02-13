#!/usr/bin/env python3
"""
Social Connector Agent / ソーシャルコネクターエージェント
Social relationship management and reminders

ソーシャル関係管理とリマインダー
"""

import sqlite3
import os
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Any

class SocialConnectorAgent:
    """Social Connector Agent"""

    def __init__(self, db_path=None):
        if db_path is None:
            db_path = os.path.join(os.path.dirname(__file__), "data.db")
        self.db_path = db_path
        self.conn = None
        self.init_db()

    def init_db(self):
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        cursor = self.conn.cursor()
        # Create contacts table
        cursor.execute("CREATE TABLE IF NOT EXISTS contacts (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, content TEXT NOT NULL, priority INTEGER DEFAULT 0, status TEXT DEFAULT 'active', metadata TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
        # Create entries table
        cursor.execute("CREATE TABLE IF NOT EXISTS entries (id INTEGER PRIMARY KEY AUTOINCREMENT, type TEXT NOT NULL, title TEXT, content TEXT NOT NULL, status TEXT DEFAULT 'active', priority INTEGER DEFAULT 0, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
        # Create indices
        cursor.execute(f'CREATE INDEX IF NOT EXISTS idx_{self._sanitize_table("contacts")}_status ON contacts(status)')
        cursor.execute(f'CREATE INDEX IF NOT EXISTS idx_{self._sanitize_table("contacts")}_priority ON contacts(priority)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_entries_status ON entries(status)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_entries_created_at ON entries(created_at)')
        self.conn.commit()

    def _sanitize_table(self, table_name):
        return table_name.replace("-", "_")

    def add_item(self, title, content, priority=0, metadata=None):
        cursor = self.conn.cursor()
        metadata_json = json.dumps(metadata) if metadata else None
        cursor.execute("INSERT INTO contacts (title, content, priority, metadata) VALUES (?, ?, ?, ?)", (title, content, priority, metadata_json))
        self.conn.commit()
        return cursor.lastrowid

    def get_items(self, status=None, min_priority=None, limit=None):
        cursor = self.conn.cursor()
        query = "SELECT * FROM contacts"
        params = []
        conditions = []
        if status:
            conditions.append("status = ?")
            params.append(status)
        if min_priority is not None:
            conditions.append("priority >= ?")
            params.append(min_priority)
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        query += " ORDER BY priority DESC, created_at DESC"
        if limit:
            query += " LIMIT ?"
            params.append(limit)
        cursor.execute(query, params)
        return cursor.fetchall()

    def update_item(self, item_id, **kwargs):
        valid_fields = ['title', 'content', 'priority', 'status']
        updates = [f"{k} = ?" for k in kwargs.keys() if k in valid_fields]
        values = [v for k, v in kwargs.items() if k in valid_fields]
        if updates:
            query = f"UPDATE contacts SET {', '.join(updates)} WHERE id = ?"
            values.append(item_id)
            cursor = self.conn.cursor()
            cursor.execute(query, values)
            self.conn.commit()

    def delete_item(self, item_id):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM contacts WHERE id = ?", (item_id,))
        self.conn.commit()

    def add_entry(self, entry_type, content, title=None, priority=0):
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO entries (type, title, content, priority) VALUES (?, ?, ?, ?)", (entry_type, title, content, priority))
        self.conn.commit()
        return cursor.lastrowid

    def get_entries(self, entry_type=None, status=None, limit=None):
        cursor = self.conn.cursor()
        query = "SELECT * FROM entries"
        params = []
        if entry_type:
            query += " WHERE type = ?"
            params.append(entry_type)
        query += " ORDER BY created_at DESC"
        if limit:
            query += " LIMIT ?"
            params.append(limit)
        cursor.execute(query, params)
        return cursor.fetchall()

    def get_summary(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) as total, COUNT(CASE WHEN status='active' THEN 1 END) as active FROM contacts")
        result = cursor.fetchone()
        return {"total": result['total'], "active": result['active']}

    def close(self):
        if self.conn:
            self.conn.close()

def main():
    agent = SocialConnectorAgent()
    try:
        print(f"Social Connector Agent initialized")
        print(f"Database: {agent.db_path}")
        print("Available commands: connect, remember, remind, event, network")
    finally:
        agent.close()

if __name__ == "__main__":
    main()
