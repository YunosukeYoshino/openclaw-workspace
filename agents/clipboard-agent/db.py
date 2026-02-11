#!/usr/bin/env python3
"""
クリップボード管理エージェント
- クリップボード履歴の保存
- クリップボードの検索
- よく使うテキストの保存
"""

import sqlite3
from pathlib import Path
from datetime import datetime
from hashlib import sha256

DB_PATH = Path(__file__).parent / "clipboard.db"

def init_db():
    """データベース初期化"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # クリップボード履歴テーブル
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS clipboard_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        content TEXT NOT NULL,
        content_hash TEXT UNIQUE NOT NULL,
        content_type TEXT DEFAULT 'text',
        size INTEGER NOT NULL,
        use_count INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # よく使うテキスト（スニペット）テーブル
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS snippets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        description TEXT,
        category_id INTEGER,
        is_favorite BOOLEAN DEFAULT 0,
        use_count INTEGER DEFAULT 0,
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

    # スニペット・タグ紐付け
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS snippet_tags (
        snippet_id INTEGER NOT NULL,
        tag_id INTEGER NOT NULL,
        PRIMARY KEY (snippet_id, tag_id),
        FOREIGN KEY (snippet_id) REFERENCES snippets(id) ON DELETE CASCADE,
        FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
    )
    ''')

    # 更新トリガー
    cursor.execute('''
    CREATE TRIGGER IF NOT EXISTS update_snippets_timestamp
    AFTER UPDATE ON snippets
    BEGIN
        UPDATE snippets SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
    END
    ''')

    cursor.execute('''
    CREATE TRIGGER IF NOT EXISTS update_clipboard_last_used
    AFTER UPDATE ON clipboard_history
    BEGIN
        UPDATE clipboard_history SET last_used = CURRENT_TIMESTAMP WHERE id = NEW.id;
    END
    ''')

    # インデックス
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_history_created ON clipboard_history(created_at)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_history_hash ON clipboard_history(content_hash)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_history_last_used ON clipboard_history(last_used)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_snippets_category ON snippets(category_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_snippets_favorite ON snippets(is_favorite)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_snippet_tags_tag ON snippet_tags(tag_id)')

    # デフォルトカテゴリ
    default_categories = [
        ('Code', '#3498db'),
        ('コード', '#3498db'),
        ('Email', '#2ecc71'),
        ('メール', '#2ecc71'),
        ('Response', '#f39c12'),
        ('返信', '#f39c12'),
        ('Template', '#9b59b6'),
        ('テンプレート', '#9b59b6'),
    ]
    for name, color in default_categories:
        cursor.execute('INSERT OR IGNORE INTO categories (name, color) VALUES (?, ?)', (name, color))

    conn.commit()
    conn.close()
    print("✅ クリップボードデータベース初期化完了")

def _compute_hash(content):
    """コンテンツのハッシュを計算"""
    return sha256(content.encode('utf-8')).hexdigest()

def add_to_history(content, content_type='text'):
    """履歴に追加"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    content_hash = _compute_hash(content)
    size = len(content.encode('utf-8'))

    # 既存のコンテンツがある場合は使用カウントを増やす
    cursor.execute('SELECT id, use_count FROM clipboard_history WHERE content_hash = ?',
                  (content_hash,))
    result = cursor.fetchone()

    if result:
        cursor.execute('''
        UPDATE clipboard_history
        SET use_count = use_count + 1, last_used = CURRENT_TIMESTAMP
        WHERE id = ?
        ''', (result[0],))
        conn.commit()
        conn.close()
        return result[0]

    # 新規追加
    cursor.execute('''
    INSERT INTO clipboard_history (content, content_hash, size)
    VALUES (?, ?, ?)
    ''', (content, content_hash, size))

    history_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return history_id

def get_history(limit=50, content_type=None):
    """履歴を取得"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    if content_type:
        cursor.execute('''
        SELECT id, substr(content, 1, 100), content_type, size, use_count, last_used
        FROM clipboard_history
        WHERE content_type = ?
        ORDER BY last_used DESC
        LIMIT ?
        ''', (content_type, limit))
    else:
        cursor.execute('''
        SELECT id, substr(content, 1, 100), content_type, size, use_count, last_used
        FROM clipboard_history
        ORDER BY last_used DESC
        LIMIT ?
        ''', (limit,))

    history = cursor.fetchall()
    conn.close()
    return history

def get_history_item(history_id):
    """履歴アイテムを取得"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM clipboard_history WHERE id = ?', (history_id,))
    item = cursor.fetchone()

    if item:
        cursor.execute('''
        UPDATE clipboard_history
        SET use_count = use_count + 1, last_used = CURRENT_TIMESTAMP
        WHERE id = ?
        ''', (history_id,))
        conn.commit()

    conn.close()
    return item

def search_history(keyword):
    """履歴を検索"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT id, substr(content, 1, 100), content_type, size, use_count, last_used
    FROM clipboard_history
    WHERE content LIKE ?
    ORDER BY last_used DESC
    ''', (f'%{keyword}%',))

    results = cursor.fetchall()
    conn.close()
    return results

def add_snippet(title, content, description=None, category=None, tags=None, is_favorite=False):
    """スニペットを追加"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # カテゴリID取得/作成
    category_id = None
    if category:
        cursor.execute('INSERT OR IGNORE INTO categories (name) VALUES (?)', (category,))
        cursor.execute('SELECT id FROM categories WHERE name = ?', (category,))
        category_id = cursor.fetchone()[0]

    # スニペット追加
    cursor.execute('''
    INSERT INTO snippets (title, content, description, category_id, is_favorite)
    VALUES (?, ?, ?, ?, ?)
    ''', (title, content, description, category_id, is_favorite))

    snippet_id = cursor.lastrowid

    # タグ紐付け
    if tags:
        for tag in tags:
            cursor.execute('INSERT OR IGNORE INTO tags (name) VALUES (?)', (tag,))
            cursor.execute('SELECT id FROM tags WHERE name = ?', (tag,))
            tag_id = cursor.fetchone()[0]
            cursor.execute('INSERT OR IGNORE INTO snippet_tags (snippet_id, tag_id) VALUES (?, ?)',
                          (snippet_id, tag_id))

    conn.commit()
    conn.close()
    return snippet_id

def get_snippets(limit=50, category=None, favorites_only=False):
    """スニペット一覧"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    query = '''
    SELECT s.id, s.title, substr(s.content, 1, 100), s.description, c.name, s.is_favorite, s.use_count, s.updated_at
    FROM snippets s
    LEFT JOIN categories c ON s.category_id = c.id
    WHERE 1=1
    '''
    params = []

    if category:
        query += ' AND c.name = ?'
        params.append(category)

    if favorites_only:
        query += ' AND s.is_favorite = 1'

    query += ' ORDER BY s.updated_at DESC LIMIT ?'
    params.append(limit)

    cursor.execute(query, params)
    snippets = cursor.fetchall()
    conn.close()
    return snippets

def get_snippet(snippet_id):
    """スニペットを取得"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM snippets WHERE id = ?', (snippet_id,))
    snippet = cursor.fetchone()

    if snippet:
        cursor.execute('UPDATE snippets SET use_count = use_count + 1 WHERE id = ?', (snippet_id,))
        conn.commit()

    conn.close()
    return snippet

def search_snippets(keyword):
    """スニペットを検索"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT s.id, s.title, substr(s.content, 1, 100), s.description, c.name, s.is_favorite, s.use_count, s.updated_at
    FROM snippets s
    LEFT JOIN categories c ON s.category_id = c.id
    WHERE s.title LIKE ? OR s.content LIKE ? OR s.description LIKE ?
    ORDER BY s.updated_at DESC
    ''', (f'%{keyword}%', f'%{keyword}%', f'%{keyword}%'))

    results = cursor.fetchall()
    conn.close()
    return results

def search_snippets_by_tag(tag_name):
    """タグでスニペットを検索"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT s.id, s.title, substr(s.content, 1, 100), s.description, c.name, s.is_favorite, s.use_count, s.updated_at
    FROM snippets s
    LEFT JOIN categories c ON s.category_id = c.id
    JOIN snippet_tags st ON s.id = st.snippet_id
    JOIN tags t ON st.tag_id = t.id
    WHERE t.name = ?
    ORDER BY s.updated_at DESC
    ''', (tag_name,))

    results = cursor.fetchall()
    conn.close()
    return results

def update_snippet(snippet_id, title=None, content=None, description=None, category=None, is_favorite=None):
    """スニペットを更新"""
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
    if description is not None:
        updates.append('description = ?')
        params.append(description)
    if category is not None:
        cursor.execute('INSERT OR IGNORE INTO categories (name) VALUES (?)', (category,))
        cursor.execute('SELECT id FROM categories WHERE name = ?', (category,))
        category_id = cursor.fetchone()[0]
        updates.append('category_id = ?')
        params.append(category_id)
    if is_favorite is not None:
        updates.append('is_favorite = ?')
        params.append(1 if is_favorite else 0)

    if updates:
        params.append(snippet_id)
        cursor.execute(f'UPDATE snippets SET {", ".join(updates)} WHERE id = ?', params)
        conn.commit()

    conn.close()

def delete_snippet(snippet_id):
    """スニペットを削除"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM snippets WHERE id = ?', (snippet_id,))
    conn.commit()
    conn.close()

def delete_history_item(history_id):
    """履歴アイテムを削除"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM clipboard_history WHERE id = ?', (history_id,))
    conn.commit()
    conn.close()

def clear_old_history(days=30):
    """古い履歴をクリア"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    DELETE FROM clipboard_history
    WHERE last_used < datetime('now', '-' || ? || ' days')
    ''', (days,))

    deleted = cursor.rowcount
    conn.commit()
    conn.close()
    return deleted

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

def get_stats():
    """統計情報"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    stats = {}

    # 履歴数
    cursor.execute('SELECT COUNT(*) FROM clipboard_history')
    stats['history_count'] = cursor.fetchone()[0]

    # スニペット数
    cursor.execute('SELECT COUNT(*) FROM snippets')
    stats['snippet_count'] = cursor.fetchone()[0]

    # お気に入り数
    cursor.execute('SELECT COUNT(*) FROM snippets WHERE is_favorite = 1')
    stats['favorite_count'] = cursor.fetchone()[0]

    # カテゴリ別
    cursor.execute('''
    SELECT c.name, COUNT(s.id) as count
    FROM categories c
    LEFT JOIN snippets s ON c.id = s.category_id
    GROUP BY c.id
    ORDER BY count DESC
    ''')
    stats['snippets_by_category'] = dict(cursor.fetchall())

    # タグ別
    cursor.execute('''
    SELECT t.name, COUNT(st.snippet_id) as count
    FROM tags t
    LEFT JOIN snippet_tags st ON t.id = st.tag_id
    GROUP BY t.id
    ORDER BY count DESC
    ''')
    stats['snippets_by_tag'] = dict(cursor.fetchall())

    conn.close()
    return stats

if __name__ == '__main__':
    init_db()
