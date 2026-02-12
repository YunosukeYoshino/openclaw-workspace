#!/usr/bin/env python3
"""
Database module for report-agent
"""

import sqlite3
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

class Database:
    """Database manager for report-agent"""

    def __init__(self, db_path: str = None):
        """Initialize database"""
        if db_path is None:
            db_path = Path(__file__).parent / "report-agent.db"
        self.db_path = db_path
        self._initialize_schema()

    def get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def execute(self, sql: str, params: tuple = None) -> sqlite3.Cursor:
        """Execute SQL statement"""
        conn = self.get_connection()
        cursor = conn.cursor()
        if params:
            cursor.execute(sql, params)
        else:
            cursor.execute(sql)
        conn.commit()
        return cursor

    def fetch_all(self, sql: str, params: tuple = None) -> List[sqlite3.Row]:
        """Fetch all rows"""
        conn = self.get_connection()
        cursor = conn.cursor()
        if params:
            cursor.execute(sql, params)
        else:
            cursor.execute(sql)
        results = cursor.fetchall()
        conn.close()
        return results

    def fetch_one(self, sql: str, params: tuple = None) -> Optional[sqlite3.Row]:
        """Fetch one row"""
        results = self.fetch_all(sql, params)
        return results[0] if results else None

    def insert(self, table: str, data: Dict[str, Any]) -> int:
        """Insert a record"""
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?'] * len(data))
        sql = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        cursor = self.execute(sql, tuple(data.values()))
        return cursor.lastrowid

    def update(self, table: str, record_id: int, data: Dict[str, Any]) -> bool:
        """Update a record"""
        set_clause = ', '.join([f"{k} = ?" for k in data.keys()])
        sql = f"UPDATE {table} SET {set_clause} WHERE id = ?"
        values = list(data.values()) + [record_id]
        self.execute(sql, tuple(values))
        return True

    def delete(self, table: str, record_id: int) -> bool:
        """Delete a record"""
        sql = f"DELETE FROM {table} WHERE id = ?"
        self.execute(sql, (record_id,))
        return True

    def get_by_id(self, table: str, record_id: int) -> Optional[Dict]:
        """Get a record by ID"""
        sql = f"SELECT * FROM {table} WHERE id = ?"
        row = self.fetch_one(sql, (record_id,))
        return dict(row) if row else None

    def list_all(self, table: str, limit: int = 100) -> List[Dict]:
        """List all records"""
        sql = f"SELECT * FROM {table} ORDER BY id DESC LIMIT ?"
        rows = self.fetch_all(sql, (limit,))
        return [dict(row) for row in rows]

    def search(self, table: str, field: str, query: str) -> List[Dict]:
        """Search records"""
        sql = f"SELECT * FROM {table} WHERE {field} LIKE ?"
        rows = self.fetch_all(sql, (f"%{query}%",))
        return [dict(row) for row in rows]

    def get_stats(self) -> Dict:
        """Get database statistics"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Get all table names
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]

        stats = {}
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            stats[table] = cursor.fetchone()[0]

        conn.close()
        return stats

    def _initialize_schema(self):
        """Initialize database schema"""
        self.execute('''
            CREATE TABLE IF NOT EXISTS report_agent (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')


# Convenience class for backward compatibility
class report_agentDB(Database):
    """Legacy name for Database class"""
    def __init__(self, db_path: str = None):
        super().__init__(db_path)

    def add_record(self, record: Dict[str, Any]) -> int:
        """Add a report record"""
        content = record.get('content', '')
        metadata = json.dumps({k: v for k, v in record.items() if k != 'content'})
        return self.insert('report_agent', {
            'content': content,
            'metadata': metadata
        })

    def get_all_records(self, limit: int = 100) -> List[Dict]:
        """Get all report records"""
        return self.list_all('report_agent', limit)


if __name__ == "__main__":
    db = report_agentDB()
    print("report-agent Database initialized")
    print(f"Database path: {db.db_path}")
    print(f"Stats: {db.get_stats()}")
