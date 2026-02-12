#!/usr/bin/env python3
"""
meal-planning-agent - Database Module

SQLite database operations for agent.
"""

import sqlite3
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path


class Database:
    """Database manager for meal-planning-agent"""

    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = Path(__file__).parent / "data.db"
        self.db_path = db_path
        self.conn = None
        self._initialize()

    def _initialize(self):
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self._create_tables()

    def _create_tables(self):
        cursor = self.conn.cursor()

        cursor.execute(
            "CREATE TABLE IF NOT EXISTS chores ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT,"
            "title TEXT NOT NULL,"
            "description TEXT,"
            "category TEXT,"
            "frequency TEXT DEFAULT 'once',"
            "priority INTEGER DEFAULT 0,"
            "status TEXT DEFAULT 'pending',"
            "due_date TEXT,"
            "completed_date TEXT,"
            "assigned_to TEXT,"
            "notes TEXT,"
            "created_at TEXT DEFAULT CURRENT_TIMESTAMP,"
            "updated_at TEXT DEFAULT CURRENT_TIMESTAMP"
            ")"
        )

        cursor.execute(
            "CREATE TABLE IF NOT EXISTS shopping_items ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT,"
            "name TEXT NOT NULL,"
            "category TEXT,"
            "quantity INTEGER DEFAULT 1,"
            "unit TEXT,"
            "priority INTEGER DEFAULT 0,"
            "status TEXT DEFAULT 'needed',"
            "estimated_price REAL,"
            "notes TEXT,"
            "created_at TEXT DEFAULT CURRENT_TIMESTAMP"
            ")"
        )

        cursor.execute(
            "CREATE TABLE IF NOT EXISTS bills ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT,"
            "name TEXT NOT NULL,"
            "category TEXT,"
            "amount REAL NOT NULL,"
            "due_date TEXT NOT NULL,"
            "status TEXT DEFAULT 'pending',"
            "paid_date TEXT,"
            "payment_method TEXT,"
            "notes TEXT,"
            "created_at TEXT DEFAULT CURRENT_TIMESTAMP"
            ")"
        )

        self.conn.commit()

    def add_chore(self, title: str, description: str = None,
                  category: str = None, frequency: str = 'once',
                  priority: int = 0, due_date: str = None,
                  assigned_to: str = None) -> int:
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO chores (title, description, category, frequency, priority, due_date, assigned_to) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (title, description, category, frequency, priority, due_date, assigned_to)
        )
        self.conn.commit()
        return cursor.lastrowid

    def get_chore(self, chore_id: int) -> Optional[Dict]:
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM chores WHERE id = ?', (chore_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def list_chores(self, status: str = None,
                    category: str = None) -> List[Dict]:
        cursor = self.conn.cursor()
        query = 'SELECT * FROM chores WHERE 1=1'
        params = []

        if status:
            query += ' AND status = ?'
            params.append(status)

        if category:
            query += ' AND category = ?'
            params.append(category)

        query += ' ORDER BY priority DESC, due_date ASC'
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

    def update_chore(self, chore_id: int, **kwargs) -> bool:
        valid_fields = ['title', 'description', 'category', 'frequency',
                       'priority', 'status', 'due_date', 'completed_date',
                       'assigned_to', 'notes']
        update_fields = {k: v for k, v in kwargs.items() if k in valid_fields}

        if not update_fields:
            return False

        update_fields['updated_at'] = datetime.now().isoformat()
        set_clause = ', '.join([f'{k} = ?' for k in update_fields.keys()])
        values = list(update_fields.values()) + [chore_id]

        cursor = self.conn.cursor()
        cursor.execute(
            f"UPDATE chores SET {set_clause} WHERE id = ?",
            values
        )
        self.conn.commit()
        return cursor.rowcount > 0

    def add_shopping_item(self, name: str, category: str = None,
                         quantity: int = 1, unit: str = None,
                         priority: int = 0, estimated_price: float = None) -> int:
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO shopping_items (name, category, quantity, unit, priority, estimated_price) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (name, category, quantity, unit, priority, estimated_price)
        )
        self.conn.commit()
        return cursor.lastrowid

    def list_shopping_items(self, status: str = None,
                            category: str = None) -> List[Dict]:
        cursor = self.conn.cursor()
        query = 'SELECT * FROM shopping_items WHERE 1=1'
        params = []

        if status:
            query += ' AND status = ?'
            params.append(status)

        if category:
            query += ' AND category = ?'
            params.append(category)

        query += ' ORDER BY priority DESC, created_at ASC'
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

    def add_bill(self, name: str, amount: float, due_date: str,
                 category: str = None, payment_method: str = None) -> int:
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO bills (name, category, amount, due_date, payment_method) "
            "VALUES (?, ?, ?, ?, ?)",
            (name, category, amount, due_date, payment_method)
        )
        self.conn.commit()
        return cursor.lastrowid

    def list_bills(self, status: str = None) -> List[Dict]:
        cursor = self.conn.cursor()
        query = 'SELECT * FROM bills WHERE 1=1'
        params = []

        if status:
            query += ' AND status = ?'
            params.append(status)

        query += ' ORDER BY due_date ASC'
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

    def get_statistics(self) -> Dict:
        cursor = self.conn.cursor()

        cursor.execute('SELECT COUNT(*) FROM chores WHERE status = "pending"')
        pending_chores = cursor.fetchone()[0]

        cursor.execute('SELECT COUNT(*) FROM shopping_items WHERE status = "needed"')
        needed_items = cursor.fetchone()[0]

        cursor.execute('SELECT SUM(amount) FROM bills WHERE status = "pending"')
        pending_bills = cursor.fetchone()[0] or 0

        return {
            'pending_chores': pending_chores,
            'needed_shopping_items': needed_items,
            'pending_bill_amount': round(pending_bills, 2)
        }

    def close(self):
        if self.conn:
            self.conn.close()


if __name__ == '__main__':
    db = Database()
    print(f"Database initialized at {db.db_path}")
    print(f"Statistics: {db.get_statistics()}")
    db.close()
