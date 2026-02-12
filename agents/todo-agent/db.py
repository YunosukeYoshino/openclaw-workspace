#!/usr/bin/env python3
"""
ToDoエージェント #5
- タスク管理
- 優先順位・期限・完了
"""

import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / "todos.db"

def init_db():
    """データベース初期化"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # タスクテーブル
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS todos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT,
        priority INTEGER CHECK(priority IN (1,2,3)),
        due_date DATE,
        status TEXT DEFAULT 'pending' CHECK(status IN ('pending', 'completed', 'cancelled')),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        completed_at TIMESTAMP
    )
    ''')

    # 更新トリガー
    cursor.execute('''
    CREATE TRIGGER IF NOT EXISTS update_todos_completed_at
    AFTER UPDATE OF status ON todos
    WHEN NEW.status = 'completed' AND OLD.status != 'completed'
    BEGIN
        UPDATE todos SET completed_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
    END
    ''')

    # インデックス
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_todos_status ON todos(status)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_todos_priority ON todos(priority)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_todos_due ON todos(due_date)')

    conn.commit()
    conn.close()
    print("✅ データベース初期化完了")

def add_todo(title, description=None, priority=None, due_date=None):
    """タスク追加"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO todos (title, description, priority, due_date)
    VALUES (?, ?, ?, ?)
    ''', (title, description, priority, due_date))

    todo_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return todo_id

def complete_todo(todo_id):
    """タスク完了"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    UPDATE todos SET status = 'completed' WHERE id = ?
    ''', (todo_id,))

    conn.commit()
    conn.close()

def list_todos(status=None, limit=20):
    """タスク一覧"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    query = '''
    SELECT id, title, description, priority, due_date, status, created_at
    FROM todos
    '''

    params = []
    if status:
        query += ' WHERE status = ?'
        params.append(status)

    query += ' ORDER BY priority DESC, due_date ASC, created_at DESC LIMIT ?'
    params.append(limit)

    cursor.execute(query, params)
    todos = cursor.fetchall()
    conn.close()
    return todos

def search_todos(keyword):
    """タスク検索"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT id, title, description, priority, due_date, status, created_at
    FROM todos
    WHERE title LIKE ? OR description LIKE ?
    ORDER BY priority DESC, due_date ASC, created_at DESC
    ''', (f'%{keyword}%', f'%{keyword}%'))

    todos = cursor.fetchall()
    conn.close()
    return todos

def get_stats():
    """統計情報"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    stats = {}

    # 全タスク数
    cursor.execute('SELECT COUNT(*) FROM todos WHERE status != "cancelled"')
    stats['total'] = cursor.fetchone()[0]

    # 未完了
    cursor.execute('SELECT COUNT(*) FROM todos WHERE status = "pending"')
    stats['pending'] = cursor.fetchone()[0]

    # 完了
    cursor.execute('SELECT COUNT(*) FROM todos WHERE status = "completed"')
    stats['completed'] = cursor.fetchone()[0]

    # 期限切れ
    cursor.execute('''
    SELECT COUNT(*) FROM todos
    WHERE status = "pending" AND due_date < date('now')
    ''')
    stats['overdue'] = cursor.fetchone()[0]

    conn.close()
    return stats

if __name__ == '__main__':
    init_db()
