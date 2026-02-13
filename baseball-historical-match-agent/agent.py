#!/usr/bin/env python3
"""Agent: baseball-historical-match-agent"""

import os
import sys
import sqlite3
import logging
import json
from datetime import datetime
from typing import Optional, Dict, List, Any

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('baseball-historical-match-agent')


class BaseballHistoricalMatchAgent:
    """Agent for 野球歴史的名試合エージェント"""

    def __init__(self, db_path: str = None):
        self.name = "baseball-historical-match-agent"
        self.db_path = db_path or os.path.join(
            os.path.dirname(__file__),
            "data.db"
        )
        self.conn = None

    def initialize_database(self):
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
            cursor = self.conn.cursor()

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    type TEXT NOT NULL,
                    title TEXT,
                    content TEXT NOT NULL,
                    status TEXT DEFAULT 'active',
                    priority INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS activity_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    action TEXT NOT NULL,
                    details TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            self.conn.commit()
            logger.info("Database initialized")
            return True

        except sqlite3.Error as err:
            logger.error(f"Database init failed: {err}")
            return False

    def log_activity(self, action: str, details: str = None):
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT INTO activity_log (action, details) VALUES (?, ?)",
                (action, details)
            )
            self.conn.commit()
        except sqlite3.Error as err:
            logger.error(f"Activity log failed: {err}")

    def add_entry(self, type: str, title: str, content: str, priority: int = 0) -> Optional[int]:
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT INTO entries (type, title, content, priority) VALUES (?, ?, ?, ?)",
                (type, title, content, priority)
            )
            self.conn.commit()
            entry_id = cursor.lastrowid
            self.log_activity("add_entry", f"Added entry {entry_id}: {title}")
            logger.info(f"Added entry {entry_id}")
            return entry_id
        except sqlite3.Error as err:
            logger.error(f"Add entry failed: {err}")
            return None

    def get_entry(self, entry_id: int) -> Optional[Dict]:
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM entries WHERE id = ?", (entry_id,))
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None
        except sqlite3.Error as err:
            logger.error(f"Get entry failed: {err}")
            return None

    def list_entries(self, entry_type: str = None, status: str = None, limit: int = 100) -> List[Dict]:
        try:
            cursor = self.conn.cursor()
            query = "SELECT * FROM entries"
            params = []

            conditions = []
            if entry_type:
                conditions.append("type = ?")
                params.append(entry_type)
            if status:
                conditions.append("status = ?")
                params.append(status)

            if conditions:
                query += " WHERE " + " AND ".join(conditions)

            query += " ORDER BY created_at DESC LIMIT ?"
            params.append(limit)

            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except sqlite3.Error as err:
            logger.error(f"List entries failed: {err}")
            return []

    def update_entry_status(self, entry_id: int, status: str) -> bool:
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "UPDATE entries SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (status, entry_id)
            )
            self.conn.commit()
            self.log_activity("update_status", f"Updated entry {entry_id} to {status}")
            logger.info(f"Updated entry {entry_id} status to {status}")
            return True
        except sqlite3.Error as err:
            logger.error(f"Update status failed: {err}")
            return False

    def delete_entry(self, entry_id: int) -> bool:
        try:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM entries WHERE id = ?", (entry_id,))
            self.conn.commit()
            self.log_activity("delete_entry", f"Deleted entry {entry_id}")
            logger.info(f"Deleted entry {entry_id}")
            return True
        except sqlite3.Error as err:
            logger.error(f"Delete entry failed: {err}")
            return False

    def get_stats(self) -> Dict:
        try:
            cursor = self.conn.cursor()

            stats = {}
            cursor.execute("SELECT COUNT(*) FROM entries")
            stats['total_entries'] = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM entries WHERE status = 'active'")
            stats['active_entries'] = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM entries WHERE status = 'completed'")
            stats['completed_entries'] = cursor.fetchone()[0]

            cursor.execute("SELECT type, COUNT(*) as count FROM entries GROUP BY type")
            stats['by_type'] = {row[0]: row[1] for row in cursor.fetchall()}

            return stats
        except sqlite3.Error as err:
            logger.error(f"Get stats failed: {err}")
            return {}

    def search_entries(self, query: str, limit: int = 50) -> List[Dict]:
        try:
            cursor = self.conn.cursor()
            search_pattern = f"%{query}%"
            cursor.execute(
                "SELECT * FROM entries WHERE title LIKE ? OR content LIKE ? ORDER BY created_at DESC LIMIT ?",
                (search_pattern, search_pattern, limit)
            )
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except sqlite3.Error as err:
            logger.error(f"Search failed: {err}")
            return []

    def get_recent_activity(self, limit: int = 20) -> List[Dict]:
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT * FROM activity_log ORDER BY timestamp DESC LIMIT ?",
                (limit,)
            )
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except sqlite3.Error as err:
            logger.error(f"Get activity failed: {err}")
            return []

    def close(self):
        if self.conn:
            self.conn.close()


def main():
    agent = BaseballHistoricalMatchAgent()

    if not agent.initialize_database():
        print("Failed to initialize database")
        sys.exit(1)

    if len(sys.argv) < 2:
        print("Usage: python3 agent.py <command> [args...]")
        print("Commands: add, get, list, update_status, delete, get_stats, search, activity")
        sys.exit(1)

    command = sys.argv[1]

    if command == "add":
        type = sys.argv[2].split("=")[1] if len(sys.argv) > 2 and "=" in sys.argv[2] else "note"
        title = sys.argv[3].split("=")[1] if len(sys.argv) > 3 and "=" in sys.argv[3] else None
        content = sys.argv[4].split("=")[1] if len(sys.argv) > 4 and "=" in sys.argv[4] else ""
        priority = int(sys.argv[5].split("=")[1]) if len(sys.argv) > 5 and "=" in sys.argv[5] else 0
        entry_id = agent.add_entry(type, title, content, priority)
        if entry_id:
            print(f"Added entry {entry_id}")
        else:
            print("Failed to add entry")

    elif command == "get":
        entry_id = int(sys.argv[2].split("=")[1]) if len(sys.argv) > 2 and "=" in sys.argv[2] else 1
        entry = agent.get_entry(entry_id)
        if entry:
            print(json.dumps(entry, indent=2, default=str))
        else:
            print(f"Entry {entry_id} not found")

    elif command == "list":
        entry_type = sys.argv[2].split("=")[1] if len(sys.argv) > 2 and "=" in sys.argv[2] else None
        status = sys.argv[3].split("=")[1] if len(sys.argv) > 3 and "=" in sys.argv[3] else None
        limit = int(sys.argv[4].split("=")[1]) if len(sys.argv) > 4 and "=" in sys.argv[4] else 100
        entries = agent.list_entries(entry_type, status, limit)
        print(json.dumps(entries, indent=2, default=str))

    elif command == "update_status":
        entry_id = int(sys.argv[2].split("=")[1]) if len(sys.argv) > 2 and "=" in sys.argv[2] else 1
        status = sys.argv[3].split("=")[1] if len(sys.argv) > 3 and "=" in sys.argv[3] else "active"
        if agent.update_entry_status(entry_id, status):
            print(f"Updated entry {entry_id} status to {status}")
        else:
            print("Failed to update status")

    elif command == "delete":
        entry_id = int(sys.argv[2].split("=")[1]) if len(sys.argv) > 2 and "=" in sys.argv[2] else 1
        if agent.delete_entry(entry_id):
            print(f"Deleted entry {entry_id}")
        else:
            print("Failed to delete entry")

    elif command == "get_stats":
        stats = agent.get_stats()
        print(json.dumps(stats, indent=2))

    elif command == "search":
        query = sys.argv[2].split("=")[1] if len(sys.argv) > 2 and "=" in sys.argv[2] else ""
        limit = int(sys.argv[3].split("=")[1]) if len(sys.argv) > 3 and "=" in sys.argv[3] else 50
        results = agent.search_entries(query, limit)
        print(json.dumps(results, indent=2, default=str))

    elif command == "activity":
        limit = int(sys.argv[2].split("=")[1]) if len(sys.argv) > 2 and "=" in sys.argv[2] else 20
        activity = agent.get_recent_activity(limit)
        print(json.dumps(activity, indent=2, default=str))

    else:
        print(f"Unknown command: {command}")

    agent.close()


if __name__ == "__main__":
    main()
