#!/usr/bin/env python3
"""
Device Agent - Database Module
SQLite database for device management
"""

import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional, Any
from pathlib import Path

class DeviceDatabase:
    """Database manager for device tracking"""

    def __init__(self, db_path: str = "devices.db"):
        """Initialize database connection and create tables"""
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._create_tables()

    def _create_tables(self):
        """Create all necessary tables"""
        cursor = self.conn.cursor()

        # Devices table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS devices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                type TEXT NOT NULL,
                model TEXT,
                serial_number TEXT,
                status TEXT DEFAULT 'active',
                location TEXT,
                ip_address TEXT,
                mac_address TEXT,
                owner TEXT,
                purchase_date DATE,
                warranty_expiry DATE,
                specifications TEXT,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Device maintenance table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS device_maintenance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_id INTEGER NOT NULL,
                maintenance_type TEXT NOT NULL,
                description TEXT,
                cost REAL,
                performed_date DATE,
                performed_by TEXT,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (device_id) REFERENCES devices (id)
            )
        """)

        # Device issues table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS device_issues (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_id INTEGER NOT NULL,
                issue_type TEXT NOT NULL,
                description TEXT,
                severity TEXT,
                status TEXT DEFAULT 'open',
                reported_date DATE,
                resolved_date DATE,
                resolution_notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (device_id) REFERENCES devices (id)
            )
        """)

        # Device assignments table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS device_assignments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_id INTEGER NOT NULL,
                assigned_to TEXT NOT NULL,
                assigned_date DATE,
                returned_date DATE,
                purpose TEXT,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (device_id) REFERENCES devices (id)
            )
        """)

        self.conn.commit()

    # Device CRUD operations
    def add_device(self, name: str, type: str, **kwargs) -> int:
        """Add a new device"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO devices (name, type, model, serial_number, status, location,
                               ip_address, mac_address, owner, purchase_date,
                               warranty_expiry, specifications, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (name, type, kwargs.get('model'), kwargs.get('serial_number'),
              kwargs.get('status', 'active'), kwargs.get('location'),
              kwargs.get('ip_address'), kwargs.get('mac_address'),
              kwargs.get('owner'), kwargs.get('purchase_date'),
              kwargs.get('warranty_expiry'), kwargs.get('specifications'),
              kwargs.get('notes')))
        self.conn.commit()
        return cursor.lastrowid

    def get_device(self, device_id: int) -> Optional[Dict]:
        """Get device by ID"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM devices WHERE id = ?", (device_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def list_devices(self, status: str = None, type: str = None) -> List[Dict]:
        """List all devices with optional filters"""
        cursor = self.conn.cursor()
        query = "SELECT * FROM devices WHERE 1=1"
        params = []

        if status:
            query += " AND status = ?"
            params.append(status)
        if type:
            query += " AND type = ?"
            params.append(type)

        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

    def update_device(self, device_id: int, **kwargs) -> bool:
        """Update device information"""
        cursor = self.conn.cursor()
        updates = []
        params = []

        for key, value in kwargs.items():
            if key in ['name', 'type', 'model', 'serial_number', 'status',
                      'location', 'ip_address', 'mac_address', 'owner',
                      'purchase_date', 'warranty_expiry', 'specifications', 'notes']:
                updates.append(f"{key} = ?")
                params.append(value)

        if updates:
            params.append(device_id)
            cursor.execute(f"""
                UPDATE devices SET {', '.join(updates)}, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, params)
            self.conn.commit()
            return cursor.rowcount > 0
        return False

    def delete_device(self, device_id: int) -> bool:
        """Delete a device"""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM devices WHERE id = ?", (device_id,))
        self.conn.commit()
        return cursor.rowcount > 0

    # Maintenance operations
    def add_maintenance(self, device_id: int, maintenance_type: str, **kwargs) -> int:
        """Add maintenance record"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO device_maintenance (device_id, maintenance_type, description,
                                           cost, performed_date, performed_by, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (device_id, maintenance_type, kwargs.get('description'),
              kwargs.get('cost'), kwargs.get('performed_date'),
              kwargs.get('performed_by'), kwargs.get('notes')))
        self.conn.commit()
        return cursor.lastrowid

    def get_maintenance_history(self, device_id: int) -> List[Dict]:
        """Get maintenance history for a device"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM device_maintenance WHERE device_id = ?
            ORDER BY performed_date DESC
        """, (device_id,))
        return [dict(row) for row in cursor.fetchall()]

    # Issue operations
    def add_issue(self, device_id: int, issue_type: str, **kwargs) -> int:
        """Add device issue"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO device_issues (device_id, issue_type, description, severity,
                                      status, reported_date, resolved_date, resolution_notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (device_id, issue_type, kwargs.get('description'), kwargs.get('severity'),
              kwargs.get('status', 'open'), kwargs.get('reported_date'),
              kwargs.get('resolved_date'), kwargs.get('resolution_notes')))
        self.conn.commit()
        return cursor.lastrowid

    def resolve_issue(self, issue_id: int, resolution_notes: str, resolved_date: str = None) -> bool:
        """Mark issue as resolved"""
        cursor = self.conn.cursor()
        if not resolved_date:
            resolved_date = datetime.now().strftime('%Y-%m-%d')
        cursor.execute("""
            UPDATE device_issues SET status = 'resolved', resolved_date = ?, resolution_notes = ?
            WHERE id = ?
        """, (resolved_date, resolution_notes, issue_id))
        self.conn.commit()
        return cursor.rowcount > 0

    def get_device_issues(self, device_id: int, status: str = None) -> List[Dict]:
        """Get issues for a device"""
        cursor = self.conn.cursor()
        query = "SELECT * FROM device_issues WHERE device_id = ?"
        params = [device_id]

        if status:
            query += " AND status = ?"
            params.append(status)

        query += " ORDER BY reported_date DESC"

        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

    # Assignment operations
    def assign_device(self, device_id: int, assigned_to: str, **kwargs) -> int:
        """Assign device to someone"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO device_assignments (device_id, assigned_to, assigned_date, purpose, notes)
            VALUES (?, ?, ?, ?, ?)
        """, (device_id, assigned_to, kwargs.get('assigned_date'),
              kwargs.get('purpose'), kwargs.get('notes')))
        self.conn.commit()
        return cursor.lastrowid

    def return_device(self, assignment_id: int, returned_date: str = None) -> bool:
        """Mark device as returned"""
        cursor = self.conn.cursor()
        if not returned_date:
            returned_date = datetime.now().strftime('%Y-%m-%d')
        cursor.execute("""
            UPDATE device_assignments SET returned_date = ? WHERE id = ?
        """, (returned_date, assignment_id))
        self.conn.commit()
        return cursor.rowcount > 0

    def get_device_assignments(self, device_id: int = None) -> List[Dict]:
        """Get device assignments"""
        cursor = self.conn.cursor()
        if device_id:
            cursor.execute("""
                SELECT * FROM device_assignments WHERE device_id = ? ORDER BY assigned_date DESC
            """, (device_id,))
        else:
            cursor.execute("SELECT * FROM device_assignments ORDER BY assigned_date DESC")
        return [dict(row) for row in cursor.fetchall()]

    # Search and query operations
    def search_devices(self, search_term: str) -> List[Dict]:
        """Search devices by name, type, or serial number"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM devices
            WHERE name LIKE ? OR type LIKE ? OR serial_number LIKE ? OR model LIKE ?
            ORDER BY name
        """, (f'%{search_term}%', f'%{search_term}%', f'%{search_term}%', f'%{search_term}%'))
        return [dict(row) for row in cursor.fetchall()]

    def get_expiring_warranties(self, days: int = 30) -> List[Dict]:
        """Get devices with warranties expiring soon"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM devices
            WHERE warranty_expiry BETWEEN DATE('now') AND DATE('now', '+' || ? || ' days')
            AND status = 'active'
            ORDER BY warranty_expiry
        """, (days,))
        return [dict(row) for row in cursor.fetchall()]

    def get_active_issues(self) -> List[Dict]:
        """Get all open issues"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT di.*, d.name as device_name
            FROM device_issues di
            JOIN devices d ON di.device_id = d.id
            WHERE di.status = 'open'
            ORDER BY di.reported_date DESC
        """)
        return [dict(row) for row in cursor.fetchall()]

    def get_statistics(self) -> Dict[str, Any]:
        """Get device statistics"""
        cursor = self.conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM devices")
        total = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM devices WHERE status = 'active'")
        active = cursor.fetchone()[0]

        cursor.execute("SELECT type, COUNT(*) FROM devices GROUP BY type")
        by_type = {row[0]: row[1] for row in cursor.fetchall()}

        cursor.execute("SELECT COUNT(*) FROM device_issues WHERE status = 'open'")
        open_issues = cursor.fetchone()[0]

        return {
            'total_devices': total,
            'active_devices': active,
            'by_type': by_type,
            'open_issues': open_issues
        }

    def close(self):
        """Close database connection"""
        self.conn.close()

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
