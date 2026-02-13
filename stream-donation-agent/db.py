#!/usr/bin/env python3
"""Database Module for stream-donation-agent"""

import sqlite3
import os
import json
from typing import Optional, List, Dict, Any
from contextlib import contextmanager
from datetime import datetime
import logging

logger = logging.getLogger('stream-donation-agent')


class DatabaseManager:
    def __init__(self, db_path: str = None):
        self.db_path = db_path or os.path.join(
            os.path.dirname(__file__),
            "data.db"
        )
        self.conn = None

    def connect(self) -> bool:
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
            return True
        except sqlite3.Error as err:
            logger.error(f"Connection failed: {err}")
            return False

    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None

    @contextmanager
    def get_cursor(self):
        cursor = None
        try:
            if not self.conn:
                self.connect()
            cursor = self.conn.cursor()
            yield cursor
            self.conn.commit()
        except sqlite3.Error as err:
            if self.conn:
                self.conn.rollback()
            logger.error(f"Database error: {err}")
            raise
        finally:
            if cursor:
                cursor.close()

    def initialize_schema(self) -> bool:
        try:
            with self.get_cursor() as cursor:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS entries (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        type TEXT NOT NULL CHECK(type IN ('idea','goal','project','vision','note','task')),
                        title TEXT,
                        content TEXT NOT NULL,
                        status TEXT DEFAULT 'active' CHECK(status IN ('active','archived','completed')),
                        priority INTEGER DEFAULT 0,
                        metadata TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS tags (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT UNIQUE NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS entry_tags (
                        entry_id INTEGER NOT NULL,
                        tag_id INTEGER NOT NULL,
                        PRIMARY KEY (entry_id, tag_id),
                        FOREIGN KEY (entry_id) REFERENCES entries(id) ON DELETE CASCADE,
                        FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
                    )
                """)

                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS activity_log (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        action TEXT NOT NULL,
                        entity_type TEXT,
                        entity_id INTEGER,
                        details TEXT,
                        metadata TEXT,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS settings (
                        key TEXT PRIMARY KEY,
                        value TEXT NOT NULL,
                        value_type TEXT DEFAULT 'string',
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                cursor.execute("CREATE INDEX IF NOT EXISTS idx_entries_type ON entries(type)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_entries_status ON entries(status)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_activity_timestamp ON activity_log(timestamp)")

                logger.info("Schema initialized")
                return True

        except sqlite3.Error as err:
            logger.error(f"Schema init failed: {err}")
            return False

    def add_entry(self, entry_type: str, content: str, title: str = None,
                  priority: int = 0, metadata: Dict = None) -> Optional[int]:
        try:
            with self.get_cursor() as cursor:
                metadata_json = json.dumps(metadata) if metadata else None
                cursor.execute(
                    "INSERT INTO entries (type, title, content, priority, metadata) VALUES (?, ?, ?, ?, ?)",
                    (entry_type, title, content, priority, metadata_json)
                )
                return cursor.lastrowid
        except sqlite3.Error as err:
            logger.error(f"Failed to add entry: {err}")
            return None

    def get_entry(self, entry_id: int) -> Optional[Dict]:
        try:
            with self.get_cursor() as cursor:
                cursor.execute("SELECT * FROM entries WHERE id = ?", (entry_id,))
                row = cursor.fetchone()
                if not row:
                    return None

                entry = dict(row)
                if entry.get("metadata"):
                    entry["metadata"] = json.loads(entry["metadata"])

                cursor.execute("""
                    SELECT t.name FROM tags t
                    JOIN entry_tags et ON t.id = et.tag_id
                    WHERE et.entry_id = ?
                """, (entry_id,))
                entry["tags"] = [row["name"] for row in cursor.fetchall()]

                return entry
        except sqlite3.Error as err:
            logger.error(f"Failed to get entry: {err}")
            return None

    def update_entry(self, entry_id: int, title: str = None, content: str = None,
                     status: str = None, priority: int = None, metadata: Dict = None) -> bool:
        try:
            updates = []
            params = []

            if title is not None:
                updates.append("title = ?")
                params.append(title)
            if content is not None:
                updates.append("content = ?")
                params.append(content)
            if status is not None:
                updates.append("status = ?")
                params.append(status)
            if priority is not None:
                updates.append("priority = ?")
                params.append(priority)
            if metadata is not None:
                updates.append("metadata = ?")
                params.append(json.dumps(metadata))

            if not updates:
                return False

            updates.append("updated_at = CURRENT_TIMESTAMP")
            params.append(entry_id)

            with self.get_cursor() as cursor:
                cursor.execute(
                    "UPDATE entries SET {0} WHERE id = ?".format(', '.join(updates)),
                    params
                )
                return True
        except sqlite3.Error as err:
            logger.error(f"Failed to update entry: {err}")
            return False

    def list_entries(self, entry_type: str = None, status: str = None,
                     priority_min: int = None, limit: int = 100, offset: int = 0) -> List[Dict]:
        try:
            conditions = []
            params = []

            if entry_type:
                conditions.append("type = ?")
                params.append(entry_type)
            if status:
                conditions.append("status = ?")
                params.append(status)
            if priority_min is not None:
                conditions.append("priority >= ?")
                params.append(priority_min)

            where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

            with self.get_cursor() as cursor:
                cursor.execute("""
                    SELECT * FROM entries
                    {0}
                    ORDER BY priority DESC, created_at DESC
                    LIMIT ? OFFSET ?
                """.format(where_clause), params + [limit, offset])

                rows = cursor.fetchall()
                results = []
                for row in rows:
                    entry = dict(row)
                    if entry.get("metadata"):
                        entry["metadata"] = json.loads(entry["metadata"])
                    results.append(entry)

                return results
        except sqlite3.Error as err:
            logger.error(f"Failed to list entries: {err}")
            return []

    def delete_entry(self, entry_id: int) -> bool:
        try:
            with self.get_cursor() as cursor:
                cursor.execute("DELETE FROM entries WHERE id = ?", (entry_id,))
                return True
        except sqlite3.Error as err:
            logger.error(f"Failed to delete entry: {err}")
            return False

    def add_tag(self, tag_name: str) -> Optional[int]:
        try:
            with self.get_cursor() as cursor:
                cursor.execute(
                    "INSERT OR IGNORE INTO tags (name) VALUES (?)",
                    (tag_name,)
                )
                cursor.execute("SELECT id FROM tags WHERE name = ?", (tag_name,))
                row = cursor.fetchone()
                return row["id"] if row else None
        except sqlite3.Error as err:
            logger.error(f"Failed to add tag: {err}")
            return None

    def link_tag_to_entry(self, entry_id: int, tag_name: str) -> bool:
        try:
            tag_id = self.add_tag(tag_name)
            if not tag_id:
                return False

            with self.get_cursor() as cursor:
                cursor.execute(
                    "INSERT OR IGNORE INTO entry_tags (entry_id, tag_id) VALUES (?, ?)",
                    (entry_id, tag_id)
                )
                return True
        except sqlite3.Error as err:
            logger.error(f"Failed to link tag: {err}")
            return False

    def get_tags(self) -> List[Dict]:
        try:
            with self.get_cursor() as cursor:
                cursor.execute("""
                    SELECT t.*, COUNT(et.entry_id) as entry_count
                    FROM tags t
                    LEFT JOIN entry_tags et ON t.id = et.tag_id
                    GROUP BY t.id
                    ORDER BY t.name
                """)
                return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as err:
            logger.error(f"Failed to get tags: {err}")
            return []

    def log_activity(self, action: str, entity_type: str = None, entity_id: int = None,
                     details: str = None, metadata: Dict = None):
        try:
            with self.get_cursor() as cursor:
                cursor.execute(
                    "INSERT INTO activity_log (action, entity_type, entity_id, details, metadata) VALUES (?, ?, ?, ?, ?)",
                    (action, entity_type, entity_id, details, json.dumps(metadata) if metadata else None)
                )
        except sqlite3.Error as err:
            logger.error(f"Failed to log activity: {err}")

    def get_activity_log(self, limit: int = 100, entity_type: str = None,
                         entity_id: int = None) -> List[Dict]:
        try:
            conditions = []
            params = []

            if entity_type:
                conditions.append("entity_type = ?")
                params.append(entity_type)
            if entity_id:
                conditions.append("entity_id = ?")
                params.append(entity_id)

            where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

            with self.get_cursor() as cursor:
                cursor.execute("""
                    SELECT * FROM activity_log
                    {0}
                    ORDER BY timestamp DESC
                    LIMIT ?
                """.format(where_clause), params + [limit])

                rows = cursor.fetchall()
                results = []
                for row in rows:
                    entry = dict(row)
                    if entry.get("metadata"):
                        entry["metadata"] = json.loads(entry["metadata"])
                    results.append(entry)

                return results
        except sqlite3.Error as err:
            logger.error(f"Failed to get activity log: {err}")
            return []

    def set_setting(self, key: str, value: Any, value_type: str = None) -> bool:
        try:
            if value_type is None:
                if isinstance(value, bool):
                    value_type = "boolean"
                    value = "true" if value else "false"
                elif isinstance(value, int):
                    value_type = "integer"
                    value = str(value)
                elif isinstance(value, float):
                    value_type = "float"
                    value = str(value)
                elif isinstance(value, (dict, list)):
                    value_type = "json"
                    value = json.dumps(value)
                else:
                    value_type = "string"

            with self.get_cursor() as cursor:
                cursor.execute(
                    "INSERT OR REPLACE INTO settings (key, value, value_type, updated_at) VALUES (?, ?, ?, CURRENT_TIMESTAMP)",
                    (key, value, value_type)
                )
                return True
        except sqlite3.Error as err:
            logger.error(f"Failed to set setting: {err}")
            return False

    def get_setting(self, key: str) -> Optional[Any]:
        try:
            with self.get_cursor() as cursor:
                cursor.execute("SELECT * FROM settings WHERE key = ?", (key,))
                row = cursor.fetchone()
                if not row:
                    return None

                value = row["value"]
                value_type = row["value_type"]

                if value_type == "boolean":
                    return value.lower() == "true"
                elif value_type == "integer":
                    return int(value)
                elif value_type == "float":
                    return float(value)
                elif value_type == "json":
                    return json.loads(value)
                else:
                    return value
        except sqlite3.Error as err:
            logger.error(f"Failed to get setting: {err}")
            return None

    def get_all_settings(self) -> Dict[str, Any]:
        try:
            with self.get_cursor() as cursor:
                cursor.execute("SELECT key, value, value_type FROM settings")
                settings = {}
                for row in cursor.fetchall():
                    settings[row["key"]] = self.get_setting(row["key"])
                return settings
        except sqlite3.Error as err:
            logger.error(f"Failed to get settings: {err}")
            return {}

    def get_stats(self) -> Dict:
        try:
            with self.get_cursor() as cursor:
                cursor.execute("SELECT type, COUNT(*) as count FROM entries GROUP BY type")
                entries_by_type = {row["type"]: row["count"] for row in cursor.fetchall()}

                cursor.execute("SELECT status, COUNT(*) as count FROM entries GROUP BY status")
                entries_by_status = {row["status"]: row["count"] for row in cursor.fetchall()}

                cursor.execute("SELECT COUNT(*) as count FROM entries")
                total_entries = cursor.fetchone()["count"]

                cursor.execute("SELECT COUNT(*) as count FROM tags")
                total_tags = cursor.fetchone()["count"]

                cursor.execute("SELECT COUNT(*) as count FROM activity_log")
                total_activities = cursor.fetchone()["count"]

                return {
                    "total_entries": total_entries,
                    "entries_by_type": entries_by_type,
                    "entries_by_status": entries_by_status,
                    "total_tags": total_tags,
                    "total_activities": total_activities
                }
        except sqlite3.Error as err:
            logger.error(f"Failed to get stats: {err}")
            return {}


def main():
    db = DatabaseManager()
    if db.connect():
        db.initialize_schema()
        print("Database Statistics:")
        print(json.dumps(db.get_stats(), indent=2))
        print("\nAll Settings:")
        print(json.dumps(db.get_all_settings(), indent=2))
        db.close()


if __name__ == "__main__":
    main()
