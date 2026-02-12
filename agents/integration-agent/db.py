"""
Integration Agent Database Module
SQLite-based data storage for service integrations
"""
import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional

class IntegrationDB:
    """Database manager for integration agent"""

    def __init__(self, db_path: str = "integration.db"):
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
            CREATE TABLE IF NOT EXISTS services (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                service_type TEXT NOT NULL,
                base_url TEXT,
                api_key TEXT,
                config_json TEXT,
                enabled BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS api_connections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                service_id INTEGER NOT NULL,
                endpoint TEXT NOT NULL,
                method TEXT NOT NULL,
                response_status INTEGER,
                response_time REAL,
                error_message TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (service_id) REFERENCES services(id)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS data_syncs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_service TEXT NOT NULL,
                target_service TEXT NOT NULL,
                sync_type TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                records_processed INTEGER DEFAULT 0,
                records_failed INTEGER DEFAULT 0,
                started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                error_message TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS webhooks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                url TEXT NOT NULL,
                events TEXT,
                secret TEXT,
                active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        conn.commit()
        conn.close()

    def add_service(self, name: str, service_type: str, base_url: str = None,
                    api_key: str = None, config: Dict = None) -> int:
        """Add a new service"""
        conn = self.get_connection()
        cursor = conn.cursor()

        config_json = json.dumps(config) if config else None

        try:
            cursor.execute('''
                INSERT INTO services (name, service_type, base_url, api_key, config_json)
                VALUES (?, ?, ?, ?, ?)
            ''', (name, service_type, base_url, api_key, config_json))

            service_id = cursor.lastrowid
            conn.commit()
            conn.close()
            return service_id
        except sqlite3.IntegrityError:
            conn.close()
            raise ValueError(f"Service '{name}' already exists")

    def get_services(self, enabled_only: bool = False) -> List[Dict]:
        """Get all services"""
        conn = self.get_connection()
        cursor = conn.cursor()

        if enabled_only:
            cursor.execute("SELECT * FROM services WHERE enabled = 1")
        else:
            cursor.execute("SELECT * FROM services")

        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def get_service(self, name: str) -> Optional[Dict]:
        """Get a specific service by name"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM services WHERE name = ?", (name,))
        row = cursor.fetchone()
        conn.close()

        return dict(row) if row else None

    def log_api_call(self, service_id: int, endpoint: str, method: str,
                     status: int = None, response_time: float = None, error: str = None) -> int:
        """Log an API call"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO api_connections (service_id, endpoint, method, response_status, response_time, error_message)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (service_id, endpoint, method, status, response_time, error))

        call_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return call_id

    def get_api_logs(self, service_id: int = None, limit: int = 50) -> List[Dict]:
        """Get API call logs"""
        conn = self.get_connection()
        cursor = conn.cursor()

        if service_id:
            cursor.execute('''
                SELECT * FROM api_connections
                WHERE service_id = ?
                ORDER BY timestamp DESC LIMIT ?
            ''', (service_id, limit))
        else:
            cursor.execute('''
                SELECT * FROM api_connections
                ORDER BY timestamp DESC LIMIT ?
            ''', (limit,))

        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def create_sync(self, source: str, target: str, sync_type: str) -> int:
        """Create a new data sync task"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO data_syncs (source_service, target_service, sync_type)
            VALUES (?, ?, ?)
        ''', (source, target, sync_type))

        sync_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return sync_id

    def update_sync(self, sync_id: int, status: str, processed: int = 0,
                    failed: int = 0, error: str = None):
        """Update sync status"""
        conn = self.get_connection()
        cursor = conn.cursor()

        updates = ["status = ?", "records_processed = ?", "records_failed = ?"]
        params = [status, processed, failed]

        if error:
            updates.append("error_message = ?")
            params.append(error)

        if status == 'completed':
            updates.append("completed_at = CURRENT_TIMESTAMP")

        params.append(sync_id)

        cursor.execute(f'''
            UPDATE data_syncs
            SET {', '.join(updates)}
            WHERE id = ?
        ''', params)

        conn.commit()
        conn.close()

    def get_syncs(self, status: str = None) -> List[Dict]:
        """Get sync tasks"""
        conn = self.get_connection()
        cursor = conn.cursor()

        if status:
            cursor.execute("SELECT * FROM data_syncs WHERE status = ? ORDER BY started_at DESC", (status,))
        else:
            cursor.execute("SELECT * FROM data_syncs ORDER BY started_at DESC")

        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def add_webhook(self, name: str, url: str, events: List[str] = None, secret: str = None) -> int:
        """Add a webhook"""
        conn = self.get_connection()
        cursor = conn.cursor()

        events_json = json.dumps(events) if events else None

        cursor.execute('''
            INSERT INTO webhooks (name, url, events, secret)
            VALUES (?, ?, ?, ?)
        ''', (name, url, events_json, secret))

        webhook_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return webhook_id

    def get_webhooks(self, active_only: bool = False) -> List[Dict]:
        """Get all webhooks"""
        conn = self.get_connection()
        cursor = conn.cursor()

        if active_only:
            cursor.execute("SELECT * FROM webhooks WHERE active = 1")
        else:
            cursor.execute("SELECT * FROM webhooks")

        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def toggle_webhook(self, webhook_id: int, active: bool) -> bool:
        """Enable/disable webhook"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("UPDATE webhooks SET active = ? WHERE id = ?", (active, webhook_id))
        success = cursor.rowcount > 0

        conn.commit()
        conn.close()
        return success
