"""
Monitoring Agent Database Module
SQLite-based data storage for system monitoring data
"""
import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional

class MonitoringDB:
    """Database manager for monitoring agent"""

    def __init__(self, db_path: str = "monitoring.db"):
        self.db_path = db_path
        self.init_db()

    def get_connection(self) -> sqlite3.Connection:
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        """Initialize database tables"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_name TEXT NOT NULL,
                value REAL NOT NULL,
                unit TEXT,
                source TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                alert_type TEXT NOT NULL,
                severity TEXT NOT NULL CHECK(severity IN ('info','warning','error','critical')),
                message TEXT NOT NULL,
                source TEXT,
                resolved BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                resolved_at TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS performance_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                service_name TEXT NOT NULL,
                response_time REAL,
                status_code INTEGER,
                success BOOLEAN,
                error_message TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS thresholds (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_name TEXT NOT NULL,
                warning_threshold REAL,
                critical_threshold REAL,
                enabled BOOLEAN DEFAULT 1
            )
        ''')

        conn.commit()
        conn.close()

    def record_metric(self, metric_name: str, value: float, unit: str = None, source: str = "system") -> int:
        """Record a system metric"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO metrics (metric_name, value, unit, source)
            VALUES (?, ?, ?, ?)
        ''', (metric_name, value, unit, source))

        metric_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return metric_id

    def get_metrics(self, metric_name: str = None, limit: int = 100) -> List[Dict]:
        """Retrieve metrics"""
        conn = self.get_connection()
        cursor = conn.cursor()

        if metric_name:
            cursor.execute('''
                SELECT * FROM metrics
                WHERE metric_name = ?
                ORDER BY timestamp DESC LIMIT ?
            ''', (metric_name, limit))
        else:
            cursor.execute('''
                SELECT * FROM metrics
                ORDER BY timestamp DESC LIMIT ?
            ''', (limit,))

        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def create_alert(self, alert_type: str, severity: str, message: str, source: str = None) -> int:
        """Create a new alert"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO alerts (alert_type, severity, message, source)
            VALUES (?, ?, ?, ?)
        ''', (alert_type, severity, message, source))

        alert_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return alert_id

    def get_alerts(self, resolved: bool = None, severity: str = None) -> List[Dict]:
        """Get alerts"""
        conn = self.get_connection()
        cursor = conn.cursor()

        query = "SELECT * FROM alerts WHERE 1=1"
        params = []

        if resolved is not None:
            query += " AND resolved = ?"
            params.append(1 if resolved else 0)

        if severity:
            query += " AND severity = ?"
            params.append(severity)

        query += " ORDER BY created_at DESC"

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def resolve_alert(self, alert_id: int) -> bool:
        """Mark an alert as resolved"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            UPDATE alerts
            SET resolved = 1, resolved_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (alert_id,))

        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return success

    def log_performance(self, service_name: str, response_time: float = None,
                        status_code: int = None, success: bool = True, error_message: str = None) -> int:
        """Log service performance"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO performance_logs (service_name, response_time, status_code, success, error_message)
            VALUES (?, ?, ?, ?, ?)
        ''', (service_name, response_time, status_code, success, error_message))

        log_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return log_id

    def get_performance_logs(self, service_name: str = None, limit: int = 100) -> List[Dict]:
        """Get performance logs"""
        conn = self.get_connection()
        cursor = conn.cursor()

        if service_name:
            cursor.execute('''
                SELECT * FROM performance_logs
                WHERE service_name = ?
                ORDER BY timestamp DESC LIMIT ?
            ''', (service_name, limit))
        else:
            cursor.execute('''
                SELECT * FROM performance_logs
                ORDER BY timestamp DESC LIMIT ?
            ''', (limit,))

        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def set_threshold(self, metric_name: str, warning: float = None, critical: float = None) -> int:
        """Set monitoring thresholds"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT OR REPLACE INTO thresholds (metric_name, warning_threshold, critical_threshold)
            VALUES (?, ?, ?)
        ''', (metric_name, warning, critical))

        threshold_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return threshold_id

    def check_thresholds(self) -> List[Dict]:
        """Check current metrics against thresholds"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT t.*, m.value as current_value
            FROM thresholds t
            JOIN (
                SELECT metric_name, value, ROW_NUMBER() OVER (PARTITION BY metric_name ORDER BY timestamp DESC) as rn
                FROM metrics
            ) m ON t.metric_name = m.metric_name AND m.rn = 1
            WHERE t.enabled = 1
        ''')

        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
