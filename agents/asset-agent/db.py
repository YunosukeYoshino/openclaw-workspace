#!/usr/bin/env python3
"""
資産管理エージェント #13
- 資産の記録と追跡
- 統計機能
"""

import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / "assets.db"

def init_db():
    """データベース初期化"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 資産テーブル
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS assets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        type TEXT NOT NULL CHECK(type IN ('cash', 'bank', 'investment', 'property', 'digital', 'other')),
        name TEXT NOT NULL,
        amount REAL NOT NULL,
        currency TEXT DEFAULT 'JPY',
        memo TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # 資産履歴テーブル
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS asset_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        asset_id INTEGER NOT NULL,
        amount REAL NOT NULL,
        change REAL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (asset_id) REFERENCES assets(id) ON DELETE CASCADE
    )
    ''')

    # インデックス
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_assets_type ON assets(type)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_assets_created ON assets(created_at)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_asset_history_asset ON asset_history(asset_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_asset_history_created ON asset_history(created_at)')

    conn.commit()
    conn.close()
    print("✅ データベース初期化完了")

def add_asset(asset_type, name, amount, currency='JPY', memo=None):
    """資産追加"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO assets (type, name, amount, currency, memo)
    VALUES (?, ?, ?, ?, ?)
    ''', (asset_type, name, amount, currency, memo))

    asset_id = cursor.lastrowid

    # 履歴に追加
    cursor.execute('''
    INSERT INTO asset_history (asset_id, amount, change)
    VALUES (?, ?, ?)
    ''', (asset_id, amount, amount))

    conn.commit()
    conn.close()
    return asset_id

def update_asset(asset_id, amount, change=None):
    """資産更新"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    if change is None:
        # 既存の金額を取得
        cursor.execute('SELECT amount FROM assets WHERE id = ?', (asset_id,))
        result = cursor.fetchone()
        old_amount = result[0] if result else 0
        change = amount - old_amount

    cursor.execute('''
    UPDATE assets SET amount = ? WHERE id = ?
    ''', (amount, asset_id))

    # 履歴に追加
    cursor.execute('''
    INSERT INTO asset_history (asset_id, amount, change)
    VALUES (?, ?, ?)
    ''', (asset_id, amount, change))

    conn.commit()
    conn.close()

def list_assets():
    """資産一覧"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT id, type, name, amount, currency, memo, created_at
    FROM assets
    ORDER BY created_at DESC
    ''')

    assets = cursor.fetchall()
    conn.close()
    return assets

def get_total_assets():
    """総資産計算"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT type, SUM(amount) as total
    FROM assets
    GROUP BY type
    ''')

    by_type = dict(cursor.fetchall())

    # 合計
    cursor.execute('SELECT SUM(amount) FROM assets')
    total = cursor.fetchone()[0] or 0

    conn.close()
    return {
        'total': total,
        'by_type': by_type
    }

if __name__ == '__main__':
    init_db()
