#!/usr/bin/env python3
"""
メモエージェント #2
- メモの保存・検索・管理
- カテゴリ・タグ機能
"""

import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / "memos.db"

def init_db():
    """データベース初期化"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # メモテーブル
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS memos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        content TEXT NOT NULL,
        category_id INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (category_id) REFERENCES categories(id)
    )
    ''')

    # カテゴリテーブル
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # タグテーブル
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tags (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # メモ・タグ紐付け
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS memo_tags (
        memo_id INTEGER NOT NULL,
        tag_id INTEGER NOT NULL,
        PRIMARY KEY (memo_id, tag_id),
        FOREIGN KEY (memo_id) REFERENCES memos(id) ON DELETE CASCADE,
        FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
    )
    ''')

    # 更新トリガー
    cursor.execute('''
    CREATE TRIGGER IF NOT EXISTS update_memos_timestamp
    AFTER UPDATE ON memos
    BEGIN
        UPDATE memos SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
    END
    ''')

    # インデックス
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_memos_category ON memos(category_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_memos_created ON memos(created_at)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_memo_tags_tag ON memo_tags(tag_id)')

    conn.commit()
    conn.close()
    print("✅ データベース初期化完了")

def add_memo(title, content, category=None, tags=None):
    """メモ追加"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # カテゴリID取得/作成
    category_id = None
    if category:
        cursor.execute('INSERT OR IGNORE INTO categories (name) VALUES (?)', (category,))
        cursor.execute('SELECT id FROM categories WHERE name = ?', (category,))
        category_id = cursor.fetchone()[0]

    # メモ追加
    cursor.execute('''
    INSERT INTO memos (title, content, category_id)
    VALUES (?, ?, ?)
    ''', (title, content, category_id))

    memo_id = cursor.lastrowid

    # タグ紐付け
    if tags:
        for tag in tags:
            cursor.execute('INSERT OR IGNORE INTO tags (name) VALUES (?)', (tag,))
            cursor.execute('SELECT id FROM tags WHERE name = ?', (tag,))
            tag_id = cursor.fetchone()[0]
            cursor.execute('INSERT OR IGNORE INTO memo_tags (memo_id, tag_id) VALUES (?, ?)', (memo_id, tag_id))

    conn.commit()
    conn.close()
    return memo_id

def list_memos(limit=20):
    """メモ一覧"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT m.id, m.title, substr(m.content, 1, 50), c.name, m.created_at
    FROM memos m
    LEFT JOIN categories c ON m.category_id = c.id
    ORDER BY m.created_at DESC
    LIMIT ?
    ''', (limit,))

    memos = cursor.fetchall()
    conn.close()
    return memos

def search_memos(keyword):
    """メモ検索"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT m.id, m.title, substr(m.content, 1, 50), c.name, m.created_at
    FROM memos m
    LEFT JOIN categories c ON m.category_id = c.id
    WHERE m.title LIKE ? OR m.content LIKE ?
    ORDER BY m.created_at DESC
    ''', (f'%{keyword}%', f'%{keyword}%'))

    memos = cursor.fetchall()
    conn.close()
    return memos

def get_categories():
    """カテゴリ一覧"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM categories ORDER BY name')
    categories = cursor.fetchall()
    conn.close()
    return categories

def get_tags():
    """タグ一覧"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM tags ORDER BY name')
    tags = cursor.fetchall()
    conn.close()
    return tags

def delete_memo(memo_id):
    """メモ削除"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM memos WHERE id = ?', (memo_id,))
    conn.commit()
    conn.close()

def update_memo(memo_id, title=None, content=None, category=None):
    """メモ更新"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    updates = []
    params = []

    if title is not None:
        updates.append('title = ?')
        params.append(title)
    if content is not None:
        updates.append('content = ?')
        params.append(content)
    if category is not None:
        # カテゴリID取得/作成
        cursor.execute('INSERT OR IGNORE INTO categories (name) VALUES (?)', (category,))
        cursor.execute('SELECT id FROM categories WHERE name = ?', (category,))
        category_id = cursor.fetchone()[0]
        updates.append('category_id = ?')
        params.append(category_id)

    if updates:
        params.append(memo_id)
        cursor.execute(f'UPDATE memos SET {", ".join(updates)} WHERE id = ?', params)
        conn.commit()

    conn.close()

def export_json():
    """JSONエクスポート"""
    import json
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    memos = []
    cursor.execute('''
    SELECT m.id, m.title, m.content, c.name as category, m.created_at, m.updated_at,
           GROUP_CONCAT(t.name) as tags
    FROM memos m
    LEFT JOIN categories c ON m.category_id = c.id
    LEFT JOIN memo_tags mt ON m.id = mt.memo_id
    LEFT JOIN tags t ON mt.tag_id = t.id
    GROUP BY m.id
    ORDER BY m.created_at DESC
    ''')

    for row in cursor.fetchall():
        memo = dict(row)
        memo['tags'] = memo['tags'].split(',') if memo['tags'] else []
        memos.append(memo)

    conn.close()
    return json.dumps(memos, ensure_ascii=False, indent=2)

def get_stats():
    """統計情報"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    stats = {}

    # 全メモ数
    cursor.execute('SELECT COUNT(*) FROM memos')
    stats['total_memos'] = cursor.fetchone()[0]

    # カテゴリ別
    cursor.execute('''
    SELECT c.name, COUNT(m.id) as count
    FROM categories c
    LEFT JOIN memos m ON c.id = m.category_id
    GROUP BY c.id
    ORDER BY count DESC
    ''')
    stats['by_category'] = dict(cursor.fetchall())

    # タグ別
    cursor.execute('''
    SELECT t.name, COUNT(mt.memo_id) as count
    FROM tags t
    LEFT JOIN memo_tags mt ON t.id = mt.tag_id
    GROUP BY t.id
    ORDER BY count DESC
    ''')
    stats['by_tag'] = dict(cursor.fetchall())

    conn.close()
    return stats

if __name__ == '__main__':
    init_db()
