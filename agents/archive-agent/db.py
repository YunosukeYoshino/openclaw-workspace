#!/usr/bin/env python3
"""
Archive Agent - アーカイブ管理
- アーカイブアイテムの登録・管理
- アーカイブカテゴリの管理
- アーカイブの検索・参照
- アーカイブのステータス管理（アクティブ/アーカイブ済み）
"""

import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / "archive.db"

def init_db():
    """データベース初期化"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # カテゴリテーブル
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        description TEXT,
        color TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # アーカイブアイテムテーブル
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS archive_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT,
        content TEXT,
        category_id INTEGER,
        status TEXT DEFAULT 'active' CHECK(status IN ('active', 'archived')),
        tags TEXT,
        priority INTEGER DEFAULT 0,
        url TEXT,
        file_path TEXT,
        metadata TEXT,
        archived_at TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (category_id) REFERENCES categories(id)
    )
    ''')

    # アーカイブタグテーブル（タグの正規化管理）
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tags (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # アイテム-タグ紐付けテーブル
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS item_tags (
        item_id INTEGER NOT NULL,
        tag_id INTEGER NOT NULL,
        PRIMARY KEY (item_id, tag_id),
        FOREIGN KEY (item_id) REFERENCES archive_items(id) ON DELETE CASCADE,
        FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
    )
    ''')

    # 更新トリガー
    cursor.execute('''
    CREATE TRIGGER IF NOT EXISTS update_categories_updated_at
    AFTER UPDATE ON categories
    BEGIN
        UPDATE categories SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
    END
    ''')

    cursor.execute('''
    CREATE TRIGGER IF NOT EXISTS update_archive_items_updated_at
    AFTER UPDATE ON archive_items
    BEGIN
        UPDATE archive_items SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
    END
    ''')

    # インデックス
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_archive_items_status ON archive_items(status)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_archive_items_category ON archive_items(category_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_archive_items_priority ON archive_items(priority)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_archive_items_created_at ON archive_items(created_at)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_archive_items_archived_at ON archive_items(archived_at)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_item_tags_item_id ON item_tags(item_id)')

    conn.commit()
    conn.close()
    print("✅ データベース初期化完了")

def add_category(name, description=None, color=None):
    """カテゴリを追加"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute('''
        INSERT INTO categories (name, description, color)
        VALUES (?, ?, ?)
        ''', (name, description, color))
        category_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return category_id
    except sqlite3.IntegrityError:
        conn.close()
        return None

def get_category(category_id):
    """カテゴリを取得"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT id, name, description, color, created_at, updated_at
    FROM categories WHERE id = ?
    ''', (category_id,))

    category = cursor.fetchone()
    conn.close()
    return category

def list_categories():
    """カテゴリ一覧"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT id, name, description, color, created_at, updated_at
    FROM categories
    ORDER BY name ASC
    ''')

    categories = cursor.fetchall()
    conn.close()
    return categories

def update_category(category_id, **kwargs):
    """カテゴリを更新"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    allowed_fields = ['name', 'description', 'color']

    set_clause = []
    params = []

    for field, value in kwargs.items():
        if field in allowed_fields:
            set_clause.append(f"{field} = ?")
            params.append(value)

    if not set_clause:
        conn.close()
        return False

    params.append(category_id)
    query = f"UPDATE categories SET {', '.join(set_clause)} WHERE id = ?"
    cursor.execute(query, params)

    conn.commit()
    conn.close()
    return True

def delete_category(category_id):
    """カテゴリを削除"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 関連アイテムのカテゴリをNULLに設定
    cursor.execute('UPDATE archive_items SET category_id = NULL WHERE category_id = ?', (category_id,))
    cursor.execute('DELETE FROM categories WHERE id = ?', (category_id,))

    conn.commit()
    conn.close()

def add_archive_item(title, description=None, content=None, category_id=None,
                     status='active', tags=None, priority=0, url=None,
                     file_path=None, metadata=None):
    """アーカイブアイテムを追加"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # ステータスがarchivedの場合、アーカイブ日時を設定
    archived_at = None
    if status == 'archived':
        archived_at = datetime.now().isoformat()

    cursor.execute('''
    INSERT INTO archive_items (title, description, content, category_id, status, tags, priority, url, file_path, metadata, archived_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (title, description, content, category_id, status, tags, priority, url, file_path, metadata, archived_at))

    item_id = cursor.lastrowid

    # タグを処理（同じ接続を使用）
    if tags:
        tag_list = [t.strip() for t in tags.split(',') if t.strip()]
        for tag_name in tag_list:
            # タグを取得または作成（同じ接続で）
            cursor.execute('SELECT id FROM tags WHERE name = ?', (tag_name,))
            result = cursor.fetchone()
            if result:
                tag_id = result[0]
            else:
                cursor.execute('INSERT INTO tags (name) VALUES (?)', (tag_name,))
                tag_id = cursor.lastrowid
            # アイテム-タグ紐付け
            cursor.execute('INSERT OR IGNORE INTO item_tags (item_id, tag_id) VALUES (?, ?)', (item_id, tag_id))

    conn.commit()
    conn.close()
    return item_id

def get_archive_item(item_id):
    """アーカイブアイテムを取得"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT id, title, description, content, category_id, status, tags, priority, url, file_path, metadata, archived_at, created_at, updated_at
    FROM archive_items WHERE id = ?
    ''', (item_id,))

    item = cursor.fetchone()
    conn.close()
    return item

def list_archive_items(status=None, category_id=None, priority=None, limit=50):
    """アーカイブアイテム一覧"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    query = '''
    SELECT id, title, description, category_id, status, tags, priority, url, archived_at, created_at, updated_at
    FROM archive_items
    '''
    params = []
    conditions = []

    if status:
        conditions.append('status = ?')
        params.append(status)
    if category_id:
        conditions.append('category_id = ?')
        params.append(category_id)
    if priority is not None:
        conditions.append('priority = ?')
        params.append(priority)

    if conditions:
        query += ' WHERE ' + ' AND '.join(conditions)

    query += ' ORDER BY created_at DESC LIMIT ?'
    params.append(limit)

    cursor.execute(query, params)
    items = cursor.fetchall()
    conn.close()
    return items

def search_archive_items(keyword, status=None, category_id=None, limit=50):
    """アーカイブアイテムを検索"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    query = '''
    SELECT id, title, description, category_id, status, tags, priority, url, archived_at, created_at, updated_at
    FROM archive_items
    WHERE (title LIKE ? OR description LIKE ? OR content LIKE ? OR tags LIKE ?)
    '''
    params = [f'%{keyword}%', f'%{keyword}%', f'%{keyword}%', f'%{keyword}%']

    if status:
        query += ' AND status = ?'
        params.append(status)
    if category_id:
        query += ' AND category_id = ?'
        params.append(category_id)

    query += ' ORDER BY created_at DESC LIMIT ?'
    params.append(limit)

    cursor.execute(query, params)
    items = cursor.fetchall()
    conn.close()
    return items

def update_archive_item(item_id, **kwargs):
    """アーカイブアイテムを更新"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    allowed_fields = ['title', 'description', 'content', 'category_id', 'status', 'tags',
                      'priority', 'url', 'file_path', 'metadata']

    set_clause = []
    params = []

    for field, value in kwargs.items():
        if field in allowed_fields:
            set_clause.append(f"{field} = ?")
            params.append(value)

    # ステータスがarchivedに変更された場合、archived_atを設定
    if 'status' in kwargs and kwargs['status'] == 'archived':
        set_clause.append('archived_at = ?')
        params.append(datetime.now().isoformat())

    if not set_clause:
        conn.close()
        return False

    params.append(item_id)
    query = f"UPDATE archive_items SET {', '.join(set_clause)} WHERE id = ?"
    cursor.execute(query, params)

    conn.commit()
    conn.close()
    return True

def archive_item(item_id):
    """アイテムをアーカイブ"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    UPDATE archive_items
    SET status = 'archived', archived_at = ?, updated_at = CURRENT_TIMESTAMP
    WHERE id = ?
    ''', (datetime.now().isoformat(), item_id))

    conn.commit()
    conn.close()

def unarchive_item(item_id):
    """アイテムのアーカイブを解除"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    UPDATE archive_items
    SET status = 'active', archived_at = NULL, updated_at = CURRENT_TIMESTAMP
    WHERE id = ?
    ''', (item_id,))

    conn.commit()
    conn.close()

def delete_archive_item(item_id):
    """アーカイブアイテムを削除"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('DELETE FROM item_tags WHERE item_id = ?', (item_id,))
    cursor.execute('DELETE FROM archive_items WHERE id = ?', (item_id,))

    conn.commit()
    conn.close()

def get_or_create_tag(tag_name):
    """タグを取得または作成"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('SELECT id FROM tags WHERE name = ?', (tag_name,))
    result = cursor.fetchone()

    if result:
        tag_id = result[0]
    else:
        cursor.execute('INSERT INTO tags (name) VALUES (?)', (tag_name,))
        tag_id = cursor.lastrowid
        conn.commit()

    conn.close()
    return tag_id

def get_item_tags(item_id):
    """アイテムのタグを取得"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT t.id, t.name
    FROM tags t
    JOIN item_tags it ON t.id = it.tag_id
    WHERE it.item_id = ?
    ORDER BY t.name
    ''', (item_id,))

    tags = cursor.fetchall()
    conn.close()
    return tags

def add_tag_to_item(item_id, tag_name):
    """アイテムにタグを追加"""
    tag_id = get_or_create_tag(tag_name)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('INSERT OR IGNORE INTO item_tags (item_id, tag_id) VALUES (?, ?)', (item_id, tag_id))

    conn.commit()
    conn.close()

def remove_tag_from_item(item_id, tag_name):
    """アイテムからタグを削除"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    DELETE FROM item_tags
    WHERE item_id = ? AND tag_id = (SELECT id FROM tags WHERE name = ?)
    ''', (item_id, tag_name))

    conn.commit()
    conn.close()

def get_items_by_tag(tag_name, limit=50):
    """タグでアイテムを検索"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT ai.id, ai.title, ai.description, ai.category_id, ai.status, ai.tags, ai.priority, ai.url, ai.archived_at, ai.created_at, ai.updated_at
    FROM archive_items ai
    JOIN item_tags it ON ai.id = it.item_id
    JOIN tags t ON it.tag_id = t.id
    WHERE t.name = ?
    ORDER BY ai.created_at DESC
    LIMIT ?
    ''', (tag_name, limit))

    items = cursor.fetchall()
    conn.close()
    return items

def get_all_tags(limit=50):
    """全タグを取得"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT t.id, t.name, COUNT(it.item_id) as item_count
    FROM tags t
    LEFT JOIN item_tags it ON t.id = it.tag_id
    GROUP BY t.id
    ORDER BY item_count DESC, t.name
    LIMIT ?
    ''', (limit,))

    tags = cursor.fetchall()
    conn.close()
    return tags

def get_archive_stats():
    """統計情報"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    stats = {}

    # カテゴリ数
    cursor.execute('SELECT COUNT(*) FROM categories')
    stats['total_categories'] = cursor.fetchone()[0]

    # アイテム数
    cursor.execute('SELECT COUNT(*) FROM archive_items')
    stats['total_items'] = cursor.fetchone()[0]

    # アクティブ/アーカイブ済みアイテム数
    cursor.execute('SELECT COUNT(*) FROM archive_items WHERE status = "active"')
    stats['active_items'] = cursor.fetchone()[0]

    cursor.execute('SELECT COUNT(*) FROM archive_items WHERE status = "archived"')
    stats['archived_items'] = cursor.fetchone()[0]

    # タグ数
    cursor.execute('SELECT COUNT(*) FROM tags')
    stats['total_tags'] = cursor.fetchone()[0]

    # カテゴリ別アイテム数
    cursor.execute('''
    SELECT c.name, COUNT(ai.id) as count
    FROM categories c
    LEFT JOIN archive_items ai ON c.id = ai.category_id
    GROUP BY c.id
    ORDER BY count DESC
    ''')
    stats['by_category'] = cursor.fetchall()

    # 今日追加されたアイテム数
    today = datetime.now().strftime("%Y-%m-%d")
    cursor.execute('SELECT COUNT(*) FROM archive_items WHERE DATE(created_at) = ?', (today,))
    stats['today_added'] = cursor.fetchone()[0]

    # 今月アーカイブされたアイテム数
    current_month = datetime.now().strftime("%Y-%m")
    cursor.execute('SELECT COUNT(*) FROM archive_items WHERE archived_at LIKE ?', (f"{current_month}%",))
    stats['month_archived'] = cursor.fetchone()[0]

    conn.close()
    return stats

if __name__ == '__main__':
    init_db()
