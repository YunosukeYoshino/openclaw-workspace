#!/usr/bin/env python3
"""
Monitor Agent - Database Management
Metrics and alerts management
"""

import sqlite3
from pathlib import Path
from datetime import datetime
import json

DB_PATH = Path(__file__).parent / "monitor.db"

def init_db():
    """Initialize database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Metrics table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS metrics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        metric_name TEXT NOT NULL,
        metric_type TEXT CHECK(metric_type IN ('counter','gauge','histogram','summary')),
        value REAL NOT NULL,
        unit TEXT,
        labels TEXT,
        source TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Monitored services table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS services (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        type TEXT CHECK(type IN ('api','database','cache','queue','worker','external','custom')),
        endpoint TEXT,
        environment TEXT,
        health_check_enabled BOOLEAN DEFAULT 1,
        health_check_interval INTEGER DEFAULT 60,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Metric definitions table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS metric_definitions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        service_id INTEGER,
        metric_name TEXT NOT NULL,
        description TEXT,
        metric_type TEXT CHECK(metric_type IN ('counter','gauge','histogram','summary')),
        unit TEXT,
        aggregation_method TEXT DEFAULT 'avg' CHECK(aggregation_method IN ('avg','sum','min','max','count')),
        retention_days INTEGER DEFAULT 30,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (service_id) REFERENCES services(id)
    )
    ''')

    # Alerts table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS alerts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        metric_name TEXT NOT NULL,
        condition TEXT NOT NULL,
        threshold REAL NOT NULL,
        comparison_operator TEXT DEFAULT '>' CHECK(comparison_operator IN ('>','<','>=','<=','==','!=')),
        time_window INTEGER DEFAULT 300,
        aggregation_method TEXT DEFAULT 'avg' CHECK(aggregation_method IN ('avg','sum','min','max','count')),
        severity TEXT DEFAULT 'warning' CHECK(severity IN ('info','warning','error','critical')),
        enabled BOOLEAN DEFAULT 1,
        notification_channels TEXT,
        cooldown_minutes INTEGER DEFAULT 10,
        last_triggered TIMESTAMP,
        trigger_count INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Alert triggers table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS alert_triggers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        alert_id INTEGER NOT NULL,
        triggered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        actual_value REAL NOT NULL,
        threshold REAL NOT NULL,
        severity TEXT,
        acknowledged BOOLEAN DEFAULT 0,
        acknowledged_at TIMESTAMP,
        acknowledged_by TEXT,
        notes TEXT,
        resolved BOOLEAN DEFAULT 0,
        resolved_at TIMESTAMP,
        FOREIGN KEY (alert_id) REFERENCES alerts(id)
    )
    ''')

    # Health checks table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS health_checks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        service_id INTEGER NOT NULL,
        check_type TEXT CHECK(check_type IN ('http','tcp','database','custom')),
        endpoint TEXT,
        status TEXT DEFAULT 'unknown' CHECK(status IN ('unknown','healthy','unhealthy','degraded')),
        response_time_ms INTEGER,
        status_code INTEGER,
        error_message TEXT,
        checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (service_id) REFERENCES services(id)
    )
    ''')

    # Metric aggregations table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS metric_aggregations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        metric_name TEXT NOT NULL,
        aggregation_type TEXT CHECK(aggregation_type IN ('avg','sum','min','max','count','p50','p75','p90','p95','p99')),
        window_start TIMESTAMP NOT NULL,
        window_end TIMESTAMP NOT NULL,
        value REAL NOT NULL,
        labels TEXT,
        calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Incident reports table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS incidents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT,
        severity TEXT CHECK(severity IN ('minor','major','critical')),
        status TEXT DEFAULT 'open' CHECK(status IN ('open','investigating','resolved','closed')),
        detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        resolved_at TIMESTAMP,
        duration_minutes INTEGER,
        affected_services TEXT,
        root_cause TEXT,
        resolution TEXT,
        postmortem TEXT,
        created_by TEXT,
        assigned_to TEXT,
        FOREIGN KEY (affected_services) REFERENCES services(id)
    )
    ''')

    # Dashboards table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS dashboards (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        layout TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Dashboard widgets table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS widgets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        dashboard_id INTEGER NOT NULL,
        widget_type TEXT CHECK(widget_type IN ('line','bar','gauge','stat','table','log')),
        title TEXT,
        metric_name TEXT,
        query TEXT,
        config TEXT,
        position_x INTEGER DEFAULT 0,
        position_y INTEGER DEFAULT 0,
        width INTEGER DEFAULT 4,
        height INTEGER DEFAULT 3,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (dashboard_id) REFERENCES dashboards(id)
    )
    ''')

    # Indexes
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_metrics_name ON metrics(metric_name)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_metrics_timestamp ON metrics(timestamp)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_services_name ON services(name)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_alerts_name ON alerts(name)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_alert_triggers_alert ON alert_triggers(alert_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_health_checks_service ON health_checks(service_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_metric_aggregations_metric ON metric_aggregations(metric_name)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_incidents_status ON incidents(status)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_widgets_dashboard ON widgets(dashboard_id)')

    conn.commit()
    conn.close()
    print("✅ Database initialized")

def create_service(name, service_type, endpoint=None, environment=None, health_check_interval=60):
    """Create a monitored service"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO services (name, type, endpoint, environment, health_check_interval)
    VALUES (?, ?, ?, ?, ?)
    ''', (name, service_type, endpoint, environment, health_check_interval))

    conn.commit()
    service_id = cursor.lastrowid
    conn.close()
    return service_id

def get_services(enabled_only=True):
    """Get monitored services"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    if enabled_only:
        cursor.execute('SELECT * FROM services WHERE health_check_enabled = 1')
    else:
        cursor.execute('SELECT * FROM services')

    services = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return services

def record_metric(metric_name, value, metric_type='gauge', unit=None, labels=None, source=None):
    """Record a metric"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    labels_json = json.dumps(labels) if labels else None
    cursor.execute('''
    INSERT INTO metrics (metric_name, metric_type, value, unit, labels, source)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', (metric_name, metric_type, value, unit, labels_json, source))

    conn.commit()
    conn.close()

def get_metrics(metric_name=None, start_time=None, end_time=None, labels=None, limit=1000):
    """Get metrics with optional filters"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    query = 'SELECT * FROM metrics WHERE 1=1'
    params = []

    if metric_name:
        query += ' AND metric_name = ?'
        params.append(metric_name)
    if start_time:
        query += ' AND timestamp >= ?'
        params.append(start_time)
    if end_time:
        query += ' AND timestamp <= ?'
        params.append(end_time)

    query += ' ORDER BY timestamp DESC LIMIT ?'
    params.append(limit)

    cursor.execute(query, params)
    metrics = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return metrics

def create_alert(name, metric_name, threshold, condition='>', time_window=300, severity='warning',
                aggregation_method='avg', notification_channels=None):
    """Create an alert"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    channels_json = json.dumps(notification_channels) if notification_channels else None
    cursor.execute('''
    INSERT INTO alerts (name, metric_name, threshold, comparison_operator, time_window, aggregation_method, severity, notification_channels)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (name, metric_name, threshold, condition, time_window, aggregation_method, severity, channels_json))

    conn.commit()
    alert_id = cursor.lastrowid
    conn.close()
    return alert_id

def get_alerts(enabled_only=True):
    """Get alerts"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    if enabled_only:
        cursor.execute('SELECT * FROM alerts WHERE enabled = 1')
    else:
        cursor.execute('SELECT * FROM alerts')

    alerts = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return alerts

def trigger_alert(alert_id, actual_value):
    """Trigger an alert"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Get alert details
    cursor.execute('SELECT * FROM alerts WHERE id = ?', (alert_id,))
    alert = cursor.fetchone()

    if not alert:
        conn.close()
        return None

    # Create trigger record
    cursor.execute('''
    INSERT INTO alert_triggers (alert_id, actual_value, threshold, severity)
    VALUES (?, ?, ?, ?)
    ''', (alert_id, actual_value, alert[4], alert[9]))

    # Update alert
    cursor.execute('''
    UPDATE alerts
    SET last_triggered = CURRENT_TIMESTAMP, trigger_count = trigger_count + 1
    WHERE id = ?
    ''', (alert_id,))

    conn.commit()
    trigger_id = cursor.lastrowid
    conn.close()
    return trigger_id

def get_alert_triggers(alert_id=None, acknowledged=False, limit=50):
    """Get alert triggers"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    query = 'SELECT * FROM alert_triggers WHERE 1=1'
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
    triggers = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return triggers

def acknowledge_trigger(trigger_id, acknowledged_by, notes=None):
    """Acknowledge an alert trigger"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    UPDATE alert_triggers
    SET acknowledged = 1, acknowledged_at = CURRENT_TIMESTAMP, acknowledged_by = ?, notes = ?
    WHERE id = ?
    ''', (acknowledged_by, notes, trigger_id))

    conn.commit()
    conn.close()

def record_health_check(service_id, check_type, status, response_time_ms=None, status_code=None, error_message=None):
    """Record a health check"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO health_checks (service_id, check_type, status, response_time_ms, status_code, error_message)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', (service_id, check_type, status, response_time_ms, status_code, error_message))

    conn.commit()
    conn.close()

def get_health_checks(service_id=None, status=None, limit=50):
    """Get health checks"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    query = 'SELECT * FROM health_checks WHERE 1=1'
    params = []

    if service_id:
        query += ' AND service_id = ?'
        params.append(service_id)
    if status:
        query += ' AND status = ?'
        params.append(status)

    query += ' ORDER BY checked_at DESC LIMIT ?'
    params.append(limit)

    cursor.execute(query, params)
    checks = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return checks

def aggregate_metrics(metric_name, aggregation_type, window_start, window_end):
    """Aggregate metrics over a time window"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    agg_func = {
        'avg': 'AVG(value)',
        'sum': 'SUM(value)',
        'min': 'MIN(value)',
        'max': 'MAX(value)',
        'count': 'COUNT(*)',
        'p50': 'percentile_50',
        'p90': 'percentile_90',
        'p95': 'percentile_95',
        'p99': 'percentile_99'
    }.get(aggregation_type, 'AVG(value)')

    if aggregation_type.startswith('p'):
        # For percentiles, we'd need a more complex query
        # Simplified version using simple aggregation
        cursor.execute(f'SELECT {agg_func} as value FROM metrics WHERE metric_name = ? AND timestamp >= ? AND timestamp <= ?',
                      (metric_name, window_start, window_end))
    else:
        cursor.execute(f'SELECT {agg_func} as value FROM metrics WHERE metric_name = ? AND timestamp >= ? AND timestamp <= ?',
                      (metric_name, window_start, window_end))

    result = cursor.fetchone()
    value = result[0] if result and result[0] is not None else 0

    # Store aggregation
    cursor.execute('''
    INSERT INTO metric_aggregations (metric_name, aggregation_type, window_start, window_end, value)
    VALUES (?, ?, ?, ?, ?)
    ''', (metric_name, aggregation_type, window_start, window_end, value))

    conn.commit()
    conn.close()
    return value

def create_incident(title, description=None, severity='major', created_by=None, assigned_to=None):
    """Create an incident"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO incidents (title, description, severity, created_by, assigned_to)
    VALUES (?, ?, ?, ?, ?)
    ''', (title, description, severity, created_by, assigned_to))

    conn.commit()
    incident_id = cursor.lastrowid
    conn.close()
    return incident_id

def update_incident(incident_id, status=None, root_cause=None, resolution=None, postmortem=None):
    """Update an incident"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    updates = []
    params = []

    if status:
        updates.append('status = ?')
        params.append(status)
        if status in ('resolved', 'closed'):
            updates.append('resolved_at = CURRENT_TIMESTAMP')
    if root_cause:
        updates.append('root_cause = ?')
        params.append(root_cause)
    if resolution:
        updates.append('resolution = ?')
        params.append(resolution)
    if postmortem:
        updates.append('postmortem = ?')
        params.append(postmortem)

    if updates:
        query = f"UPDATE incidents SET {', '.join(updates)} WHERE id = ?"
        params.append(incident_id)
        cursor.execute(query, params)
        conn.commit()

    conn.close()

def get_incidents(status=None, severity=None, limit=50):
    """Get incidents"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    query = 'SELECT * FROM incidents WHERE 1=1'
    params = []

    if status:
        query += ' AND status = ?'
        params.append(status)
    if severity:
        query += ' AND severity = ?'
        params.append(severity)

    query += ' ORDER BY detected_at DESC LIMIT ?'
    params.append(limit)

    cursor.execute(query, params)
    incidents = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return incidents

def create_dashboard(name, description=None):
    """Create a dashboard"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO dashboards (name, description)
    VALUES (?, ?)
    ''', (name, description))

    conn.commit()
    dashboard_id = cursor.lastrowid
    conn.close()
    return dashboard_id

def get_dashboards(limit=20):
    """Get dashboards"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM dashboards ORDER BY created_at DESC LIMIT ?', (limit,))
    dashboards = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return dashboards

def add_widget(dashboard_id, widget_type, title, metric_name=None, query=None, config=None, position_x=0, position_y=0, width=4, height=3):
    """Add a widget to a dashboard"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    config_json = json.dumps(config) if config else None
    cursor.execute('''
    INSERT INTO widgets (dashboard_id, widget_type, title, metric_name, query, config, position_x, position_y, width, height)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (dashboard_id, widget_type, title, metric_name, query, config_json, position_x, position_y, width, height))

    conn.commit()
    conn.close()

def get_widgets(dashboard_id):
    """Get widgets for a dashboard"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM widgets WHERE dashboard_id = ?', (dashboard_id,))
    widgets = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return widgets

def get_monitoring_summary():
    """Get monitoring summary statistics"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Get service counts
    cursor.execute('SELECT health_check_enabled, COUNT(*) as count FROM services GROUP BY health_check_enabled')
    services = {f"{'enabled' if row[0] else 'disabled'}_services": row[1] for row in cursor.fetchall()}

    # Get active incidents
    cursor.execute('SELECT COUNT(*) as count FROM incidents WHERE status IN ("open", "investigating")')
    incidents = cursor.fetchone()['count']

    # Get recent alert triggers
    cursor.execute('SELECT COUNT(*) as count FROM alert_triggers WHERE triggered_at >= datetime("now", "-1 hour")')
    recent_alerts = cursor.fetchone()['count']

    # Get health status
    cursor.execute('SELECT status, COUNT(*) as count FROM health_checks WHERE checked_at >= datetime("now", "-5 minutes") GROUP BY status')
    health = {row[0]: row[1] for row in cursor.fetchall()}

    conn.close()

    return {
        'services': services,
        'active_incidents': incidents,
        'recent_alerts': recent_alerts,
        'health': health
    }

if __name__ == '__main__':
    init_db()
