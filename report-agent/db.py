#!/usr/bin/env python3
"""
Report Agent - Database Management
Reports, analytics, and exports management
"""

import sqlite3
from pathlib import Path
from datetime import datetime
import json
import csv

DB_PATH = Path(__file__).parent / "report.db"

def init_db():
    """Initialize database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Reports table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS reports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT,
        report_type TEXT NOT NULL CHECK(report_type IN ('summary','analytics','trend','comparison','custom')),
        source TEXT,
        status TEXT DEFAULT 'draft' CHECK(status IN ('draft','generating','ready','scheduled')),
        data TEXT,
        format TEXT DEFAULT 'json' CHECK(format IN ('json','csv','pdf','html')),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        scheduled_at TIMESTAMP
    )
    ''')

    # Analytics data table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS analytics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        report_id INTEGER,
        metric_name TEXT NOT NULL,
        metric_value REAL,
        metric_unit TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        category TEXT,
        tags TEXT,
        FOREIGN KEY (report_id) REFERENCES reports(id)
    )
    ''')

    # Export history table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS exports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        report_id INTEGER NOT NULL,
        format TEXT NOT NULL,
        file_path TEXT,
        status TEXT DEFAULT 'pending' CHECK(status IN ('pending','processing','completed','failed')),
        exported_at TIMESTAMP,
        file_size INTEGER,
        error_message TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (report_id) REFERENCES reports(id)
    )
    ''')

    # Report templates table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS templates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        description TEXT,
        template_type TEXT NOT NULL CHECK(template_type IN ('summary','analytics','trend','comparison','custom')),
        config TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Indexes
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_reports_status ON reports(status)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_reports_type ON reports(report_type)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_analytics_report ON analytics(report_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_analytics_timestamp ON analytics(timestamp)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_exports_report ON exports(report_id)')

    conn.commit()
    conn.close()
    print("✅ Database initialized")

def create_report(title, report_type, description=None, source=None, config=None):
    """Create a new report"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    data_json = json.dumps(config) if config else None
    cursor.execute('''
    INSERT INTO reports (title, description, report_type, source, data)
    VALUES (?, ?, ?, ?, ?)
    ''', (title, description, report_type, source, data_json))

    conn.commit()
    report_id = cursor.lastrowid
    conn.close()
    return report_id

def get_report(report_id):
    """Get report by ID"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM reports WHERE id = ?', (report_id,))
    report = cursor.fetchone()
    conn.close()
    return dict(report) if report else None

def list_reports(status=None, report_type=None, limit=50):
    """List reports with optional filters"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    query = 'SELECT * FROM reports WHERE 1=1'
    params = []

    if status:
        query += ' AND status = ?'
        params.append(status)
    if report_type:
        query += ' AND report_type = ?'
        params.append(report_type)

    query += ' ORDER BY created_at DESC LIMIT ?'
    params.append(limit)

    cursor.execute(query, params)
    reports = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return reports

def add_analytics(report_id, metric_name, metric_value, unit=None, category=None, tags=None):
    """Add analytics data point"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    tags_json = json.dumps(tags) if tags else None
    cursor.execute('''
    INSERT INTO analytics (report_id, metric_name, metric_value, metric_unit, category, tags)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', (report_id, metric_name, metric_value, unit, category, tags_json))

    conn.commit()
    conn.close()

def get_analytics(report_id, category=None, limit=100):
    """Get analytics data for a report"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    query = 'SELECT * FROM analytics WHERE report_id = ?'
    params = [report_id]

    if category:
        query += ' AND category = ?'
        params.append(category)

    query += ' ORDER BY timestamp DESC LIMIT ?'
    params.append(limit)

    cursor.execute(query, params)
    analytics = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return analytics

def create_template(name, template_type, config, description=None):
    """Create a report template"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    config_json = json.dumps(config)
    cursor.execute('''
    INSERT INTO templates (name, description, template_type, config)
    VALUES (?, ?, ?, ?)
    ''', (name, description, template_type, config_json))

    conn.commit()
    conn.close()

def get_template(name):
    """Get template by name"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM templates WHERE name = ?', (name,))
    template = cursor.fetchone()
    conn.close()
    return dict(template) if template else None

def export_report(report_id, format='csv'):
    """Export report to specified format"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Update export status
    cursor.execute('''
    INSERT INTO exports (report_id, format, status)
    VALUES (?, ?, 'processing')
    ''', (report_id, format))
    export_id = cursor.lastrowid

    report = get_report(report_id)
    if not report:
        cursor.execute('UPDATE exports SET status = ?, error_message = ? WHERE id = ?',
                      ('failed', 'Report not found', export_id))
        conn.commit()
        conn.close()
        return None

    # Generate export
    try:
        filename = f"report_{report_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{format}"
        file_path = Path(__file__).parent / "exports" / filename
        file_path.parent.mkdir(exist_ok=True)

        analytics_data = get_analytics(report_id)

        if format == 'json':
            export_data = {
                'report': report,
                'analytics': analytics_data
            }
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)

        elif format == 'csv':
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                if analytics_data:
                    writer = csv.DictWriter(f, fieldnames=analytics_data[0].keys())
                    writer.writeheader()
                    writer.writerows(analytics_data)

        cursor.execute('''
        UPDATE exports SET status = 'completed', file_path = ?, exported_at = CURRENT_TIMESTAMP, file_size = ?
        WHERE id = ?
        ''', (str(file_path), file_path.stat().st_size, export_id))

        conn.commit()
        conn.close()
        return str(file_path)

    except Exception as e:
        cursor.execute('UPDATE exports SET status = ?, error_message = ? WHERE id = ?',
                      ('failed', str(e), export_id))
        conn.commit()
        conn.close()
        return None

def get_exports(report_id=None):
    """Get export history"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    if report_id:
        cursor.execute('SELECT * FROM exports WHERE report_id = ? ORDER BY created_at DESC', (report_id,))
    else:
        cursor.execute('SELECT * FROM exports ORDER BY created_at DESC')

    exports = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return exports

if __name__ == '__main__':
    init_db()
