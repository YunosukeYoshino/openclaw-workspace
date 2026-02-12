#!/usr/bin/env python3
"""
家事管理エージェント データベースモジュール
Household Management Agent Database Module
"""

import sqlite3
from datetime import datetime
from typing import List, Dict, Optional


class HouseholdDatabase:
    def __init__(self, db_path: str = "household.db"):
        self.db_path = db_path
        self.conn = None
        self.init_db()

    def connect(self):
        if self.conn is None:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row

    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None

    def init_db(self):
        self.connect()
        cursor = self.conn.cursor()

        # 家事タスクテーブル
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                frequency TEXT,
                due_date TEXT,
                priority TEXT DEFAULT 'medium',
                assigned_to TEXT,
                status TEXT DEFAULT 'pending',
                completed_at TEXT,
                recurring BOOLEAN DEFAULT 0,
                notes TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # メンテナンス記録テーブル
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS maintenance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item TEXT NOT NULL,
                type TEXT NOT NULL,
                location TEXT,
                scheduled_date TEXT,
                completed_date TEXT,
                cost REAL,
                contractor TEXT,
                notes TEXT,
                status TEXT DEFAULT 'scheduled',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 家具・備品テーブル
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS furniture (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                location TEXT,
                purchase_date TEXT,
                purchase_price REAL,
                warranty_expiry TEXT,
                condition TEXT DEFAULT 'good',
                notes TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 家事スケジュールテーブル
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS schedules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chore_id INTEGER,
                frequency TEXT,
                next_due TEXT,
                active BOOLEAN DEFAULT 1,
                FOREIGN KEY (chore_id) REFERENCES chores(id)
            )
        """)

        # インデックス
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_chores_status ON chores(status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_chores_due ON chores(due_date)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_maintenance_status ON maintenance(status)")

        self.conn.commit()

    def add_chore(self, name: str, category: str, **kwargs) -> int:
        self.connect()
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO chores (name, category, frequency, due_date, priority,
                              assigned_to, recurring, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (name, category, kwargs.get('frequency'), kwargs.get('due_date'),
              kwargs.get('priority', 'medium'), kwargs.get('assigned_to'),
              kwargs.get('recurring', False), kwargs.get('notes')))
        self.conn.commit()
        return cursor.lastrowid

    def complete_chore(self, chore_id: int) -> bool:
        self.connect()
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE chores SET status = 'completed', completed_at = ?
            WHERE id = ?
        """, (datetime.now().isoformat(), chore_id))
        self.conn.commit()
        return cursor.rowcount > 0

    def get_chores(self, status: Optional[str] = None) -> List[Dict]:
        self.connect()
        cursor = self.conn.cursor()
        if status:
            cursor.execute("SELECT * FROM chores WHERE status = ? ORDER BY due_date", (status,))
        else:
            cursor.execute("SELECT * FROM chores ORDER BY due_date")
        return [dict(row) for row in cursor.fetchall()]

    def add_maintenance(self, item: str, type_: str, **kwargs) -> int:
        self.connect()
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO maintenance (item, type, location, scheduled_date, cost,
                                    contractor, notes, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (item, type_, kwargs.get('location'), kwargs.get('scheduled_date'),
              kwargs.get('cost'), kwargs.get('contractor'), kwargs.get('notes'),
              kwargs.get('status', 'scheduled')))
        self.conn.commit()
        return cursor.lastrowid

    def get_maintenance(self, status: Optional[str] = None) -> List[Dict]:
        self.connect()
        cursor = self.conn.cursor()
        if status:
            cursor.execute("SELECT * FROM maintenance WHERE status = ?", (status,))
        else:
            cursor.execute("SELECT * FROM maintenance ORDER BY scheduled_date")
        return [dict(row) for row in cursor.fetchall()]

    def get_summary(self) -> Dict:
        self.connect()
        cursor = self.conn.cursor()

        cursor.execute("SELECT COUNT(*) as total FROM chores WHERE status = 'pending'")
        pending_chores = cursor.fetchone()['total']

        cursor.execute("SELECT COUNT(*) as total FROM maintenance WHERE status = 'scheduled'")
        scheduled_maintenance = cursor.fetchone()['total']

        cursor.execute("SELECT COUNT(*) as total FROM furniture")
        total_furniture = cursor.fetchone()['total']

        return {
            'pending_chores': pending_chores,
            'scheduled_maintenance': scheduled_maintenance,
            'total_furniture': total_furniture
        }
