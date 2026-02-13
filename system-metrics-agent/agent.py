#!/usr/bin/env python3
"""Agent: system-metrics-agent"""

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
logger = logging.getLogger('system-metrics-agent')


class SystemMetricsAgent:
    """Agent for システムモニタリング・アラートエージェント"""

    def __init__(self, db_path: str = None):
        self.name = "system-metrics-agent"
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
            logger.error(f"Failed to log: {err}")

    def add_entry(self, entry_type: str, content: str, title: str = None, priority: int = 0) -> Optional[int]:
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT INTO entries (type, title, content, priority) VALUES (?, ?, ?, ?)",
                (entry_type, title, content, priority)
            )
            self.conn.commit()
            return cursor.lastrowid
        except sqlite3.Error as err:
            logger.error(f"Failed to add entry: {err}")
            return None

    def get_entry(self, entry_id: int) -> Optional[Dict]:
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM entries WHERE id = ?", (entry_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
        except sqlite3.Error as err:
            logger.error(f"Failed to get entry: {err}")
            return None

    def list_entries(self, entry_type: str = None, status: str = "active", limit: int = 100) -> List[Dict]:
        try:
            cursor = self.conn.cursor()
            if entry_type:
                cursor.execute(
                    "SELECT * FROM entries WHERE type = ? AND status = ? ORDER BY created_at DESC LIMIT ?",
                    (entry_type, status, limit)
                )
            else:
                cursor.execute(
                    "SELECT * FROM entries WHERE status = ? ORDER BY created_at DESC LIMIT ?",
                    (status, limit)
                )
            return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as err:
            logger.error(f"Failed to list entries: {err}")
            return []

    def update_entry_status(self, entry_id: int, status: str) -> bool:
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "UPDATE entries SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (status, entry_id)
            )
            self.conn.commit()
            return True
        except sqlite3.Error as err:
            logger.error(f"Failed to update status: {err}")
            return False

    def get_settings(self) -> Dict[str, str]:
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT key, value FROM settings")
            return {row["key"]: row["value"] for row in cursor.fetchall()}
        except sqlite3.Error as err:
            logger.error(f"Failed to get settings: {err}")
            return {}

    def set_setting(self, key: str, value: str) -> bool:
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
                (key, value)
            )
            self.conn.commit()
            return True
        except sqlite3.Error as err:
            logger.error(f"Failed to set setting: {err}")
            return False

    def process_command(self, command: str, params: Dict = None) -> Dict:
        params = params or {}
        try:
            if command == "add":
                result = self.add_entry(
                    entry_type=params.get("type", "note"),
                    content=params.get("content", ""),
                    title=params.get("title"),
                    priority=params.get("priority", 0)
                )
                return {"success": bool(result), "data": {"id": result}}

            elif command == "get":
                result = self.get_entry(params.get("id"))
                return {"success": result is not None, "data": result}

            elif command == "list":
                result = self.list_entries(
                    entry_type=params.get("type"),
                    status=params.get("status", "active"),
                    limit=params.get("limit", 100)
                )
                return {"success": True, "data": result}

            elif command == "update_status":
                result = self.update_entry_status(
                    params.get("id"),
                    params.get("status", "active")
                )
                return {"success": result}

            elif command == "get_stats":
                cursor = self.conn.cursor()
                cursor.execute("SELECT COUNT(*) as count FROM entries WHERE status = 'active'")
                active_count = cursor.fetchone()["count"]
                cursor.execute("SELECT COUNT(*) as count FROM activity_log")
                activity_count = cursor.fetchone()["count"]
                return {
                    "success": True,
                    "data": {
                        "active_entries": active_count,
                        "total_activities": activity_count,
                        "settings": self.get_settings()
                    }
                }

            else:
                return {"success": False, "error": "Unknown command"}

        except Exception as err:
            logger.error(f"Command error: {err}")
            return {"success": False, "error": str(err)}

    def close(self):
        if self.conn:
            self.conn.close()


def main():
    agent = SystemMetricsAgent()
    if not agent.initialize_database():
        print("Failed to initialize database")
        sys.exit(1)

    if len(sys.argv) > 1:
        command = sys.argv[1]
        params = {}
        if len(sys.argv) > 2:
            for arg in sys.argv[2:]:
                if "=" in arg:
                    key, value = arg.split("=", 1)
                    params[key] = value

        result = agent.process_command(command, params)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    agent.close()


if __name__ == "__main__":
    main()
