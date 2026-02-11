#!/usr/bin/env python3
"""
買い物エージェント #34
- 買い物リスト管理
- 商品・カテゴリ・価格・購入状況・優先順位
"""

import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / "shopping.db"

def init_db():
    """データベース初期化"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 商品テーブル
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        category TEXT,
        price INTEGER,
        quantity INTEGER DEFAULT 1,
        status TEXT DEFAULT 'pending' CHECK(status IN ('pending', 'purchased', 'cancelled')),
        priority INTEGER CHECK(priority IN (1,2,3)),
        store TEXT,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        purchased_at TIMESTAMP
    )
    ''')

    # 更新トリガー
    cursor.execute('''
    CREATE TRIGGER IF NOT EXISTS update_items_purchased_at
    AFTER UPDATE OF status ON items
    WHEN NEW.status = 'purchased' AND OLD.status != 'purchased'
    BEGIN
        UPDATE items SET purchased_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
    END
    ''')

    # インデックス
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_items_status ON items(status)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_items_category ON items(category)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_items_priority ON items(priority)')

    conn.commit()
    conn.close()
    print("✅ データベース初期化完了")

def add_item(name, category=None, price=None, quantity=1, status='pending', priority=None, store=None, notes=None):
    """商品追加"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO items (name, category, price, quantity, status, priority, store, notes)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (name, category, price, quantity, status, priority, store, notes))

    item_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return item_id

def update_item(item_id, name=None, category=None, price=None, quantity=None, status=None, priority=None, store=None, notes=None):
    """商品更新"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    updates = []
    params = []

    if name:
        updates.append("name = ?")
        params.append(name)
    if category:
        updates.append("category = ?")
        params.append(category)
    if price is not None:
        updates.append("price = ?")
        params.append(price)
    if quantity is not None:
        updates.append("quantity = ?")
        params.append(quantity)
    if status:
        updates.append("status = ?")
        params.append(status)
    if priority:
        updates.append("priority = ?")
        params.append(priority)
    if store:
        updates.append("store = ?")
        params.append(store)
    if notes:
        updates.append("notes = ?")
        params.append(notes)

    if updates:
        query = f"UPDATE items SET {', '.join(updates)} WHERE id = ?"
        params.append(item_id)
        cursor.execute(query, params)
        conn.commit()

    conn.close()

def delete_item(item_id):
    """商品削除"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('DELETE FROM items WHERE id = ?', (item_id,))

    conn.commit()
    conn.close()

def list_items(status=None, category=None, store=None, limit=20):
    """商品一覧"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    query = '''
    SELECT id, name, category, price, quantity, status, priority, store, notes, created_at, purchased_at
    FROM items
    '''

    params = []
    conditions = []

    if status:
        conditions.append("status = ?")
        params.append(status)
    if category:
        conditions.append("category = ?")
        params.append(category)
    if store:
        conditions.append("store = ?")
        params.append(store)

    if conditions:
        query += ' WHERE ' + ' AND '.join(conditions)

    query += ' ORDER BY priority DESC, created_at ASC LIMIT ?'
    params.append(limit)

    cursor.execute(query, params)
    items = cursor.fetchall()
    conn.close()
    return items

def search_items(keyword):
    """商品検索"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT id, name, category, price, quantity, status, priority, store, notes, created_at, purchased_at
    FROM items
    WHERE name LIKE ? OR category LIKE ? OR store LIKE ? OR notes LIKE ?
    ORDER BY priority DESC, created_at ASC
    ''', (f'%{keyword}%', f'%{keyword}%', f'%{keyword}%', f'%{keyword}%'))

    items = cursor.fetchall()
    conn.close()
    return items

def get_stats():
    """統計情報"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    stats = {}

    # 全商品数
    cursor.execute('SELECT COUNT(*) FROM items')
    stats['total'] = cursor.fetchone()[0]

    # 未購入
    cursor.execute('SELECT COUNT(*) FROM items WHERE status = "pending"')
    stats['pending'] = cursor.fetchone()[0]

    # 購入済み
    cursor.execute('SELECT COUNT(*) FROM items WHERE status = "purchased"')
    stats['purchased'] = cursor.fetchone()[0]

    # 総額
    cursor.execute('SELECT SUM(price * quantity) FROM items WHERE price IS NOT NULL')
    total_amount = cursor.fetchone()[0]
    stats['total_amount'] = total_amount if total_amount else 0

    # 未購入の総額
    cursor.execute('SELECT SUM(price * quantity) FROM items WHERE status = "pending" AND price IS NOT NULL')
    pending_amount = cursor.fetchone()[0]
    stats['pending_amount'] = pending_amount if pending_amount else 0

    conn.close()
    return stats

if __name__ == '__main__':
    init_db()
