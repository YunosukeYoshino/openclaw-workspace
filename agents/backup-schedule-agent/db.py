#!/usr/bin/env python3
"""
Backup Schedule Database
バックアップスケジュールエージェントのデータベース管理
"""

import sqlite3
from pathlib import Path
from datetime import datetime

class BackupScheduleDB:
    """バックアップスケジュールデータベース"""

    def __init__(self, db_path=None):
        if db_path is None:
            db_path = Path(__file__).parent / "backup_schedule.db"
        self.db_path = Path(db_path)
        self.init_db()

    def init_db(self):
        """データベース初期化"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS backup_schedules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            target_type TEXT NOT NULL,
            path TEXT,
            schedule_type TEXT NOT NULL,
            schedule_value TEXT,
            backup_type TEXT DEFAULT 'full',
            compress BOOLEAN DEFAULT 1,
            retention_days INTEGER DEFAULT 30,
            enabled BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS backup_jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            schedule_id INTEGER,
            status TEXT DEFAULT 'pending',
            started_at TIMESTAMP,
            completed_at TIMESTAMP,
            backup_size INTEGER,
            backup_path TEXT,
            error_message TEXT,
            success BOOLEAN,
            FOREIGN KEY (schedule_id) REFERENCES backup_schedules(id)
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS backup_targets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            target_type TEXT NOT NULL,
            name TEXT NOT NULL,
            path TEXT,
            description TEXT,
            priority INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS backup_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            schedule_id INTEGER,
            log_level TEXT DEFAULT 'info',
            message TEXT,
            details TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (schedule_id) REFERENCES backup_schedules(id)
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS retention_policies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            policy_name TEXT NOT NULL,
            backup_type TEXT NOT NULL,
            daily_retention INTEGER,
            weekly_retention INTEGER,
            monthly_retention INTEGER,
            yearly_retention INTEGER,
            notes TEXT
        )
        """)

        conn.commit()
        conn.close()

    def add_schedule(self, name, target_type, path, schedule_type, schedule_value,
                    backup_type='full', compress=True, retention_days=30, enabled=True):
        """スケジュールを追加"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO backup_schedules (name, target_type, path, schedule_type, schedule_value, backup_type, compress, retention_days, enabled)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (name, target_type, path, schedule_type, schedule_value, backup_type, compress, retention_days, enabled))

        schedule_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return schedule_id

    def get_schedule(self, schedule_id):
        """スケジュールを取得"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM backup_schedules WHERE id = ?", (schedule_id,))
        row = cursor.fetchone()
        conn.close()

        if row:
            return self._row_to_dict(cursor, row, backup_schedules)
        return None

    def get_all_schedules(self, enabled_only=False):
        """全スケジュールを取得"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query = "SELECT * FROM backup_schedules"
        if enabled_only:
            query += " WHERE enabled = 1"

        cursor.execute(query)
        rows = cursor.fetchall()
        conn.close()

        return [self._row_to_dict(cursor, r) for r in rows]

    def update_schedule(self, schedule_id, **kwargs):
        """スケジュールを更新"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        fields = []
        values = []
        for key, value in kwargs.items():
            fields.append(f"{key} = ?")
            values.append(value)

        values.append(schedule_id)
        cursor.execute(f"UPDATE backup_schedules SET {', '.join(fields)}, updated_at = CURRENT_TIMESTAMP WHERE id = ?", values)

        conn.commit()
        conn.close()

    def add_job(self, schedule_id):
        """ジョブを追加"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO backup_jobs (schedule_id, status, started_at)
        VALUES (?, 'running', CURRENT_TIMESTAMP)
        """, (schedule_id,))

        job_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return job_id

    def complete_job(self, job_id, success=True, backup_path=None, backup_size=None, error_message=None):
        """ジョブを完了"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
        UPDATE backup_jobs
        SET status = 'completed', completed_at = CURRENT_TIMESTAMP, success = ?, backup_path = ?, backup_size = ?, error_message = ?
        WHERE id = ?
        """, (success, backup_path, backup_size, error_message, job_id))

        conn.commit()
        conn.close()

    def get_jobs(self, schedule_id=None, limit=None):
        """ジョブを取得"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query = "SELECT * FROM backup_jobs"
        params = []
        if schedule_id:
            query += " WHERE schedule_id = ?"
            params.append(schedule_id)

        query += " ORDER BY started_at DESC"

        if limit:
            query += " LIMIT ?"
            params.append(limit)

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        return [self._row_to_dict(cursor, r) for r in rows]

    def add_log(self, schedule_id, log_level, message, details=None):
        """ログを追加"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO backup_logs (schedule_id, log_level, message, details)
        VALUES (?, ?, ?, ?)
        """, (schedule_id, log_level, message, details))

        conn.commit()
        conn.close()

    def get_logs(self, schedule_id=None, limit=None):
        """ログを取得"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query = "SELECT * FROM backup_logs"
        params = []
        if schedule_id:
            query += " WHERE schedule_id = ?"
            params.append(schedule_id)

        query += " ORDER BY timestamp DESC"

        if limit:
            query += " LIMIT ?"
            params.append(limit)

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        return [self._row_to_dict(cursor, r) for r in rows]

    def _row_to_dict(self, cursor, row):
        """行を辞書に変換"""
        columns = [col[0] for col in cursor.description]
        return dict(zip(columns, row))

    backup_schedules = ['id', 'name', 'target_type', 'path', 'schedule_type', 'schedule_value',
                        'backup_type', 'compress', 'retention_days', 'enabled', 'created_at', 'updated_at']
    backup_jobs = ['id', 'schedule_id', 'status', 'started_at', 'completed_at', 'backup_size', 'backup_path', 'error_message', 'success']
    backup_targets = ['id', 'target_type', 'name', 'path', 'description', 'priority', 'created_at']
    backup_logs = ['id', 'schedule_id', 'log_level', 'message', 'details', 'timestamp']
    retention_policies = ['id', 'policy_name', 'backup_type', 'daily_retention', 'weekly_retention', 'monthly_retention', 'yearly_retention', 'notes']

if __name__ == '__main__':
    db = BackupScheduleDB()
    print("Backup Schedule Database initialized.")
