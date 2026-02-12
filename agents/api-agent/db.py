"""
API Agent Database Module
SQLite-based data storage for API key management and request logging
"""
import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional

class APIDB:
    """Database manager for API agent"""

    def __init__(self, db_path: str = "api.db"):
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
            CREATE TABLE IF NOT EXISTS api_keys (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                service TEXT NOT NULL,
                key_value TEXT NOT NULL,
                key_type TEXT DEFAULT 'api_key',
                base_url TEXT,
                description TEXT,
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS api_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                api_key_id INTEGER,
                service TEXT NOT NULL,
                method TEXT NOT NULL,
                endpoint TEXT NOT NULL,
                request_headers TEXT,
                request_body TEXT,
                response_status INTEGER,
                response_headers TEXT,
                response_body TEXT,
                duration_ms INTEGER,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                success INTEGER DEFAULT 0,
                FOREIGN KEY (api_key_id) REFERENCES api_keys(id)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS api_templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                service TEXT NOT NULL,
                method TEXT NOT NULL,
                endpoint TEXT NOT NULL,
                headers TEXT,
                body_template TEXT,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS request_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                log_type TEXT NOT NULL,
                message TEXT NOT NULL,
                details TEXT,
                severity TEXT DEFAULT 'info',
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        conn.commit()
        conn.close()

    def add_api_key(self, name: str, service: str, key_value: str,
                    key_type: str = 'api_key', base_url: str = None,
                    description: str = None) -> int:
        """Add a new API key"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO api_keys (name, service, key_value, key_type, base_url, description)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (name, service, key_value, key_type, base_url, description))

        key_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return key_id

    def get_api_keys(self, service: str = None, is_active: bool = None) -> List[Dict]:
        """Get all API keys with optional filters"""
        conn = self.get_connection()
        cursor = conn.cursor()

        query = "SELECT id, name, service, key_type, base_url, description, is_active, created_at FROM api_keys WHERE 1=1"
        params = []

        if service:
            query += " AND service = ?"
            params.append(service)

        if is_active is not None:
            query += " AND is_active = ?"
            params.append(1 if is_active else 0)

        query += " ORDER BY created_at DESC"

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def get_api_key(self, key_id: int) -> Optional[Dict]:
        """Get a specific API key with the actual key value"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM api_keys WHERE id = ?", (key_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    def update_api_key(self, key_id: int, key_value: str = None,
                      base_url: str = None, description: str = None) -> bool:
        """Update an API key"""
        conn = self.get_connection()
        cursor = conn.cursor()

        updates = []
        params = []

        if key_value:
            updates.append("key_value = ?")
            params.append(key_value)

        if base_url:
            updates.append("base_url = ?")
            params.append(base_url)

        if description:
            updates.append("description = ?")
            params.append(description)

        if updates:
            updates.append("updated_at = CURRENT_TIMESTAMP")
            params.append(key_id)
            query = f"UPDATE api_keys SET {', '.join(updates)} WHERE id = ?"
            cursor.execute(query, params)
            conn.commit()
            conn.close()
            return True

        conn.close()
        return False

    def toggle_key_active(self, key_id: int) -> bool:
        """Toggle API key active status"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT is_active FROM api_keys WHERE id = ?", (key_id,))
        result = cursor.fetchone()

        if result:
            new_status = 0 if result['is_active'] == 1 else 1
            cursor.execute("UPDATE api_keys SET is_active = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                         (new_status, key_id))
            conn.commit()
            conn.close()
            return new_status == 1

        conn.close()
        return False

    def delete_api_key(self, key_id: int) -> bool:
        """Delete an API key"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM api_keys WHERE id = ?", (key_id,))
        conn.commit()
        conn.close()
        return True

    def log_request(self, service: str, method: str, endpoint: str,
                    api_key_id: int = None, request_headers: Dict = None,
                    request_body: str = None, response_status: int = None,
                    response_headers: Dict = None, response_body: str = None,
                    duration_ms: int = None, success: bool = False) -> int:
        """Log an API request"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO api_requests (
                api_key_id, service, method, endpoint, request_headers,
                request_body, response_status, response_headers, response_body,
                duration_ms, success
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            api_key_id, service, method, endpoint,
            json.dumps(request_headers) if request_headers else None,
            request_body,
            response_status,
            json.dumps(response_headers) if response_headers else None,
            response_body[:5000] if response_body else None,  # Limit response size
            duration_ms,
            1 if success else 0
        ))

        request_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return request_id

    def get_requests(self, service: str = None, limit: int = 50) -> List[Dict]:
        """Get recent API requests"""
        conn = self.get_connection()
        cursor = conn.cursor()

        if service:
            cursor.execute('''
                SELECT * FROM api_requests WHERE service = ?
                ORDER BY timestamp DESC LIMIT ?
            ''', (service, limit))
        else:
            cursor.execute('''
                SELECT * FROM api_requests ORDER BY timestamp DESC LIMIT ?
            ''', (limit,))

        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def get_request_stats(self, service: str = None) -> Dict:
        """Get API request statistics"""
        conn = self.get_connection()
        cursor = conn.cursor()

        if service:
            cursor.execute('''
                SELECT
                    COUNT(*) as total_requests,
                    SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as success_count,
                    SUM(CASE WHEN success = 0 THEN 1 ELSE 0 END) as failure_count,
                    AVG(duration_ms) as avg_duration,
                    MAX(duration_ms) as max_duration
                FROM api_requests WHERE service = ?
            ''', (service,))
        else:
            cursor.execute('''
                SELECT
                    COUNT(*) as total_requests,
                    SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as success_count,
                    SUM(CASE WHEN success = 0 THEN 1 ELSE 0 END) as failure_count,
                    AVG(duration_ms) as avg_duration,
                    MAX(duration_ms) as max_duration
                FROM api_requests
            ''')

        result = cursor.fetchone()
        conn.close()
        return dict(result) if result else {}

    def add_template(self, name: str, service: str, method: str,
                     endpoint: str, headers: Dict = None,
                     body_template: str = None, description: str = None) -> int:
        """Add an API request template"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO api_templates (name, service, method, endpoint, headers, body_template, description)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (name, service, method, endpoint,
              json.dumps(headers) if headers else None, body_template, description))

        template_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return template_id

    def get_templates(self, service: str = None) -> List[Dict]:
        """Get API request templates"""
        conn = self.get_connection()
        cursor = conn.cursor()

        if service:
            cursor.execute("SELECT * FROM api_templates WHERE service = ?", (service,))
        else:
            cursor.execute("SELECT * FROM api_templates ORDER BY created_at DESC")

        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def add_log(self, log_type: str, message: str, details: str = None, severity: str = 'info') -> int:
        """Add a log entry"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO request_logs (log_type, message, details, severity)
            VALUES (?, ?, ?, ?)
        ''', (log_type, message, details, severity))

        log_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return log_id

    def get_logs(self, log_type: str = None, severity: str = None, limit: int = 50) -> List[Dict]:
        """Get log entries"""
        conn = self.get_connection()
        cursor = conn.cursor()

        query = "SELECT * FROM request_logs WHERE 1=1"
        params = []

        if log_type:
            query += " AND log_type = ?"
            params.append(log_type)

        if severity:
            query += " AND severity = ?"
            params.append(severity)

        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
