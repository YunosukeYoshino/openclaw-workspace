"""
Analytics Agent Database Module
SQLite-based data storage for analytics data
"""
import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional

class AnalyticsDB:
    """Database manager for analytics agent"""

    def __init__(self, db_path: str = "analytics.db"):
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
            CREATE TABLE IF NOT EXISTS analytics_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source TEXT NOT NULL,
                data_type TEXT NOT NULL,
                data_json TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                tags TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                content TEXT NOT NULL,
                format TEXT DEFAULT 'json',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'draft'
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS visualizations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                chart_type TEXT NOT NULL,
                data_json TEXT NOT NULL,
                config_json TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        conn.commit()
        conn.close()

    def store_data(self, source: str, data_type: str, data: Dict, tags: List[str] = None) -> int:
        """Store analytics data"""
        conn = self.get_connection()
        cursor = conn.cursor()

        tags_json = json.dumps(tags) if tags else None
        cursor.execute('''
            INSERT INTO analytics_data (source, data_type, data_json, tags)
            VALUES (?, ?, ?, ?)
        ''', (source, data_type, json.dumps(data), tags_json))

        data_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return data_id

    def get_data(self, source: str = None, data_type: str = None, limit: int = 100) -> List[Dict]:
        """Retrieve analytics data"""
        conn = self.get_connection()
        cursor = conn.cursor()

        query = "SELECT * FROM analytics_data WHERE 1=1"
        params = []

        if source:
            query += " AND source = ?"
            params.append(source)

        if data_type:
            query += " AND data_type = ?"
            params.append(data_type)

        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    def create_report(self, title: str, content: str, description: str = None, format: str = 'json') -> int:
        """Create a new report"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO reports (title, description, content, format)
            VALUES (?, ?, ?, ?)
        ''', (title, description, content, format))

        report_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return report_id

    def get_reports(self, status: str = None) -> List[Dict]:
        """Get all reports"""
        conn = self.get_connection()
        cursor = conn.cursor()

        if status:
            cursor.execute("SELECT * FROM reports WHERE status = ? ORDER BY created_at DESC", (status,))
        else:
            cursor.execute("SELECT * FROM reports ORDER BY created_at DESC")

        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def save_visualization(self, title: str, chart_type: str, data: Dict, config: Dict = None) -> int:
        """Save visualization configuration"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO visualizations (title, chart_type, data_json, config_json)
            VALUES (?, ?, ?, ?)
        ''', (title, chart_type, json.dumps(data), json.dumps(config) if config else None))

        viz_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return viz_id

    def get_visualizations(self) -> List[Dict]:
        """Get all visualizations"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM visualizations ORDER BY created_at DESC")
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
