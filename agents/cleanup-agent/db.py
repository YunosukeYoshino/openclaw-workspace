#!/usr/bin/env python3
"""
Cleanup Agent - クリーンアップ管理 (Scheduled Cleanups)
"""

import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / "cleanup.db"

def init_db():
    """データベース初期化"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # クリーンアップタスクテーブル
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS cleanup_tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        target_path TEXT,
        cleanup_type TEXT CHECK(cleanup_type IN ('files', 'folders', 'temp', 'logs', 'cache', 'custom')),
        retention_days INTEGER,
        pattern TEXT,
        schedule TEXT,
        enabled INTEGER DEFAULT 1,
        last_run_at TIMESTAMP,
        next_run_at TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # 実行履歴テーブル
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS cleanup_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        task_id INTEGER,
        run_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        status TEXT CHECK(status IN ('success', 'partial', 'failed')),
        items_processed INTEGER DEFAULT 0,
        items_deleted INTEGER DEFAULT 0,
        space_freed INTEGER DEFAULT 0,
        duration_seconds INTEGER DEFAULT 0,
        error_message TEXT,
        FOREIGN KEY (task_id) REFERENCES cleanup_tasks(id)
    )
    ''')

    # 除外ルールテーブル
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS exclusion_rules (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        task_id INTEGER,
        pattern TEXT NOT NULL,
        rule_type TEXT CHECK(rule_type IN ('glob', 'regex', 'path')),
        description TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (task_id) REFERENCES cleanup_tasks(id)
    )
    ''')

    # 更新トリガー
    cursor.execute('''
    CREATE TRIGGER IF NOT EXISTS update_cleanup_tasks_updated_at
    AFTER UPDATE ON cleanup_tasks
    BEGIN
        UPDATE cleanup_tasks SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
    END
    ''')

    # インデックス
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_cleanup_tasks_enabled ON cleanup_tasks(enabled)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_cleanup_tasks_schedule ON cleanup_tasks(schedule)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_cleanup_tasks_next_run ON cleanup_tasks(next_run_at)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_cleanup_history_task_id ON cleanup_history(task_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_cleanup_history_run_at ON cleanup_history(run_at)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_exclusion_rules_task_id ON exclusion_rules(task_id)')

    conn.commit()
    conn.close()
    print("✅ データベース初期化完了")

def add_cleanup_task(name, description=None, target_path=None, cleanup_type='files',
                     retention_days=None, pattern=None, schedule=None):
    """クリーンアップタスク追加"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO cleanup_tasks (name, description, target_path, cleanup_type, retention_days, pattern, schedule)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (name, description, target_path, cleanup_type, retention_days, pattern, schedule))

    task_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return task_id

def get_cleanup_task(task_id):
    """クリーンアップタスク取得"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT id, name, description, target_path, cleanup_type, retention_days, pattern,
           schedule, enabled, last_run_at, next_run_at, created_at, updated_at
    FROM cleanup_tasks WHERE id = ?
    ''', (task_id,))

    task = cursor.fetchone()
    conn.close()
    return task

def list_cleanup_tasks(enabled_only=False):
    """クリーンアップタスク一覧"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    query = '''
    SELECT id, name, description, cleanup_type, schedule, enabled, last_run_at, next_run_at
    FROM cleanup_tasks
    '''

    if enabled_only:
        query += ' WHERE enabled = 1'

    query += ' ORDER BY created_at DESC'

    cursor.execute(query)
    tasks = cursor.fetchall()
    conn.close()
    return tasks

def update_cleanup_task(task_id, **kwargs):
    """クリーンアップタスク更新"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    allowed_fields = ['name', 'description', 'target_path', 'cleanup_type',
                      'retention_days', 'pattern', 'schedule', 'enabled']

    set_clause = []
    params = []

    for field, value in kwargs.items():
        if field in allowed_fields:
            set_clause.append(f"{field} = ?")
            params.append(value)

    if not set_clause:
        conn.close()
        return False

    params.append(task_id)
    query = f"UPDATE cleanup_tasks SET {', '.join(set_clause)} WHERE id = ?"
    cursor.execute(query, params)

    conn.commit()
    conn.close()
    return True

def delete_cleanup_task(task_id):
    """クリーンアップタスク削除"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('DELETE FROM cleanup_tasks WHERE id = ?', (task_id,))
    cursor.execute('DELETE FROM cleanup_history WHERE task_id = ?', (task_id,))
    cursor.execute('DELETE FROM exclusion_rules WHERE task_id = ?', (task_id,))

    conn.commit()
    conn.close()

def toggle_cleanup_task(task_id):
    """クリーンアップタスク有効/無効切り替え"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    UPDATE cleanup_tasks SET enabled = NOT enabled WHERE id = ?
    ''', (task_id,))

    conn.commit()
    conn.close()

def record_cleanup_history(task_id, status, items_processed=0, items_deleted=0,
                           space_freed=0, duration_seconds=0, error_message=None):
    """実行履歴記録"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO cleanup_history
    (task_id, status, items_processed, items_deleted, space_freed, duration_seconds, error_message)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (task_id, status, items_processed, items_deleted, space_freed, duration_seconds, error_message))

    history_id = cursor.lastrowid

    # last_run_at更新
    cursor.execute('''
    UPDATE cleanup_tasks SET last_run_at = CURRENT_TIMESTAMP WHERE id = ?
    ''', (task_id,))

    conn.commit()
    conn.close()
    return history_id

def get_cleanup_history(task_id=None, limit=20):
    """実行履歴取得"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    if task_id:
        cursor.execute('''
        SELECT h.id, h.task_id, t.name, h.run_at, h.status, h.items_processed,
               h.items_deleted, h.space_freed, h.duration_seconds, h.error_message
        FROM cleanup_history h
        JOIN cleanup_tasks t ON h.task_id = t.id
        WHERE h.task_id = ?
        ORDER BY h.run_at DESC
        LIMIT ?
        ''', (task_id, limit))
    else:
        cursor.execute('''
        SELECT h.id, h.task_id, t.name, h.run_at, h.status, h.items_processed,
               h.items_deleted, h.space_freed, h.duration_seconds, h.error_message
        FROM cleanup_history h
        JOIN cleanup_tasks t ON h.task_id = t.id
        ORDER BY h.run_at DESC
        LIMIT ?
        ''', (limit,))

    history = cursor.fetchall()
    conn.close()
    return history

def add_exclusion_rule(task_id, pattern, rule_type='glob', description=None):
    """除外ルール追加"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO exclusion_rules (task_id, pattern, rule_type, description)
    VALUES (?, ?, ?, ?)
    ''', (task_id, pattern, rule_type, description))

    rule_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return rule_id

def list_exclusion_rules(task_id):
    """除外ルール一覧"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT id, pattern, rule_type, description, created_at
    FROM exclusion_rules
    WHERE task_id = ?
    ORDER BY created_at ASC
    ''', (task_id,))

    rules = cursor.fetchall()
    conn.close()
    return rules

def delete_exclusion_rule(rule_id):
    """除外ルール削除"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('DELETE FROM exclusion_rules WHERE id = ?', (rule_id,))

    conn.commit()
    conn.close()

def get_cleanup_stats():
    """統計情報"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    stats = {}

    # タスク数
    cursor.execute('SELECT COUNT(*) FROM cleanup_tasks')
    stats['total_tasks'] = cursor.fetchone()[0]

    # 有効タスク数
    cursor.execute('SELECT COUNT(*) FROM cleanup_tasks WHERE enabled = 1')
    stats['enabled_tasks'] = cursor.fetchone()[0]

    # 実行回数
    cursor.execute('SELECT COUNT(*) FROM cleanup_history')
    stats['total_runs'] = cursor.fetchone()[0]

    # 成功/失敗
    cursor.execute('SELECT COUNT(*) FROM cleanup_history WHERE status = "success"')
    stats['success_runs'] = cursor.fetchone()[0]

    cursor.execute('SELECT COUNT(*) FROM cleanup_history WHERE status = "failed"')
    stats['failed_runs'] = cursor.fetchone()[0]

    # 削除アイテム数
    cursor.execute('SELECT SUM(items_deleted) FROM cleanup_history')
    result = cursor.fetchone()[0]
    stats['total_items_deleted'] = result if result else 0

    # 解放スペース
    cursor.execute('SELECT SUM(space_freed) FROM cleanup_history')
    result = cursor.fetchone()[0]
    stats['total_space_freed'] = result if result else 0

    # 最新実行
    cursor.execute('''
    SELECT MAX(run_at) FROM cleanup_history WHERE status = "success"
    ''')
    stats['last_successful_run'] = cursor.fetchone()[0]

    conn.close()
    return stats

if __name__ == '__main__':
    init_db()
