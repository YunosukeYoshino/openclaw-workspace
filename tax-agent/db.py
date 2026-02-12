#!/usr/bin/env python3
"""
tax-agent database module
SQLite-based tax record management
"""

import sqlite3
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from pathlib import Path


class TaxDatabase:
    """SQLite database for tax records"""

    def __init__(self, db_path: str = None):
        """Initialize database connection"""
        if db_path is None:
            db_path = Path(__file__).parent / "tax.db"
        self.db_path = db_path
        self.conn = None
        self.connect()
        self.create_tables()

    def connect(self):
        """Create database connection"""
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()

    def create_tables(self):
        """Create necessary tables if they don't exist"""
        cursor = self.conn.cursor()

        # Tax records table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tax_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                year INTEGER NOT NULL,
                category TEXT NOT NULL,
                amount REAL NOT NULL,
                description TEXT,
                date_recorded TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                tags TEXT
            )
        """)

        # Categories table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                name_en TEXT NOT NULL,
                name_ja TEXT NOT NULL
            )
        """)

        # User settings table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_settings (
                user_id TEXT PRIMARY KEY,
                language TEXT DEFAULT 'ja',
                timezone TEXT DEFAULT 'UTC',
                currency TEXT DEFAULT 'JPY'
            )
        """)

        self.conn.commit()

        # Initialize default categories
        self._init_categories()

    def _init_categories(self):
        """Initialize default tax categories"""
        default_categories = [
            ('income', 'Income', '所得'),
            ('expense', 'Expense', '経費'),
            ('deduction', 'Deduction', '控除'),
            ('tax_paid', 'Tax Paid', '納税'),
            ('other', 'Other', 'その他'),
        ]

        cursor = self.conn.cursor()
        for cat_id, name_en, name_ja in default_categories:
            cursor.execute("""
                INSERT OR IGNORE INTO categories (id, name, name_en, name_ja)
                VALUES (?, ?, ?, ?)
            """, (cat_id, cat_id, name_en, name_ja))
        self.conn.commit()

    # User Settings
    def get_user_settings(self, user_id: str) -> Dict:
        """Get user settings"""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT * FROM user_settings WHERE user_id = ?",
            (user_id,)
        )
        row = cursor.fetchone()
        if row:
            return dict(row)
        return {
            'user_id': user_id,
            'language': 'ja',
            'timezone': 'UTC',
            'currency': 'JPY'
        }

    def set_user_language(self, user_id: str, language: str):
        """Set user language preference"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO user_settings (user_id, language)
            VALUES (?, COALESCE((SELECT language FROM user_settings WHERE user_id = ?), ?))
        """, (user_id, user_id, language))
        cursor.execute(
            "UPDATE user_settings SET language = ? WHERE user_id = ?",
            (language, user_id)
        )
        self.conn.commit()

    # Tax Records CRUD
    def add_record(self, user_id: str, year: int, category: str,
                   amount: float, description: str = None,
                   tags: str = None) -> int:
        """Add a new tax record"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO tax_records
            (user_id, year, category, amount, description, tags)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, year, category, amount, description, tags))
        self.conn.commit()
        return cursor.lastrowid

    def get_record(self, record_id: int) -> Optional[Dict]:
        """Get a single record by ID"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM tax_records WHERE id = ?", (record_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def get_user_records(self, user_id: str, year: int = None) -> List[Dict]:
        """Get all records for a user, optionally filtered by year"""
        cursor = self.conn.cursor()
        if year:
            cursor.execute("""
                SELECT * FROM tax_records
                WHERE user_id = ? AND year = ?
                ORDER BY date_recorded DESC
            """, (user_id, year))
        else:
            cursor.execute("""
                SELECT * FROM tax_records
                WHERE user_id = ?
                ORDER BY date_recorded DESC
            """, (user_id,))
        return [dict(row) for row in cursor.fetchall()]

    def update_record(self, record_id: int, **kwargs) -> bool:
        """Update a tax record"""
        allowed_fields = ['year', 'category', 'amount', 'description', 'tags']
        updates = {k: v for k, v in kwargs.items() if k in allowed_fields}

        if not updates:
            return False

        set_clause = ', '.join(f"{k} = ?" for k in updates.keys())
        values = list(updates.values()) + [record_id]

        cursor = self.conn.cursor()
        cursor.execute(
            f"UPDATE tax_records SET {set_clause} WHERE id = ?",
            values
        )
        self.conn.commit()
        return cursor.rowcount > 0

    def delete_record(self, record_id: int, user_id: str = None) -> bool:
        """Delete a tax record"""
        cursor = self.conn.cursor()
        if user_id:
            cursor.execute(
                "DELETE FROM tax_records WHERE id = ? AND user_id = ?",
                (record_id, user_id)
            )
        else:
            cursor.execute("DELETE FROM tax_records WHERE id = ?", (record_id,))
        self.conn.commit()
        return cursor.rowcount > 0

    # Query Methods
    def get_summary(self, user_id: str, year: int) -> Dict:
        """Get tax summary by category for a given year"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT category,
                   SUM(amount) as total,
                   COUNT(*) as count
            FROM tax_records
            WHERE user_id = ? AND year = ?
            GROUP BY category
        """, (user_id, year))

        summary = {}
        for row in cursor.fetchall():
            summary[row['category']] = {
                'total': row['total'] or 0,
                'count': row['count'] or 0
            }
        return summary

    def get_total_by_category(self, user_id: str, year: int,
                             category: str) -> float:
        """Get total amount for a specific category"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT SUM(amount) as total
            FROM tax_records
            WHERE user_id = ? AND year = ? AND category = ?
        """, (user_id, year, category))
        row = cursor.fetchone()
        return row['total'] or 0

    def search_records(self, user_id: str, keyword: str,
                      year: int = None) -> List[Dict]:
        """Search records by keyword in description or tags"""
        cursor = self.conn.cursor()
        pattern = f"%{keyword}%"

        if year:
            cursor.execute("""
                SELECT * FROM tax_records
                WHERE user_id = ? AND year = ?
                AND (description LIKE ? OR tags LIKE ?)
                ORDER BY date_recorded DESC
            """, (user_id, year, pattern, pattern))
        else:
            cursor.execute("""
                SELECT * FROM tax_records
                WHERE user_id = ?
                AND (description LIKE ? OR tags LIKE ?)
                ORDER BY date_recorded DESC
            """, (user_id, pattern, pattern))

        return [dict(row) for row in cursor.fetchall()]

    def get_years(self, user_id: str) -> List[int]:
        """Get list of years with records for a user"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT DISTINCT year FROM tax_records
            WHERE user_id = ?
            ORDER BY year DESC
        """, (user_id,))
        return [row['year'] for row in cursor.fetchall()]

    # Categories
    def get_categories(self, language: str = 'en') -> Dict[str, str]:
        """Get all category names in specified language"""
        cursor = self.conn.cursor()
        name_col = 'name_en' if language == 'en' else 'name_ja'
        cursor.execute(f"SELECT name, {name_col} FROM categories")
        return {row['name']: row[name_col] for row in cursor.fetchall()}

    def get_category_name(self, category_id: str,
                         language: str = 'en') -> str:
        """Get localized category name"""
        cursor = self.conn.cursor()
        name_col = 'name_en' if language == 'en' else 'name_ja'
        cursor.execute(f"""
            SELECT {name_col} FROM categories WHERE name = ?
        """, (category_id,))
        row = cursor.fetchone()
        return row[name_col] if row else category_id


# Convenience functions
def get_db(db_path: str = None) -> TaxDatabase:
    """Get a database instance"""
    return TaxDatabase(db_path)
