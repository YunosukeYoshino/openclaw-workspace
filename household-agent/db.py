#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Household Agent - SQLite Database
家事管理エージェント - SQLite データベース
"""

import sqlite3
from datetime import datetime
from typing import List, Dict, Optional
import os

class HouseholdDB:
    """Household Database Handler"""

    def __init__(self, db_path: str = None):
        """Initialize database"""
        if db_path is None:
            db_path = os.path.join(os.path.dirname(__file__), 'household.db')
        self.db_path = db_path
        self.init_db()

    def get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        """Initialize database tables"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Chores table (家事タスク)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                description TEXT,
                frequency TEXT,  -- daily, weekly, monthly, as_needed
                priority INTEGER DEFAULT 1,  -- 1-5
                status TEXT DEFAULT 'pending',  -- pending, in_progress, completed, skipped
                assigned_to TEXT,
                due_date DATE,
                completed_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Maintenance table (メンテナンス)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS maintenance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item TEXT NOT NULL,
                area TEXT,
                task TEXT NOT NULL,
                frequency TEXT,
                last_done DATE,
                next_due DATE,
                notes TEXT,
                priority INTEGER DEFAULT 2,
                status TEXT DEFAULT 'scheduled',  -- scheduled, overdue, completed
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Repairs table (修理)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS repairs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item TEXT NOT NULL,
                issue TEXT NOT NULL,
                severity TEXT,  -- minor, moderate, critical
                status TEXT DEFAULT 'open',  -- open, in_progress, completed, cancelled
                reported_date DATE DEFAULT (date('now')),
                scheduled_date DATE,
                completed_date DATE,
                cost REAL,
                contractor TEXT,
                description TEXT,
                resolution TEXT,
                photos TEXT,  -- JSON array of photo paths
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Supplies table (用品在庫)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS supplies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT,
                quantity INTEGER DEFAULT 0,
                unit TEXT,
                minimum_quantity INTEGER,
                location TEXT,
                last_restocked DATE,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Cleaning Schedule table (掃除スケジュール)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cleaning_schedule (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                area TEXT NOT NULL,
                task TEXT NOT NULL,
                frequency TEXT NOT NULL,
                day_of_week INTEGER,  -- 0-6 (Sunday-Saturday), null for daily/weekly
                day_of_month INTEGER,  -- 1-31, null for weekly
                assigned_to TEXT,
                estimated_duration INTEGER,  -- minutes
                last_completed DATE,
                next_due DATE,
                status TEXT DEFAULT 'scheduled',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        conn.commit()
        conn.close()

    # Chores Operations
    def add_chore(self, name: str, category: str, description: str = None,
                  frequency: str = None, priority: int = 1, assigned_to: str = None,
                  due_date: str = None) -> int:
        """Add a new chore"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO chores (name, category, description, frequency, priority, assigned_to, due_date)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (name, category, description, frequency, priority, assigned_to, due_date))
        chore_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return chore_id

    def get_chores(self, status: str = None, category: str = None) -> List[Dict]:
        """Get all chores or filter by status/category"""
        conn = self.get_connection()
        cursor = conn.cursor()

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
        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    def update_chore_status(self, chore_id: int, status: str) -> bool:
        """Update chore status"""
        conn = self.get_connection()
        cursor = conn.cursor()

        completed_at = 'CURRENT_TIMESTAMP' if status == 'completed' else 'NULL'

        cursor.execute(f'''
            UPDATE chores
            SET status = ?, completed_at = {completed_at}, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (status, chore_id))

        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return success

    # Maintenance Operations
    def add_maintenance(self, item: str, task: str, area: str = None,
                       frequency: str = None, last_done: str = None,
                       next_due: str = None, notes: str = None) -> int:
        """Add a new maintenance task"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO maintenance (item, area, task, frequency, last_done, next_due, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (item, area, task, frequency, last_done, next_due, notes))
        maint_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return maint_id

    def get_maintenance(self, status: str = None) -> List[Dict]:
        """Get all maintenance tasks"""
        conn = self.get_connection()
        cursor = conn.cursor()

        query = 'SELECT * FROM maintenance'
        if status:
            query += ' WHERE status = ?'
            cursor.execute(query, (status,))
        else:
            cursor.execute(query)

        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    def update_maintenance(self, maint_id: int, last_done: str, next_due: str = None) -> bool:
        """Update maintenance completion"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            UPDATE maintenance
            SET last_done = ?, next_due = ?, status = 'scheduled', updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (last_done, next_due, maint_id))

        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return success

    # Repairs Operations
    def add_repair(self, item: str, issue: str, severity: str = 'moderate',
                  description: str = None, scheduled_date: str = None) -> int:
        """Add a new repair record"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO repairs (item, issue, severity, description, scheduled_date)
            VALUES (?, ?, ?, ?, ?)
        ''', (item, issue, severity, description, scheduled_date))
        repair_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return repair_id

    def get_repairs(self, status: str = None) -> List[Dict]:
        """Get all repairs"""
        conn = self.get_connection()
        cursor = conn.cursor()

        query = 'SELECT * FROM repairs'
        if status:
            query += ' WHERE status = ?'
            cursor.execute(query, (status,))
        else:
            cursor.execute(query)

        query += ' ORDER BY severity DESC, reported_date ASC'

        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    def update_repair(self, repair_id: int, **kwargs) -> bool:
        """Update repair details"""
        conn = self.get_connection()
        cursor = conn.cursor()

        allowed_fields = ['status', 'scheduled_date', 'completed_date', 'cost',
                         'contractor', 'resolution', 'severity']
        updates = []
        params = []

        for field, value in kwargs.items():
            if field in allowed_fields and value is not None:
                updates.append(f'{field} = ?')
                params.append(value)

        if updates:
            params.append(repair_id)
            cursor.execute(f'''
                UPDATE repairs
                SET {', '.join(updates)}, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', params)

        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return success

    # Supplies Operations
    def add_supply(self, name: str, category: str = None, quantity: int = 0,
                   unit: str = None, minimum_quantity: int = None,
                   location: str = None) -> int:
        """Add a supply item"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO supplies (name, category, quantity, unit, minimum_quantity, location)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (name, category, quantity, unit, minimum_quantity, location))
        supply_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return supply_id

    def get_supplies(self, low_stock: bool = False) -> List[Dict]:
        """Get all supplies or only low stock items"""
        conn = self.get_connection()
        cursor = conn.cursor()

        if low_stock:
            cursor.execute('''
                SELECT * FROM supplies
                WHERE quantity <= COALESCE(minimum_quantity, 0)
                ORDER BY category, name
            ''')
        else:
            cursor.execute('SELECT * FROM supplies ORDER BY category, name')

        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    def update_supply_quantity(self, supply_id: int, quantity: int, restocked: bool = False) -> bool:
        """Update supply quantity"""
        conn = self.get_connection()
        cursor = conn.cursor()

        if restocked:
            cursor.execute('''
                UPDATE supplies
                SET quantity = ?, last_restocked = date('now'), updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (quantity, supply_id))
        else:
            cursor.execute('''
                UPDATE supplies
                SET quantity = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (quantity, supply_id))

        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return success

    # Cleaning Schedule Operations
    def add_cleaning_task(self, area: str, task: str, frequency: str,
                          day_of_week: int = None, day_of_month: int = None,
                          assigned_to: str = None, estimated_duration: int = None) -> int:
        """Add a cleaning task to schedule"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO cleaning_schedule
            (area, task, frequency, day_of_week, day_of_month, assigned_to, estimated_duration)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (area, task, frequency, day_of_week, day_of_month, assigned_to, estimated_duration))
        task_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return task_id

    def get_cleaning_schedule(self) -> List[Dict]:
        """Get cleaning schedule"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM cleaning_schedule ORDER BY day_of_week, area')
        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    def get_summary(self) -> Dict:
        """Get household summary"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM chores WHERE status = 'pending'")
        pending_chores = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM repairs WHERE status IN ('open', 'in_progress')")
        open_repairs = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM maintenance WHERE next_due <= date('now', '+7 days')")
        upcoming_maintenance = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM supplies WHERE quantity <= COALESCE(minimum_quantity, 0)")
        low_stock = cursor.fetchone()[0]

        conn.close()

        return {
            'pending_chores': pending_chores,
            'open_repairs': open_repairs,
            'upcoming_maintenance': upcoming_maintenance,
            'low_stock_items': low_stock
        }


if __name__ == '__main__':
    # Test database
    db = HouseholdDB()
    print("Database initialized successfully!")
    print("\nSummary:", db.get_summary())
