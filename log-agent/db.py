#!/usr/bin/env python3
"""
Log Agent - Database Management
System logs and monitoring management
"""

import sqlite3
from pathlib import Path
from datetime import datetime
import json
import gzip
import zlib

DB_PATH = Path(__file__).parent / "log.db"
LOGS_DIR = Path(__file__).parent / "logs"

def init_db():
    """Initialize database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Logs table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        level TEXT NOT NULL CHECK(level IN ('DEBUG','INFO','WARNING','ERROR','CRITICAL')),
        source TEXT,
        message TEXT NOT NULL,
        details TEXT,
        tags TEXT,
        stack_trace TEXT,
        correlation_id TEXT,
        compressed BOOLEAN DEFAULT 0
    )
    ''')

    # Log sources table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS sources (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        type TEXT NOT NULL CHECK(type IN ('application','system','service','external')),
        enabled BOOLEAN DEFAULT 1,
        config TEXT,
        last_log TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Log alerts table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS alerts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        condition TEXT NOT NULL,
        level TEXT CHECK(level IN ('WARNING','ERROR','CRITICAL')),
        threshold INTEGER,
        time_window INTEGER,
        active BOOLEAN DEFAULT 1,
        notification_count INTEGER DEFAULT 0,
        last_triggered TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Alert history table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS alert_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        alert_id INTEGER NOT NULL,
        triggered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        matched_logs TEXT,
        context TEXT,
        acknowledged BOOLEAN DEFAULT 0,
        acknowledged_at TIMESTAMP,
        notes TEXT,
        FOREIGN KEY (alert_id) REFERENCES alerts(id)
    )
    ''')

    # Log statistics table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS statistics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL UNIQUE,
        source TEXT,
        level TEXT,
        count INTEGER DEFAULT 0,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Indexes
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_logs_timestamp ON logs(timestamp)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_logs_level ON logs(level)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_logs_source ON logs(source)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_logs_correlation ON logs(correlation_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_alert_history_alert ON alert_history(alert_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_statistics_date ON statistics(date)')

    conn.commit()
    conn.close()

    # Create logs directory
    LOGS_DIR.mkdir(exist_ok=True)
    print("✅ Database initialized")

def add_log(level, message, source=None, details=None, tags=None, stack_trace=None, correlation_id=None):
    """Add a log entry"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    details_json = json.dumps(details) if details else None
    tags_json = json.dumps(tags) if tags else None

    cursor.execute('''
    INSERT INTO logs (level, message, source, details, tags, stack_trace, correlation_id)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (level.upper(), message, source, details_json, tags_json, stack_trace, correlation_id))

    log_id = cursor.lastrowid

    # Update statistics
    today = datetime.now().strftime('%Y-%m-%d')
    cursor.execute('''
    INSERT OR REPLACE INTO statistics (date, source, level, count, updated_at)
    VALUES (?, ?, ?, COALESCE((SELECT count FROM statistics WHERE date = ? AND source = ? AND level = ?), 0) + 1, CURRENT_TIMESTAMP)
    ''', (today, source, level.upper(), today, source, level.upper()))

    conn.commit()
    conn.close()
    return log_id

def get_logs(level=None, source=None, start_time=None, end_time=None, limit=100):
    """Get logs with optional filters"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    query = 'SELECT * FROM logs WHERE 1=1'
    params = []

    if level:
        query += ' AND level = ?'
        params.append(level.upper())
    if source:
        query += ' AND source = ?'
        params.append(source)
    if start_time:
        query += ' AND timestamp >= ?'
        params.append(start_time)
    if end_time:
        query += ' AND timestamp <= ?'
        params.append(end_time)

    query += ' ORDER BY timestamp DESC LIMIT ?'
    params.append(limit)

    cursor.execute(query, params)
    logs = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return logs

def get_log_stats(source=None, days=7):
    """Get log statistics"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    if source:
        cursor.execute('''
        SELECT level, SUM(count) as total
        FROM statistics
        WHERE source = ? AND date >= date('now', ?)
        GROUP BY level
        ORDER BY level
        ''', (source, f'-{days} days'))
    else:
        cursor.execute('''
        SELECT level, SUM(count) as total
        FROM statistics
        WHERE date >= date('now', ?)
        GROUP BY level
        ORDER BY level
        ''', (f'-{days} days',))

    stats = {row['level']: row['total'] for row in cursor.fetchall()}
    conn.close()
    return stats

def create_source(name, source_type, config=None):
    """Create a log source"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    config_json = json.dumps(config) if config else None
    cursor.execute('''
    INSERT INTO sources (name, type, config)
    VALUES (?, ?, ?)
    ''', (name, source_type, config_json))

    conn.commit()
    conn.close()

def get_sources(enabled_only=True):
    """Get log sources"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    if enabled_only:
        cursor.execute('SELECT * FROM sources WHERE enabled = 1')
    else:
        cursor.execute('SELECT * FROM sources')

    sources = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return sources

def create_alert(name, condition, level='ERROR', threshold=None, time_window=None):
    """Create a log alert"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO alerts (name, condition, level, threshold, time_window)
    VALUES (?, ?, ?, ?, ?)
    ''', (name, condition, level, threshold, time_window))

    conn.commit()
    conn.close()

def get_alerts(active_only=True):
    """Get alerts"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    if active_only:
        cursor.execute('SELECT * FROM alerts WHERE active = 1')
    else:
        cursor.execute('SELECT * FROM alerts')

    alerts = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return alerts

def get_alert_history(alert_id=None, acknowledged=False, limit=50):
    """Get alert history"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    query = 'SELECT * FROM alert_history WHERE 1=1'
    params = []

    if alert_id:
        query += ' AND alert_id = ?'
        params.append(alert_id)
    if acknowledged is not None:
        query += ' AND acknowledged = ?'
        params.append(acknowledged)

    query += ' ORDER BY triggered_at DESC LIMIT ?'
    params.append(limit)

    cursor.execute(query, params)
    history = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return history

def acknowledge_alert(alert_history_id, notes=None):
    """Acknowledge an alert"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    UPDATE alert_history
    SET acknowledged = 1, acknowledged_at = CURRENT_TIMESTAMP, notes = ?
    WHERE id = ?
    ''', (notes, alert_history_id))

    conn.commit()
    conn.close()

def export_logs_to_file(start_time=None, end_time=None, output_path=None):
    """Export logs to a file"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    query = 'SELECT * FROM logs WHERE 1=1'
    params = []

    if start_time:
        query += ' AND timestamp >= ?'
        params.append(start_time)
    if end_time:
        query += ' AND timestamp <= ?'
        params.append(end_time)

    query += ' ORDER BY timestamp'

    cursor.execute(query, params)
    logs = [dict(row) for row in cursor.fetchall()]
    conn.close()

    if not output_path:
        output_path = LOGS_DIR / f"logs_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(logs, f, ensure_ascii=False, indent=2)

    return output_path

def search_logs(query, limit=50):
    """Search logs by message content"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute('''
    SELECT * FROM logs WHERE message LIKE ? OR details LIKE ?
    ORDER BY timestamp DESC LIMIT ?
    ''', (f'%{query}%', f'%{query}%', limit))

    logs = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return logs

if __name__ == '__main__':
    init_db()
