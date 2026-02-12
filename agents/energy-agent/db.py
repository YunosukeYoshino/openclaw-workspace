#!/usr/bin/env python3
"""
エネルギーレベル記録エージェント #62
- 毎日のエネルギーレベルの記録
- 時間帯別の追跡
- パターンの分析
"""

import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / "energy.db"

def init_db():
    """データベース初期化"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # エネルギーレベルテーブル
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS energy_levels (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        level INTEGER NOT NULL CHECK(level >= 1 AND level <= 10),
        time_period TEXT CHECK(time_period IN ('morning', 'afternoon', 'evening', 'night')),
        activity TEXT,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # インデックス
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_energy_level ON energy_levels(level)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_energy_period ON energy_levels(time_period)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_energy_created ON energy_levels(created_at)')

    conn.commit()
    conn.close()
    print("✅ データベース初期化完了")

def add_energy(level, time_period=None, activity=None, notes=None):
    """エネルギーレベルを追加"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO energy_levels (level, time_period, activity, notes)
    VALUES (?, ?, ?, ?)
    ''', (level, time_period, activity, notes))

    energy_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return energy_id

def list_energy(limit=20):
    """エネルギーレベル一覧"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT id, level, time_period, activity, notes, created_at
    FROM energy_levels
    ORDER BY created_at DESC
    LIMIT ?
    ''', (limit,))

    energies = cursor.fetchall()
    conn.close()
    return energies

def get_stats(days=7):
    """エネルギー統計"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    from datetime import timedelta
    cutoff_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d %H:%M")

    # 合計数
    cursor.execute('''
    SELECT COUNT(*) FROM energy_levels
    WHERE created_at >= ?
    ''', (cutoff_date,))
    total = cursor.fetchone()[0]

    # 平均エネルギーレベル
    cursor.execute('''
    SELECT AVG(level) FROM energy_levels
    WHERE created_at >= ?
    ''', (cutoff_date,))
    avg_level = cursor.fetchone()[0] or 0

    # 時間帯別平均
    cursor.execute('''
    SELECT time_period, AVG(level) as avg_level
    FROM energy_levels
    WHERE created_at >= ? AND time_period IS NOT NULL
    GROUP BY time_period
    ''', (cutoff_date,))
    by_period = dict(cursor.fetchall())

    # 最高・最低
    cursor.execute('''
    SELECT MAX(level), MIN(level) FROM energy_levels
    WHERE created_at >= ?
    ''', (cutoff_date,))
    max_min = cursor.fetchone()

    conn.close()
    return {
        'total': total,
        'avg_level': round(avg_level, 1),
        'by_period': {k: round(v, 1) for k, v in by_period.items()},
        'max': max_min[0] if max_min[0] else 0,
        'min': max_min[1] if max_min[1] else 0
    }

if __name__ == '__main__':
    init_db()
