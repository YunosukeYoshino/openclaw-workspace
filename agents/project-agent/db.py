#!/usr/bin/env python3
"""
プロジェクト管理エージェント #12
- プロジェクトとタスクの管理
- 進捗追跡
"""

import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / "projects.db"

def init_db():
    """データベース初期化"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # プロジェクトテーブル
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS projects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        status TEXT DEFAULT 'active' CHECK(status IN ('active', 'completed', 'paused', 'cancelled')),
        progress INTEGER DEFAULT 0 CHECK(progress >= 0 AND progress <= 100),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        completed_at TIMESTAMP
    )
    ''')

    # タスクテーブル
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        status TEXT DEFAULT 'pending' CHECK(status IN ('pending', 'in_progress', 'completed', 'cancelled')),
        priority INTEGER DEFAULT 2 CHECK(priority IN (1,2,3)),
        due_date DATE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        completed_at TIMESTAMP,
        FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
    )
    ''')

    # インデックス
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_projects_status ON projects(status)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_projects_created ON projects(created_at)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_tasks_project ON tasks(project_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status)')

    conn.commit()
    conn.close()
    print("✅ データベース初期化完了")

def add_project(name, description=None):
    """プロジェクト追加"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO projects (name, description)
    VALUES (?, ?)
    ''', (name, description))

    project_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return project_id

def add_task(project_id, title, priority=2, due_date=None):
    """タスク追加"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO tasks (project_id, title, priority, due_date)
    VALUES (?, ?, ?, ?)
    ''', (project_id, title, priority, due_date))

    task_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return task_id

def update_project_status(project_id, status):
    """プロジェクトステータス更新"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    updates = ['status = ?']
    params = [status]

    if status == 'completed':
        updates.append('completed_at = ?')
        params.append(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    params.append(project_id)

    cursor.execute(f'UPDATE projects SET {", ".join(updates)} WHERE id = ?', params)
    conn.commit()
    conn.close()

def update_task_status(task_id, status):
    """タスクステータス更新"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    updates = ['status = ?']
    params = [status]

    if status == 'completed':
        updates.append('completed_at = ?')
        params.append(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    params.append(task_id)

    cursor.execute(f'UPDATE tasks SET {", ".join(updates)} WHERE id = ?', params)
    conn.commit()
    conn.close()

def list_projects():
    """プロジェクト一覧"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT id, name, description, status, progress, created_at
    FROM projects
    WHERE status IN ('active', 'paused')
    ORDER BY created_at DESC
    ''')

    projects = cursor.fetchall()
    conn.close()
    return projects

def get_project_tasks(project_id):
    """プロジェクトのタスク取得"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT id, title, status, priority, due_date, created_at
    FROM tasks
    WHERE project_id = ? AND status != 'cancelled'
    ORDER BY priority DESC, created_at ASC
    ''', (project_id,))

    tasks = cursor.fetchall()
    conn.close()
    return tasks

if __name__ == '__main__':
    init_db()
