#!/usr/bin/env python3
"""
ブックマーク管理エージェント
- ブックマークの保存・整理
- タグ付け・検索
- ブックマークの共有
"""

import sqlite3
from pathlib import Path
from datetime import datetime
import hashlib

DB_PATH = Path(__file__).parent / "bookmarks.db"

def init_db():
    """データベース初期化"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # ブックマークテーブル
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS bookmarks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        url TEXT NOT NULL,
        title TEXT,
        description TEXT,
        favicon TEXT,
        category_id INTEGER,
        shared_key TEXT UNIQUE,
        view_count INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL
    )
    ''')

    # カテゴリテーブル
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        color TEXT DEFAULT '#888888',
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

    # ブックマーク・タグ紐付け
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS bookmark_tags (
        bookmark_id INTEGER NOT NULL,
        tag_id INTEGER NOT NULL,
        PRIMARY KEY (bookmark_id, tag_id),
        FOREIGN KEY (bookmark_id) REFERENCES bookmarks(id) ON DELETE CASCADE,
        FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
    )
    ''')

    # 更新トリガー
    cursor.execute('''
    CREATE TRIGGER IF NOT EXISTS update_bookmarks_timestamp
    AFTER UPDATE ON bookmarks
    BEGIN
        UPDATE bookmarks SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
    END
    ''')

    # インデックス
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_bookmarks_url ON bookmarks(url)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_bookmarks_category ON bookmarks(category_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_bookmarks_created ON bookmarks(created_at)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_bookmark_tags_tag ON bookmark_tags(tag_id)')

    # デフォルトカテゴリ
    default_categories = [
        ('Work', '#3498db'),
        ('仕事', '#3498db'),
        ('Personal', '#2ecc71'),
        ('個人', '#2ecc71'),
        ('Reference', '#f39c12'),
        ('参考', '#f39c12'),
        ('Entertainment', '#9b59b6'),
        ('エンタメ', '#9b59b6'),
    ]
    for name, color in default_categories:
        cursor.execute('INSERT OR IGNORE INTO categories (name, color) VALUES (?, ?)', (name, color))

    conn.commit()
    conn.close()
    print("✅ ブックマークデータベース初期化完了")

def add_bookmark(url, title=None, description=None, category=None, tags=None):
    """ブックマーク追加"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # カテゴリID取得/作成
    category_id = None
    if category:
        cursor.execute('INSERT OR IGNORE INTO categories (name) VALUES (?)', (category,))
        cursor.execute('SELECT id FROM categories WHERE name = ?', (category,))
        category_id = cursor.fetchone()[0]

    # ブックマーク追加
    cursor.execute('''
    INSERT INTO bookmarks (url, title, description, category_id)
    VALUES (?, ?, ?, ?)
    ''', (url, title, description, category_id))

    bookmark_id = cursor.lastrowid

    # タグ紐付け
    if tags:
        for tag in tags:
            cursor.execute('INSERT OR IGNORE INTO tags (name) VALUES (?)', (tag,))
            cursor.execute('SELECT id FROM tags WHERE name = ?', (tag,))
            tag_id = cursor.fetchone()[0]
            cursor.execute('INSERT OR IGNORE INTO bookmark_tags (bookmark_id, tag_id) VALUES (?, ?)',
                          (bookmark_id, tag_id))

    conn.commit()
    conn.close()
    return bookmark_id

def list_bookmarks(limit=50, category=None):
    """ブックマーク一覧"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    if category:
        cursor.execute('''
        SELECT b.id, b.url, b.title, b.description, c.name, b.view_count, b.created_at
        FROM bookmarks b
        LEFT JOIN categories c ON b.category_id = c.id
        WHERE c.name = ?
        ORDER BY b.created_at DESC
        LIMIT ?
        ''', (category, limit))
    else:
        cursor.execute('''
        SELECT b.id, b.url, b.title, b.description, c.name, b.view_count, b.created_at
        FROM bookmarks b
        LEFT JOIN categories c ON b.category_id = c.id
        ORDER BY b.created_at DESC
        LIMIT ?
        ''', (limit,))

    bookmarks = cursor.fetchall()
    conn.close()
    return bookmarks

def search_bookmarks(keyword):
    """ブックマーク検索"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT b.id, b.url, b.title, b.description, c.name, b.view_count, b.created_at
    FROM bookmarks b
    LEFT JOIN categories c ON b.category_id = c.id
    WHERE b.url LIKE ? OR b.title LIKE ? OR b.description LIKE ?
    ORDER BY b.created_at DESC
    ''', (f'%{keyword}%', f'%{keyword}%', f'%{keyword}%'))

    bookmarks = cursor.fetchall()
    conn.close()
    return bookmarks

def search_by_tag(tag_name):
    """タグで検索"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT b.id, b.url, b.title, b.description, c.name, b.view_count, b.created_at
    FROM bookmarks b
    LEFT JOIN categories c ON b.category_id = c.id
    JOIN bookmark_tags bt ON b.id = bt.bookmark_id
    JOIN tags t ON bt.tag_id = t.id
    WHERE t.name = ?
    ORDER BY b.created_at DESC
    ''', (tag_name,))

    bookmarks = cursor.fetchall()
    conn.close()
    return bookmarks

def get_bookmark(bookmark_id):
    """ブックマーク取得（閲覧カウント増）"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM bookmarks WHERE id = ?', (bookmark_id,))
    bookmark = cursor.fetchone()

    if bookmark:
        cursor.execute('UPDATE bookmarks SET view_count = view_count + 1 WHERE id = ?', (bookmark_id,))
        conn.commit()

    conn.close()
    return bookmark

def delete_bookmark(bookmark_id):
    """ブックマーク削除"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM bookmarks WHERE id = ?', (bookmark_id,))
    conn.commit()
    conn.close()

def update_bookmark(bookmark_id, url=None, title=None, description=None, category=None):
    """ブックマーク更新"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    updates = []
    params = []

    if url is not None:
        updates.append('url = ?')
        params.append(url)
    if title is not None:
        updates.append('title = ?')
        params.append(title)
    if description is not None:
        updates.append('description = ?')
        params.append(description)
    if category is not None:
        cursor.execute('INSERT OR IGNORE INTO categories (name) VALUES (?)', (category,))
        cursor.execute('SELECT id FROM categories WHERE name = ?', (category,))
        category_id = cursor.fetchone()[0]
        updates.append('category_id = ?')
        params.append(category_id)

    if updates:
        params.append(bookmark_id)
        cursor.execute(f'UPDATE bookmarks SET {", ".join(updates)} WHERE id = ?', params)
        conn.commit()

    conn.close()

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

def create_share_link(bookmark_id):
    """共有リンク作成"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 既存の共有キーをチェック
    cursor.execute('SELECT shared_key FROM bookmarks WHERE id = ?', (bookmark_id,))
    result = cursor.fetchone()

    if result and result[0]:
        shared_key = result[0]
    else:
        # 新しい共有キーを生成
        shared_key = hashlib.md5(f"{bookmark_id}{datetime.now()}".encode()).hexdigest()[:12]
        cursor.execute('UPDATE bookmarks SET shared_key = ? WHERE id = ?', (shared_key, bookmark_id))
        conn.commit()

    conn.close()
    return shared_key

def get_by_shared_key(shared_key):
    """共有キーでブックマーク取得"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM bookmarks WHERE shared_key = ?', (shared_key,))
    bookmark = cursor.fetchone()

    if bookmark:
        cursor.execute('UPDATE bookmarks SET view_count = view_count + 1 WHERE id = ?', (bookmark[0],))
        conn.commit()

    conn.close()
    return bookmark

def get_stats():
    """統計情報"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    stats = {}

    # 全ブックマーク数
    cursor.execute('SELECT COUNT(*) FROM bookmarks')
    stats['total_bookmarks'] = cursor.fetchone()[0]

    # カテゴリ別
    cursor.execute('''
    SELECT c.name, COUNT(b.id) as count
    FROM categories c
    LEFT JOIN bookmarks b ON c.id = b.category_id
    GROUP BY c.id
    ORDER BY count DESC
    ''')
    stats['by_category'] = dict(cursor.fetchall())

    # タグ別
    cursor.execute('''
    SELECT t.name, COUNT(bt.bookmark_id) as count
    FROM tags t
    LEFT JOIN bookmark_tags bt ON t.id = bt.tag_id
    GROUP BY t.id
    ORDER BY count DESC
    ''')
    stats['by_tag'] = dict(cursor.fetchall())

    # 共有済み
    cursor.execute('SELECT COUNT(*) FROM bookmarks WHERE shared_key IS NOT NULL')
    stats['shared'] = cursor.fetchone()[0]

    conn.close()
    return stats

def export_json():
    """JSONエクスポート"""
    import json
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    bookmarks = []
    cursor.execute('''
    SELECT b.id, b.url, b.title, b.description, c.name as category, b.shared_key,
           b.view_count, b.created_at, b.updated_at,
           GROUP_CONCAT(t.name) as tags
    FROM bookmarks b
    LEFT JOIN categories c ON b.category_id = c.id
    LEFT JOIN bookmark_tags bt ON b.id = bt.bookmark_id
    LEFT JOIN tags t ON bt.tag_id = t.id
    GROUP BY b.id
    ORDER BY b.created_at DESC
    ''')

    for row in cursor.fetchall():
        bookmark = dict(row)
        bookmark['tags'] = bookmark['tags'].split(',') if bookmark['tags'] else []
        bookmarks.append(bookmark)

    conn.close()
    return json.dumps(bookmarks, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    init_db()
