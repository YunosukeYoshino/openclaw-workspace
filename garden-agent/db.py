#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Garden Agent - SQLite Database
園芸記録エージェント - SQLite データベース
"""

import sqlite3
from datetime import datetime
from typing import List, Dict, Optional
import os

class GardenDB:
    """Garden Database Handler"""

    def __init__(self, db_path: str = None):
        """Initialize database"""
        if db_path is None:
            db_path = os.path.join(os.path.dirname(__file__), 'garden.db')
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

        # Plants table (植物)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS plants (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                scientific_name TEXT,
                variety TEXT,
                category TEXT,  -- vegetable, flower, herb, tree, shrub, etc.
                location TEXT,
                planting_date DATE,
                source TEXT,  -- seed, seedling, cutting, purchased
                status TEXT DEFAULT 'active',  -- active, harvested, dead, dormant
                notes TEXT,
                photo_path TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Plant Care table (植物ケア)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS plant_care (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                plant_id INTEGER,
                care_type TEXT NOT NULL,  -- watering, fertilizing, pruning, pest_control
                care_date DATE DEFAULT (date('now')),
                notes TEXT,
                next_due_date DATE,
                FOREIGN KEY (plant_id) REFERENCES plants(id)
            )
        ''')

        # Harvests table (収穫)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS harvests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                plant_id INTEGER,
                harvest_date DATE DEFAULT (date('now')),
                quantity REAL,
                unit TEXT,  -- kg, g, pieces, bunch
                quality TEXT,  -- excellent, good, fair, poor
                notes TEXT,
                FOREIGN KEY (plant_id) REFERENCES plants(id)
            )
        ''')

        # Garden Activities table (園芸活動)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS garden_activities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                activity_type TEXT NOT NULL,  -- sowing, transplanting, weeding, mulching, etc.
                activity_date DATE DEFAULT (date('now')),
                area TEXT,
                plant_id INTEGER,
                description TEXT,
                duration INTEGER,  -- minutes
                weather TEXT,
                notes TEXT,
                FOREIGN KEY (plant_id) REFERENCES plants(id)
            )
        ''')

        # Pests and Diseases table (害虫・病気)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pests_diseases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                plant_id INTEGER,
                pest_disease_name TEXT NOT NULL,
                type TEXT,  -- pest, disease
                detected_date DATE DEFAULT (date('now')),
                severity TEXT,  -- mild, moderate, severe
                treatment TEXT,
                treatment_date DATE,
                resolved_date DATE,
                status TEXT DEFAULT 'active',  -- active, resolved, monitoring
                notes TEXT,
                FOREIGN KEY (plant_id) REFERENCES plants(id)
            )
        ''')

        # Seeds table (種子)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS seeds (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                plant_name TEXT NOT NULL,
                variety TEXT,
                quantity INTEGER,
                purchase_date DATE,
                source TEXT,
                expiry_date DATE,
                storage_location TEXT,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Watering Schedule table (水やりスケジュール)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS watering_schedule (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                plant_id INTEGER,
                frequency INTEGER,  -- days between watering
                last_watered DATE,
                next_watering DATE,
                notes TEXT,
                FOREIGN KEY (plant_id) REFERENCES plants(id)
            )
        ''')

        conn.commit()
        conn.close()

    # Plants Operations
    def add_plant(self, name: str, category: str, scientific_name: str = None,
                  variety: str = None, location: str = None,
                  planting_date: str = None, source: str = None,
                  notes: str = None, photo_path: str = None) -> int:
        """Add a new plant"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO plants (name, scientific_name, variety, category, location,
                              planting_date, source, notes, photo_path)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (name, scientific_name, variety, category, location,
              planting_date, source, notes, photo_path))
        plant_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return plant_id

    def get_plants(self, category: str = None, status: str = None) -> List[Dict]:
        """Get all plants or filter by category/status"""
        conn = self.get_connection()
        cursor = conn.cursor()

        query = 'SELECT * FROM plants WHERE 1=1'
        params = []

        if category:
            query += ' AND category = ?'
            params.append(category)
        if status:
            query += ' AND status = ?'
            params.append(status)

        query += ' ORDER BY name'

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    def get_plant(self, plant_id: int) -> Optional[Dict]:
        """Get a specific plant by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM plants WHERE id = ?', (plant_id,))
        row = cursor.fetchone()
        conn.close()

        return dict(row) if row else None

    def update_plant(self, plant_id: int, **kwargs) -> bool:
        """Update plant details"""
        conn = self.get_connection()
        cursor = conn.cursor()

        allowed_fields = ['name', 'scientific_name', 'variety', 'category',
                         'location', 'planting_date', 'source', 'status',
                         'notes', 'photo_path']
        updates = []
        params = []

        for field, value in kwargs.items():
            if field in allowed_fields and value is not None:
                updates.append(f'{field} = ?')
                params.append(value)

        if updates:
            params.append(plant_id)
            cursor.execute(f'''
                UPDATE plants
                SET {', '.join(updates)}, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', params)

        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return success

    # Plant Care Operations
    def add_care(self, plant_id: int, care_type: str, notes: str = None,
                next_due: str = None) -> int:
        """Add a care record"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO plant_care (plant_id, care_type, notes, next_due_date)
            VALUES (?, ?, ?, ?)
        ''', (plant_id, care_type, notes, next_due))
        care_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return care_id

    def get_plant_care(self, plant_id: int, care_type: str = None) -> List[Dict]:
        """Get care records for a plant"""
        conn = self.get_connection()
        cursor = conn.cursor()

        query = 'SELECT * FROM plant_care WHERE plant_id = ?'
        params = [plant_id]

        if care_type:
            query += ' AND care_type = ?'
            params.append(care_type)

        query += ' ORDER BY care_date DESC'

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    # Harvests Operations
    def add_harvest(self, plant_id: int, quantity: float, unit: str,
                   quality: str = 'good', notes: str = None) -> int:
        """Add a harvest record"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO harvests (plant_id, quantity, unit, quality, notes)
            VALUES (?, ?, ?, ?, ?)
        ''', (plant_id, quantity, unit, quality, notes))
        harvest_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return harvest_id

    def get_harvests(self, plant_id: int = None) -> List[Dict]:
        """Get all harvests or filter by plant"""
        conn = self.get_connection()
        cursor = conn.cursor()

        if plant_id:
            cursor.execute('''
                SELECT * FROM harvests
                WHERE plant_id = ?
                ORDER BY harvest_date DESC
            ''', (plant_id,))
        else:
            cursor.execute('SELECT * FROM harvests ORDER BY harvest_date DESC')

        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    # Garden Activities Operations
    def add_activity(self, activity_type: str, area: str = None,
                    plant_id: int = None, description: str = None,
                    duration: int = None, weather: str = None,
                    notes: str = None) -> int:
        """Add a garden activity"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO garden_activities
            (activity_type, area, plant_id, description, duration, weather, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (activity_type, area, plant_id, description, duration, weather, notes))
        activity_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return activity_id

    def get_activities(self, activity_type: str = None, plant_id: int = None) -> List[Dict]:
        """Get garden activities"""
        conn = self.get_connection()
        cursor = conn.cursor()

        query = 'SELECT * FROM garden_activities WHERE 1=1'
        params = []

        if activity_type:
            query += ' AND activity_type = ?'
            params.append(activity_type)
        if plant_id:
            query += ' AND plant_id = ?'
            params.append(plant_id)

        query += ' ORDER BY activity_date DESC'

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    # Pests and Diseases Operations
    def add_pest_disease(self, plant_id: int, pest_disease_name: str,
                        type: str, severity: str = 'moderate',
                        treatment: str = None) -> int:
        """Add a pest/disease record"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO pests_diseases
            (plant_id, pest_disease_name, type, severity, treatment)
            VALUES (?, ?, ?, ?, ?)
        ''', (plant_id, pest_disease_name, type, severity, treatment))
        pd_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return pd_id

    def get_pests_diseases(self, plant_id: int = None, status: str = None) -> List[Dict]:
        """Get pests/diseases records"""
        conn = self.get_connection()
        cursor = conn.cursor()

        query = 'SELECT * FROM pests_diseases WHERE 1=1'
        params = []

        if plant_id:
            query += ' AND plant_id = ?'
            params.append(plant_id)
        if status:
            query += ' AND status = ?'
            params.append(status)

        query += ' ORDER BY detected_date DESC'

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    def update_pest_disease(self, pd_id: int, **kwargs) -> bool:
        """Update pest/disease record"""
        conn = self.get_connection()
        cursor = conn.cursor()

        allowed_fields = ['status', 'treatment', 'treatment_date', 'resolved_date', 'severity']
        updates = []
        params = []

        for field, value in kwargs.items():
            if field in allowed_fields and value is not None:
                updates.append(f'{field} = ?')
                params.append(value)

        if updates:
            params.append(pd_id)
            cursor.execute(f'''
                UPDATE pests_diseases
                SET {', '.join(updates)}
                WHERE id = ?
            ''', params)

        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return success

    # Seeds Operations
    def add_seed(self, plant_name: str, quantity: int, variety: str = None,
                source: str = None, expiry_date: str = None,
                storage_location: str = None, notes: str = None) -> int:
        """Add seeds to inventory"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO seeds (plant_name, variety, quantity, source, expiry_date, storage_location, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (plant_name, variety, quantity, source, expiry_date, storage_location, notes))
        seed_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return seed_id

    def get_seeds(self, plant_name: str = None) -> List[Dict]:
        """Get all seeds or filter by plant name"""
        conn = self.get_connection()
        cursor = conn.cursor()

        if plant_name:
            cursor.execute('SELECT * FROM seeds WHERE plant_name LIKE ?', (f'%{plant_name}%',))
        else:
            cursor.execute('SELECT * FROM seeds ORDER BY plant_name')

        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    # Watering Schedule Operations
    def set_watering_schedule(self, plant_id: int, frequency: int,
                             last_watered: str = None, notes: str = None) -> int:
        """Set watering schedule for a plant"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO watering_schedule (plant_id, frequency, last_watered, notes)
            VALUES (?, ?, ?, ?)
        ''', (plant_id, frequency, last_watered, notes))
        schedule_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return schedule_id

    def get_watering_schedule(self) -> List[Dict]:
        """Get all watering schedules"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT ws.*, p.name as plant_name
            FROM watering_schedule ws
            JOIN plants p ON ws.plant_id = p.id
            ORDER BY ws.next_watering
        ''')
        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    def get_summary(self) -> Dict:
        """Get garden summary"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM plants WHERE status = 'active'")
        active_plants = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM pests_diseases WHERE status = 'active'")
        active_pests = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM harvests WHERE harvest_date >= date('now', '-7 days')")
        recent_harvests = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM watering_schedule WHERE next_watering <= date('now', '+1 days')")
        needs_watering = cursor.fetchone()[0]

        conn.close()

        return {
            'active_plants': active_plants,
            'active_pests': active_pests,
            'recent_harvests': recent_harvests,
            'needs_watering': needs_watering
        }


if __name__ == '__main__':
    # Test database
    db = GardenDB()
    print("Database initialized successfully!")
    print("\nSummary:", db.get_summary())
