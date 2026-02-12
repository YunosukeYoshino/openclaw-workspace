"""
Backup Schedule Agent Database Module
SQLite-based data storage for scheduled backups
"""
import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional

class BackupScheduleDB:
    """Database manager for backup schedule agent"""

    def __init__(self, db_path: str = "backup_schedule.db"):
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
            CREATE TABLE IF NOT EXISTS backup_schedules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                target_type TEXT NOT NULL,
                target_path TEXT NOT NULL,
                schedule_type TEXT NOT NULL,
                schedule_value TEXT NOT NULL,
                backup_type TEXT DEFAULT 'full',
                compression INTEGER DEFAULT 1,
                retention_days INTEGER DEFAULT 30,
                enabled INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                notes TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS backup_jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                schedule_id INTEGER,
                status TEXT DEFAULT 'pending',
                started_at TIMESTAMP,
                completed_at TIMESTAMP,
                backup_size_bytes INTEGER,
                backup_path TEXT,
                error_message TEXT,
                success INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (schedule_id) REFERENCES backup_schedules(id)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS backup_targets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                target_type TEXT NOT NULL,
                target_name TEXT NOT NULL,
                target_path TEXT NOT NULL,
                description TEXT,
                priority TEXT DEFAULT 'medium',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS backup_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                schedule_id INTEGER,
                log_level TEXT NOT NULL,
                message TEXT NOT NULL,
                details TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS retention_policies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                policy_name TEXT NOT NULL,
                backup_type TEXT,
                daily_retention INTEGER,
                weekly_retention INTEGER,
                monthly_retention INTEGER,
                yearly_retention INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                notes TEXT
            )
        ''')

        conn.commit()
        conn.close()

    def add_backup_schedule(self, name: str, target_type: str, target_path: str,
                          schedule_type: str, schedule_value: str,
                          backup_type: str = 'full', compression: bool = True,
                          retention_days: int = 30, notes: str = None) -> int:
        """Add a backup schedule"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO backup_schedules (name, target_type, target_path, schedule_type,
                                         schedule_value, backup_type, compression, retention_days, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (name, target_type, target_path, schedule_type, schedule_value,
              backup_type, 1 if compression else 0, retention_days, notes))

        schedule_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return schedule_id

    def get_backup_schedules(self, target_type: str = None, enabled: bool = None) -> List[Dict]:
        """Get backup schedules"""
        conn = self.get_connection()
        cursor = conn.cursor()

        query = "SELECT * FROM backup_schedules WHERE 1=1"
        params = []

        if target_type:
            query += " AND target_type = ?"
            params.append(target_type)

        if enabled is not None:
            query += " AND enabled = ?"
            params.append(1 if enabled else 0)

        query += " ORDER BY created_at DESC"

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def get_backup_schedule(self, schedule_id: int) -> Optional[Dict]:
        """Get a specific backup schedule"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM backup_schedules WHERE id = ?", (schedule_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    def update_backup_schedule(self, schedule_id: int, schedule_type: str = None,
                              schedule_value: str = None, retention_days: int = None,
                              enabled: bool = None) -> bool:
        """Update backup schedule"""
        conn = self.get_connection()
        cursor = conn.cursor()

        updates = []
        params = []

        if schedule_type:
            updates.append("schedule_type = ?")
            params.append(schedule_type)

        if schedule_value:
            updates.append("schedule_value = ?")
            params.append(schedule_value)

        if retention_days:
            updates.append("retention_days = ?")
            params.append(retention_days)

        if enabled is not None:
            updates.append("enabled = ?")
            params.append(1 if enabled else 0)

        if updates:
            updates.append("updated_at = CURRENT_TIMESTAMP")
            params.append(schedule_id)
            query = f"UPDATE backup_schedules SET {', '.join(updates)} WHERE id = ?"
            cursor.execute(query, params)
            conn.commit()
            conn.close()
            return True

        conn.close()
        return False

    def toggle_schedule_enabled(self, schedule_id: int) -> bool:
        """Toggle schedule enabled status"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT enabled FROM backup_schedules WHERE id = ?", (schedule_id,))
        result = cursor.fetchone()

        if result:
            new_status = 0 if result['enabled'] == 1 else 1
            cursor.execute("UPDATE backup_schedules SET enabled = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                         (new_status, schedule_id))
            conn.commit()
            conn.close()
            return new_status == 1

        conn.close()
        return False

    def delete_backup_schedule(self, schedule_id: int) -> bool:
        """Delete a backup schedule"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM backup_schedules WHERE id = ?", (schedule_id,))
        conn.commit()
        conn.close()
        return True

    def add_backup_job(self, schedule_id: int, status: str = 'pending') -> int:
        """Add a backup job"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO backup_jobs (schedule_id, status)
            VALUES (?, ?)
        ''', (schedule_id, status))

        job_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return job_id

    def update_backup_job(self, job_id: int, status: str = None,
                         backup_size_bytes: int = None, backup_path: str = None,
                         error_message: str = None, success: bool = None) -> bool:
        """Update backup job"""
        conn = self.get_connection()
        cursor = conn.cursor()

        updates = []
        params = []

        if status:
            updates.append("status = ?")
            params.append(status)
            if status == 'running':
                updates.append("started_at = CURRENT_TIMESTAMP")
            elif status == 'completed':
                updates.append("completed_at = CURRENT_TIMESTAMP")

        if backup_size_bytes:
            updates.append("backup_size_bytes = ?")
            params.append(backup_size_bytes)

        if backup_path:
            updates.append("backup_path = ?")
            params.append(backup_path)

        if error_message:
            updates.append("error_message = ?")
            params.append(error_message)

        if success is not None:
            updates.append("success = ?")
            params.append(1 if success else 0)

        if updates:
            params.append(job_id)
            query = f"UPDATE backup_jobs SET {', '.join(updates)} WHERE id = ?"
            cursor.execute(query, params)
            conn.commit()
            conn.close()
            return True

        conn.close()
        return False

    def get_backup_jobs(self, schedule_id: int = None, status: str = None, limit: int = 50) -> List[Dict]:
        """Get backup jobs"""
        conn = self.get_connection()
        cursor = conn.cursor()

        query = "SELECT * FROM backup_jobs WHERE 1=1"
        params = []

        if schedule_id:
            query += " AND schedule_id = ?"
            params.append(schedule_id)

        if status:
            query += " AND status = ?"
            params.append(status)

        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def add_backup_target(self, target_type: str, target_name: str, target_path: str,
                         description: str = None, priority: str = 'medium') -> int:
        """Add a backup target"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO backup_targets (target_type, target_name, target_path, description, priority)
            VALUES (?, ?, ?, ?, ?)
        ''', (target_type, target_name, target_path, description, priority))

        target_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return target_id

    def get_backup_targets(self, target_type: str = None) -> List[Dict]:
        """Get backup targets"""
        conn = self.get_connection()
        cursor = conn.cursor()

        if target_type:
            cursor.execute("SELECT * FROM backup_targets WHERE target_type = ? ORDER BY created_at DESC", (target_type,))
        else:
            cursor.execute("SELECT * FROM backup_targets ORDER BY created_at DESC")

        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def delete_backup_target(self, target_id: int) -> bool:
        """Delete a backup target"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM backup_targets WHERE id = ?", (target_id,))
        conn.commit()
        conn.close()
        return True

    def add_log(self, schedule_id: int, log_level: str, message: str, details: str = None) -> int:
        """Add a log entry"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO backup_logs (schedule_id, log_level, message, details)
            VALUES (?, ?, ?, ?)
        ''', (schedule_id, log_level, message, details))

        log_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return log_id

    def get_logs(self, schedule_id: int = None, log_level: str = None, limit: int = 50) -> List[Dict]:
        """Get log entries"""
        conn = self.get_connection()
        cursor = conn.cursor()

        query = "SELECT * FROM backup_logs WHERE 1=1"
        params = []

        if schedule_id:
            query += " AND schedule_id = ?"
            params.append(schedule_id)

        if log_level:
            query += " AND log_level = ?"
            params.append(log_level)

        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def add_retention_policy(self, policy_name: str, backup_type: str,
                            daily_retention: int = None, weekly_retention: int = None,
                            monthly_retention: int = None, yearly_retention: int = None,
                            notes: str = None) -> int:
        """Add a retention policy"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO retention_policies (policy_name, backup_type, daily_retention,
                                           weekly_retention, monthly_retention, yearly_retention, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (policy_name, backup_type, daily_retention, weekly_retention,
              monthly_retention, yearly_retention, notes))

        policy_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return policy_id

    def get_retention_policies(self, backup_type: str = None) -> List[Dict]:
        """Get retention policies"""
        conn = self.get_connection()
        cursor = conn.cursor()

        if backup_type:
            cursor.execute("SELECT * FROM retention_policies WHERE backup_type = ?", (backup_type,))
        else:
            cursor.execute("SELECT * FROM retention_policies ORDER BY created_at DESC")

        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def get_backup_summary(self) -> Dict:
        """Get backup summary"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Total schedules
        cursor.execute("SELECT COUNT(*) as total FROM backup_schedules")
        total_schedules = cursor.fetchone()['total']

        # Enabled schedules
        cursor.execute("SELECT COUNT(*) as total FROM backup_schedules WHERE enabled = 1")
        enabled_schedules = cursor.fetchone()['total']

        # Jobs in last 24h
        cursor.execute('''
            SELECT COUNT(*) as total FROM backup_jobs
            WHERE created_at >= datetime('now', '-24 hours')
        ''')
        recent_jobs = cursor.fetchone()['total']

        # Successful jobs
        cursor.execute('''
            SELECT COUNT(*) as total FROM backup_jobs
            WHERE success = 1
        ''')
        successful_jobs = cursor.fetchone()['total']

        # Failed jobs
        cursor.execute('''
            SELECT COUNT(*) as total FROM backup_jobs
            WHERE success = 0 AND status = 'completed'
        ''')
        failed_jobs = cursor.fetchone()['total']

        # Total backup size
        cursor.execute("SELECT SUM(backup_size_bytes) as total FROM backup_jobs WHERE backup_size_bytes IS NOT NULL")
        total_size = cursor.fetchone()['total'] or 0

        conn.close()
        return {
            'total_schedules': total_schedules,
            'enabled_schedules': enabled_schedules,
            'recent_jobs_24h': recent_jobs,
            'successful_jobs': successful_jobs,
            'failed_jobs': failed_jobs,
            'total_backup_size_bytes': total_size
        }

    def get_due_backups(self) -> List[Dict]:
        """Get backups that are due"""
        # This is a simplified version - in production, you'd need proper schedule evaluation
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM backup_schedules
            WHERE enabled = 1
            ORDER BY created_at DESC
        ''')

        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
