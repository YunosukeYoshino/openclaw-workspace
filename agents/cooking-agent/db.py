#!/usr/bin/env python3
"""
cooking-agent - Database Module

SQLite database operations for the agent.
"""

import sqlite3
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path


class Database:
    """Database manager for cooking-agent"""

    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = Path(__file__).parent / "data.db"
        self.db_path = db_path
        self.conn = None
        self._initialize()

    def _initialize(self):
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self._create_tables()

    def _create_tables(self):
        cursor = self.conn.cursor()

        cursor.execute(
            "CREATE TABLE IF NOT EXISTS projects ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT,"
            "title TEXT NOT NULL,"
            "description TEXT,"
            "category TEXT,"
            "status TEXT DEFAULT 'planned',"
            "start_date TEXT,"
            "end_date TEXT,"
            "progress INTEGER DEFAULT 0,"
            "notes TEXT,"
            "tags TEXT,"
            "created_at TEXT DEFAULT CURRENT_TIMESTAMP,"
            "updated_at TEXT DEFAULT CURRENT_TIMESTAMP"
            ")"
        )

        cursor.execute(
            "CREATE TABLE IF NOT EXISTS items ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT,"
            "name TEXT NOT NULL,"
            "description TEXT,"
            "category TEXT,"
            "quantity INTEGER DEFAULT 1,"
            "location TEXT,"
            "status TEXT DEFAULT 'available',"
            "created_at TEXT DEFAULT CURRENT_TIMESTAMP"
            ")"
        )

        cursor.execute(
            "CREATE TABLE IF NOT EXISTS logs ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT,"
            "project_id INTEGER,"
            "title TEXT,"
            "content TEXT,"
            "log_date TEXT DEFAULT CURRENT_TIMESTAMP,"
            "FOREIGN KEY (project_id) REFERENCES projects(id)"
            ")"
        )

        self.conn.commit()

    def add_project(self, title: str, description: str = None,
                   category: str = None, status: str = 'planned',
                   notes: str = None) -> int:
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO projects (title, description, category, status, notes) VALUES (?, ?, ?, ?, ?)",
            (title, description, category, status, notes)
        )
        self.conn.commit()
        return cursor.lastrowid

    def get_project(self, project_id: int) -> Optional[Dict]:
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM projects WHERE id = ?', (project_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def list_projects(self, status: str = None,
                     category: str = None) -> List[Dict]:
        cursor = self.conn.cursor()
        query = 'SELECT * FROM projects WHERE 1=1'
        params = []

        if status:
            query += ' AND status = ?'
            params.append(status)

        if category:
            query += ' AND category = ?'
            params.append(category)

        query += ' ORDER BY created_at DESC'
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

    def update_project(self, project_id: int, **kwargs) -> bool:
        valid_fields = ['title', 'description', 'category', 'status',
                       'start_date', 'end_date', 'progress', 'notes']
        update_fields = {k: v for k, v in kwargs.items() if k in valid_fields}

        if not update_fields:
            return False

        update_fields['updated_at'] = datetime.now().isoformat()
        set_clause = ', '.join([f'{k} = ?' for k in update_fields.keys()])
        values = list(update_fields.values()) + [project_id]

        cursor = self.conn.cursor()
        cursor.execute(
            f"UPDATE projects SET {set_clause} WHERE id = ?",
            values
        )
        self.conn.commit()
        return cursor.rowcount > 0

    def add_item(self, name: str, description: str = None,
                category: str = None, quantity: int = 1,
                location: str = None) -> int:
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO items (name, description, category, quantity, location) VALUES (?, ?, ?, ?, ?)",
            (name, description, category, quantity, location)
        )
        self.conn.commit()
        return cursor.lastrowid

    def list_items(self, category: str = None) -> List[Dict]:
        cursor = self.conn.cursor()
        query = 'SELECT * FROM items WHERE 1=1'
        params = []

        if category:
            query += ' AND category = ?'
            params.append(category)

        query += ' ORDER BY created_at DESC'
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

    def add_log(self, project_id: int, title: str, content: str = None) -> int:
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO logs (project_id, title, content) VALUES (?, ?, ?)",
            (project_id, title, content)
        )
        self.conn.commit()
        return cursor.lastrowid

    def get_statistics(self) -> Dict:
        cursor = self.conn.cursor()

        cursor.execute('SELECT COUNT(*) FROM projects')
        total_projects = cursor.fetchone()[0]

        cursor.execute("SELECT status, COUNT(*) FROM projects GROUP BY status")
        by_status = {row[0]: row[1] for row in cursor.fetchall()}

        cursor.execute('SELECT COUNT(*) FROM items')
        total_items = cursor.fetchone()[0]

        return {
            'total_projects': total_projects,
            'by_status': by_status,
            'total_items': total_items
        }

    def close(self):
        if self.conn:
            self.conn.close()


if __name__ == '__main__':
    db = Database()
    print(f"Database initialized at {db.db_path}")
    print(f"Statistics: {db.get_statistics()}")
    db.close()
