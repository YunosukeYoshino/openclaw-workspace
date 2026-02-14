#!/usr/bin/env python3
"""
threat-detection-agent

脅威検知エージェント。脅威のリアルタイム検知。
"""

import sqlite3
import asyncio
from pathlib import Path
from typing import Optional, List, Dict, Any
import json

class ThreatDetectionAgentAgent:
    def __init__(self, db_path: str = None):
        self.db_path = db_path or str(Path(__file__).parent / "threat-detection-agent.db")
        self.init_database()

    def init_database(self):
        """データベース初期化"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                status TEXT DEFAULT 'pending',
                priority INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT NOT NULL,
                data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()
        conn.close()

    def add_task(self, title: str, description: str = None, priority: int = 0) -> int:
        """タスクを追加"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            'INSERT INTO tasks (title, description, priority) VALUES (?, ?, ?)',
            (title, description, priority)
        )

        task_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return task_id

    def get_tasks(self, status: str = None) -> List[Dict[str, Any]]:
        """タスクを取得"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        if status:
            cursor.execute('SELECT * FROM tasks WHERE status = ?', (status,))
        else:
            cursor.execute('SELECT * FROM tasks')

        rows = cursor.fetchall()
        conn.close()

        columns = ['id', 'title', 'description', 'status', 'priority', 'created_at', 'updated_at']
        return [dict(zip(columns, row)) for row in rows]

    def update_task_status(self, task_id: int, status: str) -> bool:
        """タスクのステータスを更新"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            'UPDATE tasks SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
            (status, task_id)
        )

        affected = cursor.rowcount
        conn.commit()
        conn.close()

        return affected > 0

    def log_event(self, event_type: str, data: Dict[str, Any] = None) -> int:
        """イベントをログ"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            'INSERT INTO events (event_type, data) VALUES (?, ?)',
            (event_type, json.dumps(data) if data else None)
        )

        event_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return event_id

    def get_stats(self) -> Dict[str, Any]:
        """統計情報を取得"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('SELECT COUNT(*) FROM tasks')
        total_tasks = cursor.fetchone()[0]

        cursor.execute('SELECT COUNT(*) FROM tasks WHERE status = "pending"')
        pending_tasks = cursor.fetchone()[0]

        cursor.execute('SELECT COUNT(*) FROM tasks WHERE status = "completed"')
        completed_tasks = cursor.fetchone()[0]

        cursor.execute('SELECT COUNT(*) FROM events')
        total_events = cursor.fetchone()[0]

        conn.close()

        return {
            'total_tasks': total_tasks,
            'pending_tasks': pending_tasks,
            'completed_tasks': completed_tasks,
            'total_events': total_events
        }

async def main():
    agent = ThreatDetectionAgentAgent()

    print("AGENT_NAME is running...")

    stats = agent.get_stats()
    print("Stats:", stats)

if __name__ == "__main__":
    asyncio.run(main())
