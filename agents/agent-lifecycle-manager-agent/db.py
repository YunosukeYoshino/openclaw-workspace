#!/usr/bin/env python3
"""
Database module for エージェントライフサイクルマネージャーエージェント
"""

import sqlite3
import logging
from datetime import datetime
from typing import Optional, Dict, Any


class AgentLifecycleManagerAgentDB:
    """
    Database handler for エージェントライフサイクルマネージャーエージェント
    """

    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize database

        Args:
            db_path: Path to database file
        """
        self.db_path = db_path or "agent-lifecycle-manager-agent.db"
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row

        # Setup logging
        self.logger = logging.getLogger(f"{self.db_path}.db")
        self.logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        self.logger.addHandler(handler)

        # Initialize tables
        self._init_tables()

        self.logger.info(f"Database initialized: {self.db_path}")

    def _init_tables(self) -> None:
        """Initialize database tables."""
        cursor = self.conn.cursor()

        table_name = "agent-lifecycle-manager-agent"

        # Main entries table
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS " + table_name + " (" +
            "id INTEGER PRIMARY KEY AUTOINCREMENT, " +
            "title TEXT, " +
            "content TEXT NOT NULL, " +
            "category TEXT, " +
            "tags TEXT, " +
            "status TEXT DEFAULT 'active', " +
            "created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, " +
            "updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP" +
            ")"
        )

        # Metadata table
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS " + table_name + "_metadata (" +
            "id INTEGER PRIMARY KEY AUTOINCREMENT, " +
            "key TEXT UNIQUE NOT NULL, " +
            "value TEXT, " +
            "updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP" +
            ")"
        )

        # Activity log table
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS " + table_name + "_activity (" +
            "id INTEGER PRIMARY KEY AUTOINCREMENT, " +
            "action TEXT NOT NULL, " +
            "details TEXT, " +
            "timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP" +
            ")"
        )

        # Tags table
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS " + table_name + "_tags (" +
            "id INTEGER PRIMARY KEY AUTOINCREMENT, " +
            "name TEXT UNIQUE NOT NULL, " +
            "created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP" +
            ")"
        )

        # Entry tags junction table
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS " + table_name + "_entry_tags (" +
            "entry_id INTEGER, " +
            "tag_id INTEGER, " +
            "PRIMARY KEY (entry_id, tag_id), " +
            "FOREIGN KEY (entry_id) REFERENCES " + table_name + "(id) ON DELETE CASCADE, " +
            "FOREIGN KEY (tag_id) REFERENCES " + table_name + "_tags(id) ON DELETE CASCADE" +
            ")"
        )

        self.conn.commit()

    def execute(self, query: str, params: Optional[tuple] = None) -> sqlite3.Cursor:
        """Execute a query."""
        cursor = self.conn.cursor()
        cursor.execute(query, params or ())
        return cursor

    def fetchall(self, query: str, params: Optional[tuple] = None):
        """Fetch all rows."""
        cursor = self.conn.execute(query, params or ())
        return cursor.fetchall()

    def fetchone(self, query: str, params: Optional[tuple] = None):
        """Fetch one row."""
        cursor = self.conn.execute(query, params or ())
        return cursor.fetchone()

    def commit(self) -> None:
        """Commit transactions."""
        self.conn.commit()

    def close(self) -> None:
        """Close database connection."""
        self.conn.close()

    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics."""
        cursor = self.conn.cursor()

        table_name = "agent-lifecycle-manager-agent"

        # Total entries
        cursor.execute("SELECT COUNT(*) as total FROM " + table_name)
        total_entries = cursor.fetchone()['total']

        # Tag count
        cursor.execute("SELECT COUNT(*) as total FROM " + table_name + "_tags")
        total_tags = cursor.fetchone()['total']

        # Activity count
        cursor.execute("SELECT COUNT(*) as total FROM " + table_name + "_activity")
        total_activity = cursor.fetchone()['total']

        return {
            'total_entries': total_entries,
            'total_tags': total_tags,
            'total_activity': total_activity
        }

    def backup(self, backup_path: str) -> bool:
        """Backup database."""
        try:
            backup = sqlite3.connect(backup_path)
            self.conn.backup(backup)
            backup.close()
            self.logger.info(f"Database backed up to: {backup_path}")
            return True
        except Exception as e:
            self.logger.error(f"Backup failed: {e}")
            return False


def main():
    db = AgentLifecycleManagerAgentDB()
    print(f"Database initialized for agent-lifecycle-manager-agent")


if __name__ == "__main__":
    main()
