#!/usr/bin/env python3
"""
Deploy Agent - Database Management
Deployments and rollbacks management
"""

import sqlite3
from pathlib import Path
from datetime import datetime
import json

DB_PATH = Path(__file__).parent / "deploy.db"

def init_db():
    """Initialize database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Environments table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS environments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        type TEXT CHECK(type IN ('development','staging','production','qa')),
        description TEXT,
        url TEXT,
        branch TEXT,
        config TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Deployments table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS deployments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        environment_id INTEGER NOT NULL,
        version TEXT NOT NULL,
        build_number TEXT,
        git_branch TEXT,
        git_commit TEXT,
        git_tag TEXT,
        status TEXT DEFAULT 'pending' CHECK(status IN ('pending','in_progress','success','failed','rolled_back')),
        triggered_by TEXT,
        started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        completed_at TIMESTAMP,
        duration_seconds INTEGER,
        deployed_by TEXT,
        rollback_id INTEGER,
        notes TEXT,
        metadata TEXT,
        FOREIGN KEY (environment_id) REFERENCES environments(id),
        FOREIGN KEY (rollback_id) REFERENCES deployments(id)
    )
    ''')

    # Deployment steps table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS deployment_steps (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        deployment_id INTEGER NOT NULL,
        step_name TEXT NOT NULL,
        step_type TEXT CHECK(step_type IN ('build','test','deploy','verify','rollback')),
        status TEXT DEFAULT 'pending' CHECK(status IN ('pending','in_progress','success','failed','skipped')),
        started_at TIMESTAMP,
        completed_at TIMESTAMP,
        duration_seconds INTEGER,
        output TEXT,
        error_message TEXT,
        log_path TEXT,
        order_index INTEGER NOT NULL,
        FOREIGN KEY (deployment_id) REFERENCES deployments(id)
    )
    ''')

    # Rollbacks table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS rollbacks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        deployment_id INTEGER NOT NULL,
        original_deployment_id INTEGER NOT NULL,
        reason TEXT,
        triggered_by TEXT,
        started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        completed_at TIMESTAMP,
        status TEXT DEFAULT 'pending' CHECK(status IN ('pending','in_progress','success','failed')),
        notes TEXT,
        FOREIGN KEY (deployment_id) REFERENCES deployments(id),
        FOREIGN KEY (original_deployment_id) REFERENCES deployments(id)
    )
    ''')

    # Deployment artifacts table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS artifacts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        deployment_id INTEGER NOT NULL,
        artifact_name TEXT NOT NULL,
        artifact_type TEXT CHECK(artifact_type IN ('docker_image','zip','tar','jar','war','other')),
        artifact_path TEXT,
        size_bytes INTEGER,
        checksum TEXT,
        storage_location TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (deployment_id) REFERENCES deployments(id)
    )
    ''')

    # Deployment configuration table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS configs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        deployment_id INTEGER NOT NULL,
        config_key TEXT NOT NULL,
        config_value TEXT,
        config_type TEXT DEFAULT 'env_var' CHECK(config_type IN ('env_var','secret','config_file','database')),
        is_sensitive BOOLEAN DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (deployment_id) REFERENCES deployments(id)
    )
    ''')

    # Deployment health checks table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS health_checks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        deployment_id INTEGER NOT NULL,
        check_name TEXT NOT NULL,
        check_type TEXT CHECK(check_type IN ('http','tcp','database','custom')),
        endpoint TEXT,
        expected_status INTEGER,
        actual_status INTEGER,
        response_time_ms INTEGER,
        status TEXT DEFAULT 'pending' CHECK(status IN ('pending','pass','fail')),
        checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        notes TEXT,
        FOREIGN KEY (deployment_id) REFERENCES deployments(id)
    )
    ''')

    # Deployment notifications table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS notifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        deployment_id INTEGER NOT NULL,
        notification_type TEXT CHECK(notification_type IN ('slack','email','discord','webhook')),
        recipient TEXT NOT NULL,
        message TEXT,
        sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        status TEXT DEFAULT 'sent' CHECK(status IN ('pending','sent','failed')),
        FOREIGN KEY (deployment_id) REFERENCES deployments(id)
    )
    ''')

    # Indexes
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_deployments_env ON deployments(environment_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_deployments_status ON deployments(status)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_deployments_started ON deployments(started_at)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_deployment_steps_deployment ON deployment_steps(deployment_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_rollbacks_deployment ON rollbacks(deployment_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_artifacts_deployment ON artifacts(deployment_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_health_checks_deployment ON health_checks(deployment_id)')

    conn.commit()
    conn.close()
    print("✅ Database initialized")

def create_environment(name, env_type, description=None, url=None, branch=None, config=None):
    """Create a deployment environment"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    config_json = json.dumps(config) if config else None
    cursor.execute('''
    INSERT INTO environments (name, type, description, url, branch, config)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', (name, env_type, description, url, branch, config_json))

    conn.commit()
    env_id = cursor.lastrowid
    conn.close()
    return env_id

def get_environments(env_type=None, limit=20):
    """Get environments"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    if env_type:
        cursor.execute('SELECT * FROM environments WHERE type = ? ORDER BY name LIMIT ?', (env_type, limit))
    else:
        cursor.execute('SELECT * FROM environments ORDER BY name LIMIT ?', (limit,))

    envs = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return envs

def start_deployment(environment_id, version, triggered_by, build_number=None, git_branch=None,
                     git_commit=None, git_tag=None, notes=None):
    """Start a deployment"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    metadata_json = json.dumps({
        'build_number': build_number,
        'git_branch': git_branch,
        'git_commit': git_commit,
        'git_tag': git_tag
    })

    cursor.execute('''
    INSERT INTO deployments (environment_id, version, build_number, git_branch, git_commit, git_tag, triggered_by, notes, metadata)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (environment_id, version, build_number, git_branch, git_commit, git_tag, triggered_by, notes, metadata_json))

    conn.commit()
    deployment_id = cursor.lastrowid
    conn.close()
    return deployment_id

def complete_deployment(deployment_id, status, deployed_by=None, notes=None):
    """Complete a deployment"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Calculate duration
    cursor.execute('''
    UPDATE deployments
    SET status = ?,
        completed_at = CURRENT_TIMESTAMP,
        duration_seconds = CAST((julianday(CURRENT_TIMESTAMP) - julianday(started_at)) * 24 * 60 * 60 AS INTEGER),
        deployed_by = COALESCE(?, deployed_by),
        notes = COALESCE(?, notes)
    WHERE id = ?
    ''', (status, deployed_by, notes, deployment_id))

    conn.commit()
    conn.close()

def get_deployments(environment_id=None, status=None, limit=20):
    """Get deployments"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    query = 'SELECT * FROM deployments WHERE 1=1'
    params = []

    if environment_id:
        query += ' AND environment_id = ?'
        params.append(environment_id)
    if status:
        query += ' AND status = ?'
        params.append(status)

    query += ' ORDER BY started_at DESC LIMIT ?'
    params.append(limit)

    cursor.execute(query, params)
    deployments = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return deployments

def add_deployment_step(deployment_id, step_name, step_type, order_index):
    """Add a deployment step"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO deployment_steps (deployment_id, step_name, step_type, order_index)
    VALUES (?, ?, ?, ?)
    ''', (deployment_id, step_name, step_type, order_index))

    conn.commit()
    step_id = cursor.lastrowid
    conn.close()
    return step_id

def update_deployment_step(step_id, status, started_at=None, completed_at=None, output=None, error_message=None):
    """Update a deployment step"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    if completed_at and started_at:
        # Calculate duration
        cursor.execute('''
        UPDATE deployment_steps
        SET status = ?,
            started_at = COALESCE(?, started_at),
            completed_at = ?,
            duration_seconds = CAST((julianday(?) - julianday(COALESCE(?, started_at))) * 24 * 60 * 60 AS INTEGER),
            output = ?,
            error_message = ?
        WHERE id = ?
        ''', (status, started_at, completed_at, completed_at, started_at, output, error_message, step_id))
    else:
        cursor.execute('''
        UPDATE deployment_steps
        SET status = ?, output = ?, error_message = ?
        WHERE id = ?
        ''', (status, output, error_message, step_id))

    conn.commit()
    conn.close()

def get_deployment_steps(deployment_id):
    """Get deployment steps"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM deployment_steps WHERE deployment_id = ? ORDER BY order_index', (deployment_id,))
    steps = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return steps

def start_rollback(deployment_id, original_deployment_id, triggered_by, reason=None):
    """Start a rollback"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO rollbacks (deployment_id, original_deployment_id, triggered_by, reason)
    VALUES (?, ?, ?, ?)
    ''', (deployment_id, original_deployment_id, triggered_by, reason))

    conn.commit()
    rollback_id = cursor.lastrowid

    # Mark original deployment as rolled back
    cursor.execute('UPDATE deployments SET status = "rolled_back", rollback_id = ? WHERE id = ?', (deployment_id, rollback_id))

    conn.commit()
    conn.close()
    return rollback_id

def complete_rollback(rollback_id, status, notes=None):
    """Complete a rollback"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    UPDATE rollbacks
    SET status = ?, completed_at = CURRENT_TIMESTAMP, notes = ?
    WHERE id = ?
    ''', (status, notes, rollback_id))

    conn.commit()
    conn.close()

def get_rollbacks(deployment_id=None, status=None, limit=20):
    """Get rollbacks"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    query = 'SELECT * FROM rollbacks WHERE 1=1'
    params = []

    if deployment_id:
        query += ' AND deployment_id = ?'
        params.append(deployment_id)
    if status:
        query += ' AND status = ?'
        params.append(status)

    query += ' ORDER BY started_at DESC LIMIT ?'
    params.append(limit)

    cursor.execute(query, params)
    rollbacks = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rollbacks

def add_artifact(deployment_id, artifact_name, artifact_type, artifact_path=None, size_bytes=None, checksum=None, storage_location=None):
    """Add a deployment artifact"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO artifacts (deployment_id, artifact_name, artifact_type, artifact_path, size_bytes, checksum, storage_location)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (deployment_id, artifact_name, artifact_type, artifact_path, size_bytes, checksum, storage_location))

    conn.commit()
    conn.close()

def get_artifacts(deployment_id=None, limit=50):
    """Get deployment artifacts"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    if deployment_id:
        cursor.execute('SELECT * FROM artifacts WHERE deployment_id = ? ORDER BY id LIMIT ?', (deployment_id, limit))
    else:
        cursor.execute('SELECT * FROM artifacts ORDER BY id DESC LIMIT ?', (limit,))

    artifacts = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return artifacts

def add_config(deployment_id, config_key, config_value, config_type='env_var', is_sensitive=False):
    """Add a deployment configuration"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO configs (deployment_id, config_key, config_value, config_type, is_sensitive)
    VALUES (?, ?, ?, ?, ?)
    ''', (deployment_id, config_key, config_value, config_type, is_sensitive))

    conn.commit()
    conn.close()

def get_configs(deployment_id):
    """Get deployment configurations"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM configs WHERE deployment_id = ?', (deployment_id,))
    configs = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return configs

def add_health_check(deployment_id, check_name, check_type, endpoint=None, expected_status=200):
    """Add a health check"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO health_checks (deployment_id, check_name, check_type, endpoint, expected_status)
    VALUES (?, ?, ?, ?, ?)
    ''', (deployment_id, check_name, check_type, endpoint, expected_status))

    conn.commit()
    check_id = cursor.lastrowid
    conn.close()
    return check_id

def update_health_check(check_id, actual_status, response_time_ms, status, notes=None):
    """Update a health check result"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    UPDATE health_checks
    SET actual_status = ?, response_time_ms = ?, status = ?, notes = ?, checked_at = CURRENT_TIMESTAMP
    WHERE id = ?
    ''', (actual_status, response_time_ms, status, notes, check_id))

    conn.commit()
    conn.close()

def get_health_checks(deployment_id, status=None):
    """Get health checks"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    if status:
        cursor.execute('SELECT * FROM health_checks WHERE deployment_id = ? AND status = ? ORDER BY id', (deployment_id, status))
    else:
        cursor.execute('SELECT * FROM health_checks WHERE deployment_id = ? ORDER BY id', (deployment_id,))

    checks = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return checks

def add_notification(deployment_id, notification_type, recipient, message):
    """Add a deployment notification"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO notifications (deployment_id, notification_type, recipient, message)
    VALUES (?, ?, ?, ?)
    ''', (deployment_id, notification_type, recipient, message))

    conn.commit()
    conn.close()

def get_notifications(deployment_id=None, limit=50):
    """Get notifications"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    if deployment_id:
        cursor.execute('SELECT * FROM notifications WHERE deployment_id = ? ORDER BY sent_at DESC LIMIT ?', (deployment_id, limit))
    else:
        cursor.execute('SELECT * FROM notifications ORDER BY sent_at DESC LIMIT ?', (limit,))

    notifications = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return notifications

def get_deployment_stats(days=30):
    """Get deployment statistics"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute('''
    SELECT
        COUNT(*) as total,
        SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as successful,
        SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed,
        SUM(CASE WHEN status = 'rolled_back' THEN 1 ELSE 0 END) as rolled_back,
        AVG(CASE WHEN completed_at IS NOT NULL THEN duration_seconds ELSE NULL END) as avg_duration_seconds
    FROM deployments
    WHERE started_at >= datetime('now', ?)
    ''', (f'-{days} days',))

    stats = cursor.fetchone()
    conn.close()
    return dict(stats) if stats else None

if __name__ == '__main__':
    init_db()
