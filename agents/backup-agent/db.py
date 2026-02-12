#!/usr/bin/env python3
"""
Backup Agent - Database Management
Data backup, scheduling, and restore management
"""

import sqlite3
from pathlib import Path
from datetime import datetime
import json
import shutil

DB_PATH = Path(__file__).parent / "backup.db"
BACKUP_DIR = Path(__file__).parent / "backups"

def init_db():
    """Initialize database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Backups table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS backups (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        source_path TEXT NOT NULL,
        backup_type TEXT NOT NULL CHECK(backup_type IN ('full','incremental','differential')),
        compression TEXT DEFAULT 'none' CHECK(compression IN ('none','gzip','zip')),
        status TEXT DEFAULT 'completed' CHECK(status IN ('pending','running','completed','failed')),
        size_bytes INTEGER,
        file_count INTEGER,
        backup_path TEXT,
        checksum TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        completed_at TIMESTAMP,
        error_message TEXT
    )
    ''')

    # Backup schedules table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS schedules (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        source_path TEXT NOT NULL,
        schedule_type TEXT NOT NULL CHECK(schedule_type IN ('daily','weekly','monthly','cron')),
        schedule_value TEXT,
        backup_type TEXT DEFAULT 'full',
        compression TEXT DEFAULT 'gzip',
        retention_days INTEGER DEFAULT 30,
        active BOOLEAN DEFAULT 1,
        last_run TIMESTAMP,
        next_run TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Restore history table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS restores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        backup_id INTEGER NOT NULL,
        restore_path TEXT NOT NULL,
        status TEXT DEFAULT 'completed' CHECK(status IN ('pending','running','completed','failed')),
        restored_at TIMESTAMP,
        error_message TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (backup_id) REFERENCES backups(id)
    )
    ''')

    # Indexes
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_backups_status ON backups(status)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_backups_source ON backups(source_path)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_schedules_active ON schedules(active)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_restores_backup ON restores(backup_id)')

    conn.commit()
    conn.close()

    # Create backup directory
    BACKUP_DIR.mkdir(exist_ok=True)
    print("✅ Database initialized")

def create_backup(source_path, backup_type='full', compression='gzip'):
    """Create a backup"""
    import os
    import tarfile
    import hashlib

    source = Path(source_path)
    if not source.exists():
        raise ValueError(f"Source path does not exist: {source_path}")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Insert pending backup
    cursor.execute('''
    INSERT INTO backups (source_path, backup_type, compression, status)
    VALUES (?, ?, ?, 'running')
    ''', (str(source.absolute()), backup_type, compression))

    backup_id = cursor.lastrowid
    conn.commit()

    try:
        # Create backup filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"backup_{timestamp}_{backup_type}"
        if compression == 'gzip':
            backup_filename += '.tar.gz'
        elif compression == 'zip':
            backup_filename += '.zip'
        else:
            backup_filename += '.tar'

        backup_path = BACKUP_DIR / backup_filename

        # Calculate source size and file count
        total_size = 0
        file_count = 0
        for root, dirs, files in os.walk(source):
            for file in files:
                file_path = os.path.join(root, file)
                total_size += os.path.getsize(file_path)
                file_count += 1

        # Create backup archive
        if compression in ['gzip', 'none']:
            with tarfile.open(backup_path, f'w:gz' if compression == 'gzip' else 'w') as tar:
                tar.add(source, arcname=source.name)
        elif compression == 'zip':
            import zipfile
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                for root, dirs, files in os.walk(source):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, start=source.parent)
                        zf.write(file_path, arcname)

        # Calculate checksum
        checksum = hashlib.sha256(open(backup_path, 'rb').read()).hexdigest()

        # Update backup record
        cursor.execute('''
        UPDATE backups SET status = 'completed', size_bytes = ?, file_count = ?,
                          backup_path = ?, checksum = ?, completed_at = ?
        WHERE id = ?
        ''', (total_size, file_count, str(backup_path), checksum, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), backup_id))

        conn.commit()
        conn.close()

        return backup_id, str(backup_path), checksum

    except Exception as e:
        cursor.execute('''
        UPDATE backups SET status = 'failed', error_message = ?, completed_at = ?
        WHERE id = ?
        ''', (str(e), datetime.now().strftime("%Y-%m-%d %H:%M:%S"), backup_id))

        conn.commit()
        conn.close()
        raise

def restore_backup(backup_id, restore_path):
    """Restore from backup"""
    import tarfile
    import zipfile

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Get backup info
    cursor.execute('SELECT backup_path, compression, checksum FROM backups WHERE id = ?', (backup_id,))
    backup = cursor.fetchone()

    if not backup:
        raise ValueError(f"Backup not found: {backup_id}")

    backup_file, compression, stored_checksum = backup

    # Insert restore record
    cursor.execute('''
    INSERT INTO restores (backup_id, restore_path, status)
    VALUES (?, ?, 'running')
    ''', (backup_id, restore_path))

    restore_id = cursor.lastrowid
    conn.commit()

    try:
        restore_dir = Path(restore_path)
        restore_dir.mkdir(parents=True, exist_ok=True)

        # Verify checksum
        actual_checksum = hashlib.sha256(open(backup_file, 'rb').read()).hexdigest()
        if actual_checksum != stored_checksum:
            raise ValueError("Checksum mismatch - backup may be corrupted")

        # Extract backup
        if compression in ['gzip', 'none']:
            with tarfile.open(backup_file, 'r:gz' if compression == 'gzip' else 'r') as tar:
                tar.extractall(restore_dir)
        elif compression == 'zip':
            with zipfile.ZipFile(backup_file, 'r') as zf:
                zf.extractall(restore_dir)

        # Update restore record
        cursor.execute('''
        UPDATE restores SET status = 'completed', restored_at = ?
        WHERE id = ?
        ''', (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), restore_id))

        conn.commit()
        conn.close()

        return restore_id

    except Exception as e:
        cursor.execute('''
        UPDATE restores SET status = 'failed', error_message = ?
        WHERE id = ?
        ''', (str(e), restore_id))

        conn.commit()
        conn.close()
        raise

def create_schedule(name, source_path, schedule_type, schedule_value, backup_type='full',
                    compression='gzip', retention_days=30):
    """Create a backup schedule"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Calculate next run
    next_run = calculate_next_run(schedule_type, schedule_value)

    cursor.execute('''
    INSERT INTO schedules (name, source_path, schedule_type, schedule_value,
                          backup_type, compression, retention_days, next_run)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (name, source_path, schedule_type, schedule_value, backup_type,
          compression, retention_days, next_run))

    schedule_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return schedule_id

def calculate_next_run(schedule_type, schedule_value):
    """Calculate next scheduled run time"""
    from datetime import timedelta

    now = datetime.now()

    if schedule_type == 'daily':
        if schedule_value:
            # Parse time (e.g., "02:00")
            try:
                hour, minute = map(int, schedule_value.split(':'))
                next_run = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
                if next_run <= now:
                    next_run += timedelta(days=1)
            except:
                next_run = now + timedelta(days=1)
        else:
            next_run = now + timedelta(days=1)

    elif schedule_type == 'weekly':
        # schedule_value: day of week (0-6 or Mon-Sun)
        days = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
        target_day = schedule_value.lower()
        try:
            target_index = days.index(target_day)
            current_index = now.weekday()
            days_until = (target_index - current_index) % 7
            if days_until == 0:
                days_until = 7
            next_run = now + timedelta(days=days_until)
            next_run = next_run.replace(hour=2, minute=0, second=0, microsecond=0)
        except:
            next_run = now + timedelta(weeks=1)

    elif schedule_type == 'monthly':
        # schedule_value: day of month (1-31)
        try:
            target_day = int(schedule_value)
            if target_day < 1 or target_day > 31:
                target_day = 1
            next_run = now.replace(day=min(target_day, 28), hour=2, minute=0, second=0, microsecond=0)
            if next_run <= now:
                next_run = (next_run.replace(day=1) + timedelta(days=32)).replace(day=min(target_day, 28))
        except:
            next_run = now + timedelta(days=32)
            next_run = next_run.replace(day=1, hour=2, minute=0, second=0, microsecond=0)

    else:  # cron or default
        next_run = now + timedelta(hours=1)

    return next_run.strftime("%Y-%m-%d %H:%M:%S")

def get_backups(status=None, source_path=None, limit=20):
    """Get backups with filters"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    query = 'SELECT id, source_path, backup_type, status, size_bytes, file_count, created_at FROM backups WHERE 1=1'
    params = []

    if status:
        query += ' AND status = ?'
        params.append(status)

    if source_path:
        query += ' AND source_path = ?'
        params.append(source_path)

    query += ' ORDER BY created_at DESC LIMIT ?'
    params.append(limit)

    cursor.execute(query, params)
    backups = cursor.fetchall()
    conn.close()
    return backups

def get_schedules(active_only=True):
    """Get schedules"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    if active_only:
        cursor.execute('''
        SELECT id, name, source_path, schedule_type, schedule_value, last_run, next_run
        FROM schedules WHERE active = 1 ORDER BY next_run
        ''')
    else:
        cursor.execute('SELECT id, name, source_path, schedule_type, schedule_value, active, last_run, next_run FROM schedules')

    schedules = cursor.fetchall()
    conn.close()
    return schedules

def get_restores(backup_id=None):
    """Get restore history"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    if backup_id:
        cursor.execute('''
        SELECT id, backup_id, restore_path, status, restored_at
        FROM restores WHERE backup_id = ? ORDER BY created_at DESC
        ''', (backup_id,))
    else:
        cursor.execute('''
        SELECT id, backup_id, restore_path, status, restored_at
        FROM restores ORDER BY created_at DESC LIMIT 20
        ''')

    restores = cursor.fetchall()
    conn.close()
    return restores

def delete_backup(backup_id):
    """Delete a backup"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Get backup path
    cursor.execute('SELECT backup_path FROM backups WHERE id = ?', (backup_id,))
    backup = cursor.fetchone()

    if backup and backup[0]:
        backup_file = Path(backup[0])
        if backup_file.exists():
            backup_file.unlink()

    # Delete from database
    cursor.execute('DELETE FROM backups WHERE id = ?', (backup_id,))

    conn.commit()
    conn.close()

def cleanup_old_backups(retention_days=30):
    """Clean up backups older than retention days"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cutoff = (datetime.now() - timedelta(days=retention_days)).strftime("%Y-%m-%d %H:%M:%S")

    # Get old backups
    cursor.execute('SELECT id, backup_path FROM backups WHERE created_at < ?', (cutoff,))
    old_backups = cursor.fetchall()

    deleted_count = 0
    for backup_id, backup_path in old_backups:
        if backup_path:
            backup_file = Path(backup_path)
            if backup_file.exists():
                backup_file.unlink()
        cursor.execute('DELETE FROM backups WHERE id = ?', (backup_id,))
        deleted_count += 1

    conn.commit()
    conn.close()
    return deleted_count

def get_stats():
    """Get backup statistics"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Total backups by status
    cursor.execute('SELECT status, COUNT(*) FROM backups GROUP BY status')
    status_counts = dict(cursor.fetchall())

    # Total size
    cursor.execute('SELECT SUM(size_bytes) FROM backups WHERE status = "completed"')
    total_size = cursor.fetchone()[0] or 0

    # Active schedules
    cursor.execute('SELECT COUNT(*) FROM schedules WHERE active = 1')
    active_schedules = cursor.fetchone()[0]

    # Recent restores
    cursor.execute('SELECT COUNT(*) FROM restores WHERE created_at >= datetime("now", "-7 days")')
    recent_restores = cursor.fetchone()[0]

    conn.close()

    return {
        'status_counts': status_counts,
        'total_size_bytes': total_size,
        'active_schedules': active_schedules,
        'recent_restores': recent_restores
    }

if __name__ == '__main__':
    init_db()
