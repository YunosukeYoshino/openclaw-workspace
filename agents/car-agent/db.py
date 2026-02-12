#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Car Agent - SQLite Database
車管理エージェント - SQLite データベース
"""

import sqlite3
from datetime import datetime
from typing import List, Dict, Optional
import os

class CarDB:
    """Car Database Handler"""

    def __init__(self, db_path: str = None):
        """Initialize database"""
        if db_path is None:
            db_path = os.path.join(os.path.dirname(__file__), 'car.db')
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

        # Vehicles table (車両)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS vehicles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                make TEXT,
                model TEXT,
                year INTEGER,
                license_plate TEXT,
                vin TEXT,
                color TEXT,
                purchase_date DATE,
                purchase_price REAL,
                odometer INTEGER,
                status TEXT DEFAULT 'active',  -- active, sold, scrapped
                notes TEXT,
                photo_path TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Fuel Records table (給油記録)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS fuel_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                vehicle_id INTEGER,
                fill_date DATE DEFAULT (date('now')),
                odometer INTEGER,
                fuel_liters REAL,
                price_per_liter REAL,
                total_price REAL,
                fuel_type TEXT,
                station TEXT,
                full_tank BOOLEAN DEFAULT 1,
                notes TEXT,
                FOREIGN KEY (vehicle_id) REFERENCES vehicles(id)
            )
        ''')

        # Maintenance table (メンテナンス)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS maintenance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                vehicle_id INTEGER,
                service_date DATE DEFAULT (date('now')),
                odometer INTEGER,
                service_type TEXT,  -- oil_change, tire_rotation, brake_service, etc.
                description TEXT,
                cost REAL,
                shop TEXT,
                parts_replaced TEXT,  -- JSON array of parts
                next_due_odometer INTEGER,
                next_due_date DATE,
                notes TEXT,
                FOREIGN KEY (vehicle_id) REFERENCES vehicles(id)
            )
        ''')

        # Repairs table (修理)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS repairs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                vehicle_id INTEGER,
                issue_date DATE DEFAULT (date('now')),
                odometer INTEGER,
                issue TEXT NOT NULL,
                severity TEXT,  -- minor, moderate, critical
                status TEXT DEFAULT 'open',  -- open, in_progress, completed, cancelled
                description TEXT,
                repair_date DATE,
                cost REAL,
                shop TEXT,
                warranty BOOLEAN DEFAULT 0,
                warranty_expiry DATE,
                notes TEXT,
                FOREIGN KEY (vehicle_id) REFERENCES vehicles(id)
            )
        ''')

        # Insurance table (保険)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS insurance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                vehicle_id INTEGER,
                provider TEXT NOT NULL,
                policy_number TEXT NOT NULL,
                policy_type TEXT,  -- comprehensive, third_party, etc.
                start_date DATE NOT NULL,
                end_date DATE NOT NULL,
                premium REAL,
                coverage TEXT,  -- JSON or text description
                status TEXT DEFAULT 'active',  -- active, expired, cancelled
                renewal_date DATE,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (vehicle_id) REFERENCES vehicles(id)
            )
        ''')

        # Reminders table (リマインダー)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reminders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                vehicle_id INTEGER,
                reminder_type TEXT NOT NULL,  -- oil_change, registration, inspection, etc.
                due_date DATE,
                due_odometer INTEGER,
                description TEXT,
                status TEXT DEFAULT 'pending',  -- pending, completed, dismissed
                completed_date DATE,
                notes TEXT,
                FOREIGN KEY (vehicle_id) REFERENCES vehicles(id)
            )
        ''')

        conn.commit()
        conn.close()

    # Vehicles Operations
    def add_vehicle(self, name: str, make: str = None, model: str = None,
                   year: int = None, license_plate: str = None,
                   vin: str = None, color: str = None, odometer: int = 0) -> int:
        """Add a new vehicle"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO vehicles (name, make, model, year, license_plate, vin, color, odometer)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (name, make, model, year, license_plate, vin, color, odometer))
        vehicle_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return vehicle_id

    def get_vehicles(self, status: str = None) -> List[Dict]:
        """Get all vehicles or filter by status"""
        conn = self.get_connection()
        cursor = conn.cursor()

        query = 'SELECT * FROM vehicles WHERE 1=1'
        params = []

        if status:
            query += ' AND status = ?'
            params.append(status)

        query += ' ORDER BY name'

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    def get_vehicle(self, vehicle_id: int) -> Optional[Dict]:
        """Get a specific vehicle by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM vehicles WHERE id = ?', (vehicle_id,))
        row = cursor.fetchone()
        conn.close()

        return dict(row) if row else None

    def update_vehicle(self, vehicle_id: int, **kwargs) -> bool:
        """Update vehicle details"""
        conn = self.get_connection()
        cursor = conn.cursor()

        allowed_fields = ['name', 'make', 'model', 'year', 'license_plate',
                         'vin', 'color', 'purchase_date', 'purchase_price',
                         'odometer', 'status', 'notes', 'photo_path']
        updates = []
        params = []

        for field, value in kwargs.items():
            if field in allowed_fields and value is not None:
                updates.append(f'{field} = ?')
                params.append(value)

        if updates:
            params.append(vehicle_id)
            cursor.execute(f'''
                UPDATE vehicles
                SET {', '.join(updates)}, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', params)

        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return success

    # Fuel Records Operations
    def add_fuel_record(self, vehicle_id: int, odometer: int, fuel_liters: float,
                       price_per_liter: float, total_price: float = None,
                       fuel_type: str = None, station: str = None) -> int:
        """Add a fuel record"""
        conn = self.get_connection()
        cursor = conn.cursor()

        if total_price is None:
            total_price = fuel_liters * price_per_liter

        cursor.execute('''
            INSERT INTO fuel_records
            (vehicle_id, odometer, fuel_liters, price_per_liter, total_price, fuel_type, station)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (vehicle_id, odometer, fuel_liters, price_per_liter, total_price, fuel_type, station))
        fuel_id = cursor.lastrowid

        # Update vehicle odometer if it's higher
        cursor.execute('''
            UPDATE vehicles
            SET odometer = MAX(odometer, ?), updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (odometer, vehicle_id))

        conn.commit()
        conn.close()
        return fuel_id

    def get_fuel_records(self, vehicle_id: int = None, limit: int = 20) -> List[Dict]:
        """Get fuel records"""
        conn = self.get_connection()
        cursor = conn.cursor()

        if vehicle_id:
            cursor.execute('''
                SELECT * FROM fuel_records
                WHERE vehicle_id = ?
                ORDER BY fill_date DESC
                LIMIT ?
            ''', (vehicle_id, limit))
        else:
            cursor.execute('''
                SELECT * FROM fuel_records
                ORDER BY fill_date DESC
                LIMIT ?
            ''', (limit,))

        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    def get_fuel_stats(self, vehicle_id: int, days: int = 30) -> Dict:
        """Get fuel statistics for a vehicle"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT
                COUNT(*) as fill_count,
                SUM(fuel_liters) as total_liters,
                SUM(total_price) as total_cost,
                AVG(price_per_liter) as avg_price_per_liter
            FROM fuel_records
            WHERE vehicle_id = ?
            AND fill_date >= date('now', '-' || ? || ' days')
        ''', (vehicle_id, days))

        stats = cursor.fetchone()
        conn.close()

        if stats and stats['fill_count'] > 0:
            return {
                'fill_count': stats['fill_count'],
                'total_liters': stats['total_liters'] or 0,
                'total_cost': stats['total_cost'] or 0,
                'avg_price_per_liter': stats['avg_price_per_liter'] or 0
            }
        return {
            'fill_count': 0,
            'total_liters': 0,
            'total_cost': 0,
            'avg_price_per_liter': 0
        }

    # Maintenance Operations
    def add_maintenance(self, vehicle_id: int, service_type: str, odometer: int,
                       description: str = None, cost: float = None,
                       shop: str = None, next_due_odometer: int = None,
                       next_due_date: str = None) -> int:
        """Add a maintenance record"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO maintenance
            (vehicle_id, service_date, odometer, service_type, description, cost, shop,
             next_due_odometer, next_due_date)
            VALUES (?, date('now'), ?, ?, ?, ?, ?, ?, ?)
        ''', (vehicle_id, odometer, service_type, description, cost, shop,
              next_due_odometer, next_due_date))
        maint_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return maint_id

    def get_maintenance(self, vehicle_id: int = None, service_type: str = None) -> List[Dict]:
        """Get maintenance records"""
        conn = self.get_connection()
        cursor = conn.cursor()

        query = 'SELECT * FROM maintenance WHERE 1=1'
        params = []

        if vehicle_id:
            query += ' AND vehicle_id = ?'
            params.append(vehicle_id)
        if service_type:
            query += ' AND service_type = ?'
            params.append(service_type)

        query += ' ORDER BY service_date DESC'

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    # Repairs Operations
    def add_repair(self, vehicle_id: int, issue: str, odometer: int,
                  severity: str = 'moderate', description: str = None) -> int:
        """Add a repair record"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO repairs
            (vehicle_id, issue_date, odometer, issue, severity, description)
            VALUES (?, date('now'), ?, ?, ?, ?)
        ''', (vehicle_id, odometer, issue, severity, description))
        repair_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return repair_id

    def get_repairs(self, vehicle_id: int = None, status: str = None) -> List[Dict]:
        """Get repair records"""
        conn = self.get_connection()
        cursor = conn.cursor()

        query = 'SELECT * FROM repairs WHERE 1=1'
        params = []

        if vehicle_id:
            query += ' AND vehicle_id = ?'
            params.append(vehicle_id)
        if status:
            query += ' AND status = ?'
            params.append(status)

        query += ' ORDER BY issue_date DESC'

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    def update_repair(self, repair_id: int, **kwargs) -> bool:
        """Update repair details"""
        conn = self.get_connection()
        cursor = conn.cursor()

        allowed_fields = ['status', 'repair_date', 'cost', 'shop', 'warranty',
                         'warranty_expiry', 'severity', 'description']
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
                SET {', '.join(updates)}
                WHERE id = ?
            ''', params)

        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return success

    # Insurance Operations
    def add_insurance(self, vehicle_id: int, provider: str, policy_number: str,
                     start_date: str, end_date: str, policy_type: str = None,
                     premium: float = None) -> int:
        """Add an insurance policy"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO insurance
            (vehicle_id, provider, policy_number, policy_type, start_date, end_date, premium)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (vehicle_id, provider, policy_number, policy_type, start_date, end_date, premium))
        ins_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return ins_id

    def get_insurance(self, vehicle_id: int = None, status: str = None) -> List[Dict]:
        """Get insurance policies"""
        conn = self.get_connection()
        cursor = conn.cursor()

        query = 'SELECT * FROM insurance WHERE 1=1'
        params = []

        if vehicle_id:
            query += ' AND vehicle_id = ?'
            params.append(vehicle_id)
        if status:
            query += ' AND status = ?'
            params.append(status)

        query += ' ORDER BY end_date DESC'

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    # Reminders Operations
    def add_reminder(self, vehicle_id: int, reminder_type: str, description: str,
                    due_date: str = None, due_odometer: int = None) -> int:
        """Add a reminder"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO reminders (vehicle_id, reminder_type, description, due_date, due_odometer)
            VALUES (?, ?, ?, ?, ?)
        ''', (vehicle_id, reminder_type, description, due_date, due_odometer))
        reminder_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return reminder_id

    def get_reminders(self, vehicle_id: int = None, status: str = None) -> List[Dict]:
        """Get reminders"""
        conn = self.get_connection()
        cursor = conn.cursor()

        query = 'SELECT * FROM reminders WHERE 1=1'
        params = []

        if vehicle_id:
            query += ' AND vehicle_id = ?'
            params.append(vehicle_id)
        if status:
            query += ' AND status = ?'
            params.append(status)

        query += ' ORDER BY due_date ASC'

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    def get_summary(self) -> Dict:
        """Get car management summary"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM vehicles WHERE status = 'active'")
        active_vehicles = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM repairs WHERE status IN ('open', 'in_progress')")
        open_repairs = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM reminders WHERE status = 'pending' AND due_date <= date('now', '+14 days')")
        upcoming_reminders = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM insurance WHERE status = 'active' AND end_date <= date('now', '+30 days')")
        expiring_insurance = cursor.fetchone()[0]

        conn.close()

        return {
            'active_vehicles': active_vehicles,
            'open_repairs': open_repairs,
            'upcoming_reminders': upcoming_reminders,
            'expiring_insurance': expiring_insurance
        }


if __name__ == '__main__':
    # Test database
    db = CarDB()
    print("Database initialized successfully!")
    print("\nSummary:", db.get_summary())
