#!/usr/bin/env python3
"""
Calendar Integration Database
カレンダー連携エージェントのデータベース管理
"""

import sqlite3
from pathlib import Path
from datetime import datetime

class CalendarIntegrationDB:
    """カレンダー連携データベース"""

    def __init__(self, db_path=None):
        if db_path is None:
            db_path = Path(__file__).parent / "calendar_integration.db"
        self.db_path = Path(db_path)
        self.init_db()

    def init_db(self):
        """データベース初期化"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS calendar_sources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            source_type TEXT NOT NULL,
            config TEXT,
            enabled BOOLEAN DEFAULT 1,
            last_sync TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS sync_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_id INTEGER,
            status TEXT,
            events_synced INTEGER,
            error_message TEXT,
            sync_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (source_id) REFERENCES calendar_sources(id)
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS synced_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_id INTEGER,
            external_event_id TEXT,
            title TEXT,
            start_time TEXT,
            end_time TEXT,
            location TEXT,
            description TEXT,
            synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (source_id) REFERENCES calendar_sources(id)
        )
        """)

        conn.commit()
        conn.close()

    def add_source(self, name, source_type, config, enabled=True):
        """カレンダーソースを追加"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO calendar_sources (name, source_type, config, enabled)
        VALUES (?, ?, ?, ?)
        """, (name, source_type, config, enabled))

        source_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return source_id

    def get_source(self, source_id):
        """ソースを取得"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM calendar_sources WHERE id = ?", (source_id,))
        row = cursor.fetchone()
        conn.close()

        if row:
            return {
                'id': row[0],
                'name': row[1],
                'source_type': row[2],
                'config': row[3],
                'enabled': bool(row[4]),
                'last_sync': row[5],
                'created_at': row[6]
            }
        return None

    def get_all_sources(self):
        """全ソースを取得"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM calendar_sources ORDER BY created_at DESC")
        rows = cursor.fetchall()
        conn.close()

        return [{
            'id': r[0],
            'name': r[1],
            'source_type': r[2],
            'config': r[3],
            'enabled': bool(r[4]),
            'last_sync': r[5],
            'created_at': r[6]
        } for r in rows]

    def update_source(self, source_id, **kwargs):
        """ソースを更新"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        fields = []
        values = []
        for key, value in kwargs.items():
            fields.append(f"{key} = ?")
            values.append(value)

        values.append(source_id)
        cursor.execute(f"UPDATE calendar_sources SET {', '.join(fields)} WHERE id = ?", values)

        conn.commit()
        conn.close()

    def add_sync_log(self, source_id, status, events_synced=None, error_message=None):
        """同期ログを追加"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO sync_logs (source_id, status, events_synced, error_message)
        VALUES (?, ?, ?, ?)
        """, (source_id, status, events_synced, error_message))

        log_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return log_id

    def get_sync_logs(self, source_id=None, limit=None):
        """同期ログを取得"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query = "SELECT * FROM sync_logs"
        params = []
        if source_id:
            query += " WHERE source_id = ?"
            params.append(source_id)

        query += " ORDER BY sync_timestamp DESC"

        if limit:
            query += " LIMIT ?"
            params.append(limit)

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        return [{
            'id': r[0],
            'source_id': r[1],
            'status': r[2],
            'events_synced': r[3],
            'error_message': r[4],
            'sync_timestamp': r[5]
        } for r in rows]

    def add_synced_event(self, source_id, external_event_id, title, start_time, end_time=None, location=None, description=None):
        """同期イベントを追加"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO synced_events (source_id, external_event_id, title, start_time, end_time, location, description)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (source_id, external_event_id, title, start_time, end_time, location, description))

        event_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return event_id

    def get_synced_events(self, source_id=None):
        """同期イベントを取得"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query = "SELECT * FROM synced_events"
        params = []
        if source_id:
            query += " WHERE source_id = ?"
            params.append(source_id)

        query += " ORDER BY start_time DESC"

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        return [{
            'id': r[0],
            'source_id': r[1],
            'external_event_id': r[2],
            'title': r[3],
            'start_time': r[4],
            'end_time': r[5],
            'location': r[6],
            'description': r[7],
            'synced_at': r[8]
        } for r in rows]

if __name__ == '__main__':
    db = CalendarIntegrationDB()
    print("Calendar Integration Database initialized.")
