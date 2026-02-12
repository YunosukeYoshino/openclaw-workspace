"""
Cloud Agent Database Module

Manages cloud services, storage, and usage tracking.
"""

import sqlite3
from datetime import datetime
from typing import List, Dict, Optional
import json

class CloudDB:
    """Database handler for Cloud Agent"""

    def __init__(self, db_path: str = "agents/cloud-agent/cloud.db"):
        self.db_path = db_path
        self.conn = None
        self.init_db()

    def connect(self):
        """Create database connection"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        return self.conn

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()

    def init_db(self):
        """Initialize database tables"""
        conn = self.connect()
        cursor = conn.cursor()

        # Services table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS services (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                provider TEXT NOT NULL,
                service_type TEXT NOT NULL,
                status TEXT DEFAULT 'active' CHECK(status IN ('active','inactive','deprecated','error')),
                region TEXT,
                cost_monthly REAL DEFAULT 0,
                usage_stats TEXT,
                tags TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Storage table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS storage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                provider TEXT NOT NULL,
                type TEXT NOT NULL CHECK(type IN ('s3','blob','file','database','backup')),
                size_used_gb REAL DEFAULT 0,
                size_total_gb REAL DEFAULT 0,
                status TEXT DEFAULT 'active' CHECK(status IN ('active','inactive','archived')),
                region TEXT,
                access_tier TEXT,
                retention_days INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_accessed TIMESTAMP
            )
        """)

        # Usage logs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usage_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                resource_id INTEGER NOT NULL,
                resource_type TEXT NOT NULL CHECK(resource_type IN ('service','storage')),
                metric TEXT NOT NULL,
                value REAL,
                unit TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                notes TEXT,
                FOREIGN KEY (resource_id) REFERENCES services(id) ON DELETE CASCADE
            )
        """)

        conn.commit()
        conn.close()

    # Service operations
    def add_service(self, name: str, provider: str, service_type: str,
                    region: str = None, cost_monthly: float = 0) -> int:
        """Add a new cloud service"""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO services (name, provider, service_type, region, cost_monthly)
            VALUES (?, ?, ?, ?, ?)
        """, (name, provider, service_type, region, cost_monthly))
        service_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return service_id

    def get_services(self, provider: str = None, status: str = None) -> List[Dict]:
        """Get cloud services, optionally filtered"""
        conn = self.connect()
        cursor = conn.cursor()

        query = "SELECT * FROM services"
        params = []

        conditions = []
        if provider:
            conditions.append("provider = ?")
            params.append(provider)
        if status:
            conditions.append("status = ?")
            params.append(status)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " ORDER BY created_at DESC"

        cursor.execute(query, params)
        services = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return services

    def update_service_status(self, service_id: int, status: str) -> bool:
        """Update service status"""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE services SET status = ?, updated_at = ?
            WHERE id = ?
        """, (status, datetime.now().isoformat(), service_id))
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return success

    def update_service_cost(self, service_id: int, cost_monthly: float) -> bool:
        """Update service cost"""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE services SET cost_monthly = ?, updated_at = ?
            WHERE id = ?
        """, (cost_monthly, datetime.now().isoformat(), service_id))
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return success

    # Storage operations
    def add_storage(self, name: str, provider: str, storage_type: str,
                    size_used_gb: float = 0, size_total_gb: float = 0,
                    region: str = None) -> int:
        """Add a new storage resource"""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO storage (name, provider, type, size_used_gb, size_total_gb, region)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (name, provider, storage_type, size_used_gb, size_total_gb, region))
        storage_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return storage_id

    def get_storage(self, provider: str = None, storage_type: str = None) -> List[Dict]:
        """Get storage resources"""
        conn = self.connect()
        cursor = conn.cursor()

        query = "SELECT * FROM storage"
        params = []

        conditions = []
        if provider:
            conditions.append("provider = ?")
            params.append(provider)
        if storage_type:
            conditions.append("type = ?")
            params.append(storage_type)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " ORDER BY created_at DESC"

        cursor.execute(query, params)
        storage = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return storage

    def update_storage_usage(self, storage_id: int, size_used_gb: float) -> bool:
        """Update storage usage"""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE storage SET size_used_gb = ?, last_accessed = ?
            WHERE id = ?
        """, (size_used_gb, datetime.now().isoformat(), storage_id))
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return success

    # Usage log operations
    def log_usage(self, resource_id: int, resource_type: str,
                  metric: str, value: float, unit: str = None,
                  notes: str = None) -> int:
        """Add a usage log entry"""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO usage_logs (resource_id, resource_type, metric, value, unit, notes)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (resource_id, resource_type, metric, value, unit, notes))
        log_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return log_id

    def get_usage_logs(self, resource_id: int = None, limit: int = 50) -> List[Dict]:
        """Get usage logs, optionally filtered by resource"""
        conn = self.connect()
        cursor = conn.cursor()

        if resource_id:
            cursor.execute("""
                SELECT * FROM usage_logs WHERE resource_id = ?
                ORDER BY timestamp DESC LIMIT ?
            """, (resource_id, limit))
        else:
            cursor.execute("""
                SELECT * FROM usage_logs ORDER BY timestamp DESC LIMIT ?
            """, (limit,))

        logs = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return logs

    def get_stats(self) -> Dict:
        """Get cloud statistics"""
        conn = self.connect()
        cursor = conn.cursor()

        stats = {}

        # Service stats
        cursor.execute("SELECT provider, COUNT(*) FROM services GROUP BY provider")
        stats['services_by_provider'] = dict(cursor.fetchall())

        cursor.execute("SELECT status, COUNT(*) FROM services GROUP BY status")
        stats['services_by_status'] = dict(cursor.fetchall())

        cursor.execute("SELECT SUM(cost_monthly) FROM services WHERE status = 'active'")
        stats['total_monthly_cost'] = cursor.fetchone()[0] or 0

        # Storage stats
        cursor.execute("SELECT provider, COUNT(*) FROM storage GROUP BY provider")
        stats['storage_by_provider'] = dict(cursor.fetchall())

        cursor.execute("SELECT SUM(size_used_gb), SUM(size_total_gb) FROM storage WHERE status = 'active'")
        result = cursor.fetchone()
        stats['storage_used_gb'] = result[0] or 0
        stats['storage_total_gb'] = result[1] or 0
        stats['storage_utilization'] = round((stats['storage_used_gb'] / stats['storage_total_gb'] * 100), 2) if stats['storage_total_gb'] > 0 else 0

        conn.close()
        return stats
