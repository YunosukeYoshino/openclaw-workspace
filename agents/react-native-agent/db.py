#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
react-native-agent - Database Module
SQLite database management for react-native-agent
"""

import sqlite3
import json
from datetime import datetime
from typing import Optional, List, Dict, Any
from pathlib import Path

class ReactNativeAgentDB:
    """Database manager for react-native-agent"""

    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = str(Path(__file__).parent / "react-native-agent.db")

        self.db_path = db_path
        self.conn = None
        self.connect()
        self.init_tables()

    def connect(self):
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row

    def init_tables(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT,
                content TEXT,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_type TEXT,
                status TEXT DEFAULT "pending",
                result TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                level TEXT,
                message TEXT,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        self.conn.commit()

    def insert_data(self, data_type: str, content: str, metadata: Dict = None) -> int:
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO data (type, content, metadata)
            VALUES (?, ?, ?)
        """, (data_type, content, json.dumps(metadata or dict())))
        self.conn.commit()
        return cursor.lastrowid

    def query_data(self, data_type: str = None, limit: int = 100) -> List[Dict]:
        cursor = self.conn.cursor()
        if data_type:
            cursor.execute('SELECT * FROM data WHERE type = ? ORDER BY created_at DESC LIMIT ?',
                         (data_type, limit))
        else:
            cursor.execute('SELECT * FROM data ORDER BY created_at DESC LIMIT ?', (limit,))
        return [dict(row) for row in cursor.fetchall()]

    def create_task(self, task_type: str, metadata: Dict = None) -> int:
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO tasks (task_type, status)
            VALUES (?, "pending")
        """, (task_type,))
        self.conn.commit()
        return cursor.lastrowid

    def update_task(self, task_id: int, status: str, result: Dict = None) -> bool:
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE tasks
            SET status = ?, result = ?, completed_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (status, json.dumps(result or dict()), task_id))
        self.conn.commit()
        return cursor.rowcount > 0

    def log(self, level: str, message: str, metadata: Dict = None):
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO logs (level, message, metadata)
            VALUES (?, ?, ?)
        """, (level, message, json.dumps(metadata or dict())))
        self.conn.commit()

    def get_stats(self) -> Dict[str, Any]:
        cursor = self.conn.cursor()
        cursor.execute('SELECT COUNT(*) as count FROM data')
        data_count = cursor.fetchone()["count"]
        cursor.execute('SELECT COUNT(*) as count FROM tasks WHERE status = "pending"')
        pending_tasks = cursor.fetchone()["count"]
        cursor.execute('SELECT COUNT(*) as count FROM tasks WHERE status = "completed"')
        completed_tasks = cursor.fetchone()["count"]
        return {
            "data_count": data_count,
            "pending_tasks": pending_tasks,
            "completed_tasks": completed_tasks,
            "total_tasks": pending_tasks + completed_tasks
        }

    def close(self):
        if self.conn:
            self.conn.close()

if __name__ == "__main__":
    db = ReactNativeAgentDB()
    print("Database for react-native-agent initialized at " + str(db.db_path))
    print("Stats: " + str(db.get_stats()))
    db.close()
