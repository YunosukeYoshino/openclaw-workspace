#!/usr/bin/env python3
"""
ギフト記録エージェント #66
- プレゼントの記録（もらった/あげた）
- ギフトアイデアの保存
- ギフト管理
"""

import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / "gift.db"

def init_db():
    """データベース初期化"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # ギフトテーブル
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS gifts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        type TEXT NOT NULL CHECK(type IN ('received', 'given')),
        item_name TEXT NOT NULL,
        recipient_name TEXT,
        sender_name TEXT,
        occasion TEXT,
        date DATE,
        price REAL,
        notes TEXT,
        tags TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # ギフトアイデアテーブル
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS gift_ideas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        target_name TEXT NOT NULL,
        item_name TEXT NOT NULL,
        category TEXT,
        priority INTEGER DEFAULT 3 CHECK(priority >= 1 AND priority <= 5),
        notes TEXT,
        status TEXT DEFAULT 'idea' CHECK(status IN ('idea', 'planned', 'purchased', 'given')),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # インデックス
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_gift_type ON gifts(type)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_gift_date ON gifts(date)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_idea_target ON gift_ideas(target_name)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_idea_status ON gift_ideas(status)')

    conn.commit()
    conn.close()
    print("✅ データベース初期化完了")

def add_gift(gift_type, item_name, recipient_name=None, sender_name=None, occasion=None,
             date=None, price=None, notes=None, tags=None):
    """ギフトを追加"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")

    cursor.execute('''
    INSERT INTO gifts (type, item_name, recipient_name, sender_name, occasion, date, price, notes, tags)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (gift_type, item_name, recipient_name, sender_name, occasion, date, price, notes, tags))

    gift_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return gift_id

def add_gift_idea(target_name, item_name, category=None, priority=3, notes=None):
    """ギフトアイデアを追加"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO gift_ideas (target_name, item_name, category, priority, notes)
    VALUES (?, ?, ?, ?, ?)
    ''', (target_name, item_name, category, priority, notes))

    idea_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return idea_id

def list_gifts(gift_type=None, limit=20):
    """ギフト一覧"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    query = '''
    SELECT id, type, item_name, recipient_name, sender_name, occasion, date, price, notes, tags, created_at
    FROM gifts
    '''

    params = []
    if gift_type:
        query += ' WHERE type = ?'
        params.append(gift_type)

    query += ' ORDER BY date DESC, created_at DESC LIMIT ?'
    params.append(limit)

    cursor.execute(query, params)
    gifts = cursor.fetchall()
    conn.close()
    return gifts

def list_gift_ideas(target_name=None, status=None, limit=20):
    """ギフトアイデア一覧"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    query = '''
    SELECT id, target_name, item_name, category, priority, notes, status, created_at
    FROM gift_ideas
    '''

    params = []
    conditions = []

    if target_name:
        conditions.append("target_name LIKE ?")
        params.append(f"%{target_name}%")

    if status:
        conditions.append("status = ?")
        params.append(status)

    if conditions:
        query += ' WHERE ' + ' AND '.join(conditions)

    query += ' ORDER BY priority DESC, created_at DESC LIMIT ?'
    params.append(limit)

    cursor.execute(query, params)
    ideas = cursor.fetchall()
    conn.close()
    return ideas

def update_gift_idea(idea_id, status=None, priority=None):
    """ギフトアイデアを更新"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    updates = []
    params = []

    if status:
        updates.append("status = ?")
        params.append(status)
    if priority:
        updates.append("priority = ?")
        params.append(priority)

    if updates:
        updates.append("updated_at = ?")
        params.append(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        query = f"UPDATE gift_ideas SET {', '.join(updates)} WHERE id = ?"
        params.append(idea_id)
        cursor.execute(query, params)
        conn.commit()

    conn.close()

def get_stats():
    """ギフト統計"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    stats = {}

    # タイプ別
    cursor.execute('SELECT type, COUNT(*) FROM gifts GROUP BY type')
    by_type = dict(cursor.fetchall())
    stats['by_type'] = by_type

    # 今年の数
    current_year = datetime.now().year
    cursor.execute('SELECT COUNT(*) FROM gifts WHERE date LIKE ?', (f'{current_year}%',))
    stats['this_year'] = cursor.fetchone()[0]

    # アイデア数
    cursor.execute('SELECT COUNT(*) FROM gift_ideas WHERE status = ?', ('idea',))
    stats['idea_count'] = cursor.fetchone()[0]

    conn.close()
    return stats

if __name__ == '__main__':
    init_db()
