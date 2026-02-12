#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Event Logger - Event history system"""

import json
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

@dataclass
class EventLog:
    id: int
    timestamp: datetime
    event_type: str
    source: str
    target: Optional[str]
    data: Dict[str, Any]

    def to_dict(self):
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat(),
            "event_type": self.event_type,
            "source": self.source,
            "target": self.target,
            "data": self.data
        }

class EventLogger:
    def __init__(self, db_path="/workspace/event_logger/event_log.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS event_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                event_type TEXT NOT NULL,
                source TEXT NOT NULL,
                target TEXT,
                data TEXT NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_timestamp
            ON event_logs(timestamp)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_event_type
            ON event_logs(event_type)
        ''')
        conn.commit()
        conn.close()

    def log(self, event_type: str, source: str, data: Dict[str, Any],
            target: Optional[str] = None) -> int:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO event_logs (timestamp, event_type, source, target, data)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            datetime.now().isoformat(),
            event_type,
            source,
            target,
            json.dumps(data, ensure_ascii=False)
        ))
        event_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return event_id

    def get_recent(self, limit: int = 100) -> List[EventLog]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, timestamp, event_type, source, target, data
            FROM event_logs
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (limit,))
        rows = cursor.fetchall()
        conn.close()
        return [
            EventLog(
                id=row[0],
                timestamp=datetime.fromisoformat(row[1]),
                event_type=row[2],
                source=row[3],
                target=row[4],
                data=json.loads(row[5])
            )
            for row in rows
        ]

    def get_stats(self) -> Dict[str, Any]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM event_logs')
        total = cursor.fetchone()[0]
        cursor.execute('''
            SELECT event_type, COUNT(*) as count
            FROM event_logs
            GROUP BY event_type
            ORDER BY count DESC
        ''')
        by_type = dict(cursor.fetchall())
        conn.close()
        return {
            "total_events": total,
            "by_type": by_type
        }

event_logger = EventLogger()

def main():
    event_logger.log("test", "main", {"message": "Hello"})
    event_logger.log("test", "main", {"message": "World"})

    logs = event_logger.get_recent()
    print(f"Logs: {len(logs)}")
    for log in logs:
        print(f"  {log.timestamp}: {log.data}")

    stats = event_logger.get_stats()
    print(f"Stats: {stats}")

if __name__ == "__main__":
    main()
