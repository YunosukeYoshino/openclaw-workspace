#!/usr/bin/env python3
"""
movie-tracker-agent - Database Module

SQLite database operations for the agent.
"""

import sqlite3
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path


class Database:
    """Database manager for movie-tracker-agent"""

    def __init__(self, db_path: str = None):
        """Initialize database"""
        if db_path is None:
            db_path = Path(__file__).parent / "data.db"
        self.db_path = db_path
        self.conn = None
        self._initialize()

    def _initialize(self):
        """Initialize database connection and create tables"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self._create_tables()

    def _create_tables(self):
        """Create database tables"""
        cursor = self.conn.cursor()

        # Main records table
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS records ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT,"
            "title TEXT NOT NULL,"
            "description TEXT,"
            "category TEXT,"
            "rating INTEGER DEFAULT 0,"
            "status TEXT DEFAULT 'watching',"
            "start_date TEXT,"
            "end_date TEXT,"
            "notes TEXT,"
            "tags TEXT,"
            "created_at TEXT DEFAULT CURRENT_TIMESTAMP,"
            "updated_at TEXT DEFAULT CURRENT_TIMESTAMP"
            ")"
        )

        # Categories table
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS categories ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT,"
            "name TEXT UNIQUE NOT NULL,"
            "description TEXT,"
            "created_at TEXT DEFAULT CURRENT_TIMESTAMP"
            ")"
        )

        # Tags table
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS tags ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT,"
            "name TEXT UNIQUE NOT NULL,"
            "created_at TEXT DEFAULT CURRENT_TIMESTAMP"
            ")"
        )

        # Record tags junction table
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS record_tags ("
            "record_id INTEGER,"
            "tag_id INTEGER,"
            "PRIMARY KEY (record_id, tag_id),"
            "FOREIGN KEY (record_id) REFERENCES records(id),"
            "FOREIGN KEY (tag_id) REFERENCES tags(id)"
            ")"
        )

        self.conn.commit()

    def add_record(self, title: str, description: str = None,
                   category: str = None, rating: int = 0,
                   status: str = 'watching', notes: str = None,
                   tags: List[str] = None) -> int:
        """Add a new record"""
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO records (title, description, category, rating, status, notes) VALUES (?, ?, ?, ?, ?, ?)",
            (title, description, category, rating, status, notes)
        )
        record_id = cursor.lastrowid

        # Add tags
        if tags:
            for tag_name in tags:
                tag_id = self._get_or_create_tag(tag_name)
                cursor.execute(
                    "INSERT INTO record_tags (record_id, tag_id) VALUES (?, ?)",
                    (record_id, tag_id)
                )

        self.conn.commit()
        return record_id

    def get_record(self, record_id: int) -> Optional[Dict]:
        """Get a record by ID"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM records WHERE id = ?', (record_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def list_records(self, status: str = None,
                    category: str = None) -> List[Dict]:
        """List records with optional filters"""
        cursor = self.conn.cursor()
        query = 'SELECT * FROM records WHERE 1=1'
        params = []

        if status:
            query += ' AND status = ?'
            params.append(status)

        if category:
            query += ' AND category = ?'
            params.append(category)

        query += ' ORDER BY created_at DESC'

        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

    def update_record(self, record_id: int, **kwargs) -> bool:
        """Update a record"""
        valid_fields = ['title', 'description', 'category', 'rating',
                       'status', 'start_date', 'end_date', 'notes']
        update_fields = {k: v for k, v in kwargs.items() if k in valid_fields}

        if not update_fields:
            return False

        update_fields['updated_at'] = datetime.now().isoformat()

        set_clause = ', '.join([f'{k} = ?' for k in update_fields.keys()])
        values = list(update_fields.values()) + [record_id]

        cursor = self.conn.cursor()
        cursor.execute(
            f"UPDATE records SET {set_clause} WHERE id = ?",
            values
        )
        self.conn.commit()
        return cursor.rowcount > 0

    def delete_record(self, record_id: int) -> bool:
        """Delete a record"""
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM record_tags WHERE record_id = ?', (record_id,))
        cursor.execute('DELETE FROM records WHERE id = ?', (record_id,))
        self.conn.commit()
        return cursor.rowcount > 0

    def get_statistics(self) -> Dict:
        """Get statistics"""
        cursor = self.conn.cursor()

        # Total records
        cursor.execute('SELECT COUNT(*) FROM records')
        total = cursor.fetchone()[0]

        # By status
        cursor.execute(
            "SELECT status, COUNT(*) as count FROM records GROUP BY status"
        )
        by_status = {row[0]: row[1] for row in cursor.fetchall()}

        # Average rating
        cursor.execute('SELECT AVG(rating) FROM records WHERE rating > 0')
        avg_rating = cursor.fetchone()[0] or 0

        return {
            'total': total,
            'by_status': by_status,
            'average_rating': round(avg_rating, 2)
        }

    def _get_or_create_tag(self, tag_name: str) -> int:
        """Get or create a tag"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT id FROM tags WHERE name = ?', (tag_name,))
        row = cursor.fetchone()

        if row:
            return row[0]

        cursor.execute('INSERT INTO tags (name) VALUES (?)', (tag_name,))
        self.conn.commit()
        return cursor.lastrowid

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()


if __name__ == '__main__':
    db = Database()
    print(f"Database initialized at {db.db_path}")
    print(f"Statistics: {db.get_statistics()}")
    db.close()
