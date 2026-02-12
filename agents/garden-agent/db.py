#!/usr/bin/env python3
"""
園芸記録エージェント データベースモジュール
Garden Log Agent Database Module
"""

import sqlite3
from datetime import datetime
from typing import List, Dict, Optional


class GardenDatabase:
    def __init__(self, db_path: str = "garden.db"):
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

        # 植物テーブル
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS plants (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                scientific_name TEXT,
                type TEXT,
                location TEXT,
                planting_date TEXT,
                flowering_season TEXT,
                notes TEXT,
                status TEXT DEFAULT 'alive',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 園芸記録テーブル
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS activities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                plant_id INTEGER,
                type TEXT NOT NULL,
                description TEXT,
                date TEXT DEFAULT CURRENT_TIMESTAMP,
                notes TEXT,
                FOREIGN KEY (plant_id) REFERENCES plants(id)
            )
        """)

        # 水やりスケジュールテーブル
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS watering_schedule (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                plant_id INTEGER,
                frequency TEXT,
                last_watered TEXT,
                next_watering TEXT,
                notes TEXT,
                FOREIGN KEY (plant_id) REFERENCES plants(id)
            )
        """)

        # 肥料記録テーブル
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS fertilizing_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                plant_id INTEGER,
                fertilizer_type TEXT,
                amount TEXT,
                date TEXT DEFAULT CURRENT_TIMESTAMP,
                notes TEXT,
                FOREIGN KEY (plant_id) REFERENCES plants(id)
            )
        """)

        # インデックス
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_activities_plant ON activities(plant_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_activities_date ON activities(date)")

        self.conn.commit()

    def add_plant(self, name: str, **kwargs) -> int:
        self.connect()
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO plants (name, scientific_name, type, location, planting_date,
                              flowering_season, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (name, kwargs.get('scientific_name'), kwargs.get('type'),
              kwargs.get('location'), kwargs.get('planting_date'),
              kwargs.get('flowering_season'), kwargs.get('notes')))
        self.conn.commit()
        return cursor.lastrowid

    def get_plants(self) -> List[Dict]:
        self.connect()
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM plants WHERE status = 'alive' ORDER BY name")
        return [dict(row) for row in cursor.fetchall()]

    def add_activity(self, plant_id: int, type_: str, description: str = None, **kwargs) -> int:
        self.connect()
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO activities (plant_id, type, description, date, notes)
            VALUES (?, ?, ?, ?, ?)
        """, (plant_id, type_, description, kwargs.get('date'), kwargs.get('notes')))
        self.conn.commit()
        return cursor.lastrowid

    def log_watering(self, plant_id: int, notes: str = None) -> int:
        self.connect()
        cursor = self.conn.cursor()
        now = datetime.now().isoformat()
        cursor.execute("""
            INSERT INTO watering_schedule (plant_id, last_watered, notes)
            VALUES (?, ?, ?)
        """, (plant_id, now, notes))
        self.conn.commit()
        return cursor.lastrowid

    def log_fertilizing(self, plant_id: int, fertilizer_type: str, amount: str = None, notes: str = None) -> int:
        self.connect()
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO fertilizing_log (plant_id, fertilizer_type, amount, notes)
            VALUES (?, ?, ?, ?)
        """, (plant_id, fertilizer_type, amount, notes))
        self.conn.commit()
        return cursor.lastrowid

    def get_activities(self, plant_id: int = None, limit: int = 20) -> List[Dict]:
        self.connect()
        cursor = self.conn.cursor()
        if plant_id:
            cursor.execute("""
                SELECT a.*, p.name as plant_name FROM activities a
                LEFT JOIN plants p ON a.plant_id = p.id
                WHERE a.plant_id = ? ORDER BY a.date DESC LIMIT ?
            """, (plant_id, limit))
        else:
            cursor.execute("""
                SELECT a.*, p.name as plant_name FROM activities a
                LEFT JOIN plants p ON a.plant_id = p.id
                ORDER BY a.date DESC LIMIT ?
            """, (limit,))
        return [dict(row) for row in cursor.fetchall()]

    def get_summary(self) -> Dict:
        self.connect()
        cursor = self.conn.cursor()

        cursor.execute("SELECT COUNT(*) as total FROM plants WHERE status = 'alive'")
        total_plants = cursor.fetchone()['total']

        cursor.execute("""
            SELECT type, COUNT(*) as count FROM plants
            WHERE status = 'alive' GROUP BY type
        """)
        by_type = {row['type']: row['count'] for row in cursor.fetchall()}

        return {
            'total_plants': total_plants,
            'by_type': by_type
        }
