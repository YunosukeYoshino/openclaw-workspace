#!/usr/bin/env python3
"""
コンテキスト認識エージェント - Context Awareness Agent

ユーザーの現在の状況を認識して適切なアクションを提案するエージェント。
"""

import json
import sqlite3
import logging
from datetime import datetime
from typing import Optional, Dict, Any, List


class ContextAwarenessAgent:
    """
    コンテキスト認識エージェント

    ユーザーの現在の状況を認識して適切なアクションを提案するエージェント。
    """

    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize the agent

        Args:
            db_path: Path to database file
        """
        self.name = "context-awareness-agent"
        self.db_path = db_path or f"{self.name}.db"
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row

        # Setup logging
        self.logger = logging.getLogger(self.name)
        self.logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        self.logger.addHandler(handler)

        # Initialize database tables
        self._init_db()

        self.logger.info(f"{name} initialized")

    def _init_db(self) -> None:
        """Initialize database tables."""
        cursor = self.conn.cursor()

        # Main entries table
        table_name = self.name
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

        self.conn.commit()

    def add_entry(self, title: str, content: str, category: Optional[str] = None, tags: Optional[List[str]] = None) -> int:
        """
        Add a new entry

        Args:
            title: Entry title
            content: Entry content
            category: Entry category
            tags: List of tags

        Returns:
            Entry ID
        """
        cursor = self.conn.cursor()
        table_name = self.name
        sql = "INSERT INTO " + table_name + " (title, content, category, tags) VALUES (?, ?, ?, ?)"
        cursor.execute(sql, (title, content, category, json.dumps(tags) if tags else None))
        self.conn.commit()

        entry_id = cursor.lastrowid
        self._log_activity("add_entry", {"entry_id": entry_id, "title": title})
        self.logger.info(f"Added entry: {title}")

        return entry_id

    def get_entry(self, entry_id: int) -> Optional[Dict[str, Any]]:
        """
        Get an entry by ID

        Args:
            entry_id: Entry ID

        Returns:
            Entry data or None
        """
        cursor = self.conn.cursor()
        table_name = self.name
        sql = "SELECT * FROM " + table_name + " WHERE id = ?"
        cursor.execute(sql, (entry_id,))
        row = cursor.fetchone()

        if row:
            columns = [desc[0] for desc in cursor.description]
            entry = dict(zip(columns, row))
            if entry.get('tags'):
                entry['tags'] = json.loads(entry['tags'])
            return entry
        return None

    def list_entries(self, status: str = 'active', limit: int = 100) -> List[Dict[str, Any]]:
        """
        List entries

        Args:
            status: Filter by status
            limit: Maximum number of entries

        Returns:
            List of entries
        """
        cursor = self.conn.cursor()
        table_name = self.name
        sql = "SELECT * FROM " + table_name + " WHERE status = ? ORDER BY created_at DESC LIMIT ?"
        cursor.execute(sql, (status, limit))

        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]

        entries = []
        for row in rows:
            entry = dict(zip(columns, row))
            if entry.get('tags'):
                entry['tags'] = json.loads(entry['tags'])
            entries.append(entry)

        return entries

    def update_entry(self, entry_id: int, **kwargs) -> bool:
        """
        Update an entry

        Args:
            entry_id: Entry ID
            **kwargs: Fields to update

        Returns:
            True if successful
        """
        cursor = self.conn.cursor()

        fields = []
        values = []
        for key, value in kwargs.items():
            if key in ['title', 'content', 'category', 'status', 'tags']:
                fields.append(key + " = ?")
                values.append(json.dumps(value) if key == 'tags' else value)

        if fields:
            values.append(entry_id)
            table_name = self.name
            sql = "UPDATE " + table_name + " SET " + ", ".join(fields) + ", updated_at = CURRENT_TIMESTAMP WHERE id = ?"
            cursor.execute(sql, values)
            self.conn.commit()

            self._log_activity("update_entry", {"entry_id": entry_id, "fields": list(kwargs.keys())})
            self.logger.info(f"Updated entry: {entry_id}")

            return True
        return False

    def delete_entry(self, entry_id: int) -> bool:
        """
        Delete an entry (soft delete)

        Args:
            entry_id: Entry ID

        Returns:
            True if successful
        """
        return self.update_entry(entry_id, status='deleted')

    def search_entries(self, query: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Search entries

        Args:
            query: Search query
            limit: Maximum number of entries

        Returns:
            List of matching entries
        """
        cursor = self.conn.cursor()
        pattern = "%" + query + "%"
        table_name = self.name
        sql = "SELECT * FROM " + table_name + " WHERE status = 'active' AND (title LIKE ? OR content LIKE ?) ORDER BY created_at DESC LIMIT ?"
        cursor.execute(sql, (pattern, pattern, limit))

        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]

        entries = []
        for row in rows:
            entry = dict(zip(columns, row))
            if entry.get('tags'):
                entry['tags'] = json.loads(entry['tags'])
            entries.append(entry)

        return entries

    def set_metadata(self, key: str, value: str) -> None:
        """Set metadata."""
        cursor = self.conn.cursor()
        table_name = self.name
        sql = "INSERT OR REPLACE INTO " + table_name + "_metadata (key, value, updated_at) VALUES (?, ?, CURRENT_TIMESTAMP)"
        cursor.execute(sql, (key, value))
        self.conn.commit()

    def get_metadata(self, key: str) -> Optional[str]:
        """Get metadata."""
        cursor = self.conn.cursor()
        table_name = self.name
        sql = "SELECT value FROM " + table_name + "_metadata WHERE key = ?"
        cursor.execute(sql, (key,))
        row = cursor.fetchone()
        return row[0] if row else None

    def _log_activity(self, action: str, details: Optional[Dict[str, Any]] = None) -> None:
        """Log activity."""
        cursor = self.conn.cursor()
        table_name = self.name
        sql = "INSERT INTO " + table_name + "_activity (action, details) VALUES (?, ?)"
        cursor.execute(sql, (action, json.dumps(details) if details else None))
        self.conn.commit()

    def get_activity_log(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get activity log."""
        cursor = self.conn.cursor()
        table_name = self.name
        sql = "SELECT * FROM " + table_name + "_activity ORDER BY timestamp DESC LIMIT ?"
        cursor.execute(sql, (limit,))

        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]

        activities = []
        for row in rows:
            activity = dict(zip(columns, row))
            if activity.get('details'):
                activity['details'] = json.loads(activity['details'])
            activities.append(activity)

        return activities

    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics."""
        cursor = self.conn.cursor()

        # Total entries
        table_name = self.name
        cursor.execute("SELECT COUNT(*) as total FROM " + table_name)
        total_entries = cursor.fetchone()['total']

        # Activity count
        cursor.execute("SELECT COUNT(*) as total FROM " + table_name + "_activity")
        total_activity = cursor.fetchone()['total']

        return {
            'total_entries': total_entries,
            'total_activity': total_activity
        }

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main processing function

        Args:
            input_data: Input data dictionary

        Returns:
            Processing result
        """
        action = input_data.get('action', 'default')

        if action == 'add':
            return {
                "success": self.add_entry(
                    title=input_data.get('title', ''),
                    content=input_data.get('content', ''),
                    category=input_data.get('category'),
                    tags=input_data.get('tags')
                ),
                "action": "add_entry"
            }
        elif action == 'get':
            entry = self.get_entry(input_data.get('entry_id', 0))
            return {"success": entry is not None, "data": entry, "action": "get_entry"}
        elif action == 'list':
            entries = self.list_entries(
                status=input_data.get('status', 'active'),
                limit=input_data.get('limit', 100)
            )
            return {"success": True, "data": entries, "action": "list_entries", "count": len(entries)}
        elif action == 'update':
            entry_id = input_data.get('entry_id', 0)
            update_data = {k: v for k, v in input_data.items() if k not in ['action', 'entry_id']}
            return {"success": self.update_entry(entry_id, **update_data), "action": "update_entry"}
        elif action == 'delete':
            return {"success": self.delete_entry(input_data.get('entry_id', 0)), "action": "delete_entry"}
        elif action == 'search':
            entries = self.search_entries(
                query=input_data.get('query', ''),
                limit=input_data.get('limit', 50)
            )
            return {"success": True, "data": entries, "action": "search_entries", "count": len(entries)}

        # Default action
        return {
            "success": True,
            "message": f"{name} is ready",
            "agent": self.name,
            "timestamp": datetime.now().isoformat()
        }

    def shutdown(self) -> None:
        """Shutdown the agent."""
        self.conn.close()
        self.logger.info(f"{name} shutdown")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description='コンテキスト認識エージェント')
    parser.add_argument('--action', default='status', help='Action to perform')
    parser.add_argument('--title', help='Entry title')
    parser.add_argument('--content', help='Entry content')
    parser.add_argument('--entry-id', type=int, help='Entry ID')
    parser.add_argument('--query', help='Search query')
    parser.add_argument('--limit', type=int, default=100, help='Result limit')

    args = parser.parse_args()

    agent = ContextAwarenessAgent()

    input_data = {
        'action': args.action,
        'title': args.title,
        'content': args.content,
        'entry_id': args.entry_id,
        'query': args.query,
        'limit': args.limit
    }

    result = agent.process(input_data)
    print(json.dumps(result, ensure_ascii=False, indent=2))

    agent.shutdown()


if __name__ == '__main__':
    main()
