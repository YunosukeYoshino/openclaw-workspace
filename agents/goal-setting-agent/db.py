#!/usr/bin/env python3
"""
goal-setting-agent - Database Module

SQLite database operations for agent.
"""

import sqlite3
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path


class Database:
    """Database manager for goal-setting-agent"""

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
            "CREATE TABLE IF NOT EXISTS tasks ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT,"
            "title TEXT NOT NULL,"
            "description TEXT,"
            "category TEXT,"
            "priority INTEGER DEFAULT 0,"
            "status TEXT DEFAULT 'pending',"
            "due_date TEXT,"
            "completed_date TEXT,"
            "estimated_time INTEGER,"
            "actual_time INTEGER,"
            "tags TEXT,"
            "created_at TEXT DEFAULT CURRENT_TIMESTAMP,"
            "updated_at TEXT DEFAULT CURRENT_TIMESTAMP"
            ")"
        )

        cursor.execute(
            "CREATE TABLE IF NOT EXISTS time_entries ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT,"
            "task_id INTEGER,"
            "activity TEXT NOT NULL,"
            "start_time TEXT NOT NULL,"
            "end_time TEXT,"
            "duration INTEGER,"
            "notes TEXT,"
            "FOREIGN KEY (task_id) REFERENCES tasks(id)"
            ")"
        )

        cursor.execute(
            "CREATE TABLE IF NOT EXISTS sessions ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT,"
            "session_type TEXT,"
            "start_time TEXT NOT NULL,"
            "end_time TEXT,"
            "duration INTEGER,"
            "focus_score INTEGER DEFAULT 0,"
            "interruptions INTEGER DEFAULT 0,"
            "notes TEXT"
            ")"
        )

        self.conn.commit()

    def add_task(self, title: str, description: str = None,
                category: str = None, priority: int = 0,
                due_date: str = None, estimated_time: int = None,
                tags: str = None) -> int:
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO tasks (title, description, category, priority, due_date, estimated_time, tags) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (title, description, category, priority, due_date, estimated_time, tags)
        )
        self.conn.commit()
        return cursor.lastrowid

    def get_task(self, task_id: int) -> Optional[Dict]:
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM tasks WHERE id = ?', (task_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def list_tasks(self, status: str = None,
                   category: str = None, priority: int = None) -> List[Dict]:
        cursor = self.conn.cursor()
        query = 'SELECT * FROM tasks WHERE 1=1'
        params = []

        if status:
            query += ' AND status = ?'
            params.append(status)

        if category:
            query += ' AND category = ?'
            params.append(category)

        if priority is not None:
            query += ' AND priority >= ?'
            params.append(priority)

        query += ' ORDER BY priority DESC, due_date ASC, created_at ASC'
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

    def update_task(self, task_id: int, **kwargs) -> bool:
        valid_fields = ['title', 'description', 'category', 'priority',
                       'status', 'due_date', 'completed_date',
                       'estimated_time', 'actual_time', 'tags']
        update_fields = {k: v for k, v in kwargs.items() if k in valid_fields}

        if not update_fields:
            return False

        update_fields['updated_at'] = datetime.now().isoformat()
        set_clause = ', '.join([f'{k} = ?' for k in update_fields.keys()])
        values = list(update_fields.values()) + [task_id]

        cursor = self.conn.cursor()
        cursor.execute(
            f"UPDATE tasks SET {set_clause} WHERE id = ?",
            values
        )
        self.conn.commit()
        return cursor.rowcount > 0

    def delete_task(self, task_id: int) -> bool:
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM time_entries WHERE task_id = ?', (task_id,))
        cursor.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
        self.conn.commit()
        return cursor.rowcount > 0

    def start_time_entry(self, task_id: int, activity: str) -> int:
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO time_entries (task_id, activity, start_time) VALUES (?, ?, ?)",
            (task_id, activity, datetime.now().isoformat())
        )
        self.conn.commit()
        return cursor.lastrowid

    def end_time_entry(self, entry_id: int) -> bool:
        cursor = self.conn.cursor()
        end_time = datetime.now().isoformat()
        cursor.execute(
            "SELECT start_time FROM time_entries WHERE id = ?",
            (entry_id,)
        )
        row = cursor.fetchone()
        if not row:
            return False

        start_time = datetime.fromisoformat(row[0])
        duration = int((datetime.now() - start_time).total_seconds())

        cursor.execute(
            "UPDATE time_entries SET end_time = ?, duration = ? WHERE id = ?",
            (end_time, duration, entry_id)
        )
        self.conn.commit()
        return True

    def get_statistics(self) -> Dict:
        cursor = self.conn.cursor()

        cursor.execute('SELECT COUNT(*) FROM tasks WHERE status = "pending"')
        pending = cursor.fetchone()[0]

        cursor.execute('SELECT COUNT(*) FROM tasks WHERE status = "completed"')
        completed = cursor.fetchone()[0]

        cursor.execute('SELECT SUM(duration) FROM time_entries WHERE duration IS NOT NULL')
        total_seconds = cursor.fetchone()[0] or 0
        total_hours = round(total_seconds / 3600, 2)

        cursor.execute('SELECT COUNT(*) FROM sessions')
        total_sessions = cursor.fetchone()[0]

        return {
            'pending_tasks': pending,
            'completed_tasks': completed,
            'total_hours': total_hours,
            'total_sessions': total_sessions
        }

    def close(self):
        if self.conn:
            self.conn.close()


if __name__ == '__main__':
    db = Database()
    print(f"Database initialized at {db.db_path}")
    print(f"Statistics: {db.get_statistics()}")
    db.close()
