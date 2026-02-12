#!/usr/bin/env python3
"""
ストレスレベル記録エージェント #63
- ストレスレベルの追跡と管理
- ストレス要因の記録
- リラックス方法の記録
"""

import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / "stress.db"

def init_db():
    """データベース初期化"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # ストレスレベルテーブル
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS stress_levels (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        level INTEGER NOT NULL CHECK(level >= 1 AND level <= 10),
        trigger TEXT,
        category TEXT CHECK(category IN ('work', 'personal', 'health', 'finance', 'relationship', 'other')),
        symptoms TEXT,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # リラックス方法テーブル
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS relaxation_methods (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        category TEXT,
        effectiveness INTEGER CHECK(effectiveness >= 1 AND effectiveness <= 5),
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # インデックス
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_stress_level ON stress_levels(level)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_stress_category ON stress_levels(category)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_stress_created ON stress_levels(created_at)')

    conn.commit()
    conn.close()
    print("✅ データベース初期化完了")

def add_stress(level, trigger=None, category=None, symptoms=None, notes=None):
    """ストレスレベルを追加"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO stress_levels (level, trigger, category, symptoms, notes)
    VALUES (?, ?, ?, ?, ?)
    ''', (level, trigger, category, symptoms, notes))

    stress_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return stress_id

def add_relaxation_method(name, category=None, effectiveness=3, notes=None):
    """リラックス方法を追加"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO relaxation_methods (name, category, effectiveness, notes)
    VALUES (?, ?, ?, ?)
    ''', (name, category, effectiveness, notes))

    method_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return method_id

def list_stress(limit=20):
    """ストレスレベル一覧"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT id, level, trigger, category, symptoms, notes, created_at
    FROM stress_levels
    ORDER BY created_at DESC
    LIMIT ?
    ''', (limit,))

    stress = cursor.fetchall()
    conn.close()
    return stress

def list_relaxation_methods(limit=20):
    """リラックス方法一覧"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT id, name, category, effectiveness, notes, created_at
    FROM relaxation_methods
    ORDER BY effectiveness DESC, created_at DESC
    LIMIT ?
    ''', (limit,))

    methods = cursor.fetchall()
    conn.close()
    return methods

def get_stats(days=7):
    """ストレス統計"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    from datetime import timedelta
    cutoff_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d %H:%M")

    # 合計数
    cursor.execute('''
    SELECT COUNT(*) FROM stress_levels
    WHERE created_at >= ?
    ''', (cutoff_date,))
    total = cursor.fetchone()[0]

    # 平均ストレスレベル
    cursor.execute('''
    SELECT AVG(level) FROM stress_levels
    WHERE created_at >= ?
    ''', (cutoff_date,))
    avg_level = cursor.fetchone()[0] or 0

    # カテゴリ別平均
    cursor.execute('''
    SELECT category, AVG(level) as avg_level, COUNT(*) as count
    FROM stress_levels
    WHERE created_at >= ? AND category IS NOT NULL
    GROUP BY category
    ORDER BY avg_level DESC
    ''', (cutoff_date,))
    by_category = [{'category': r[0], 'avg': round(r[1], 1), 'count': r[2]} for r in cursor.fetchall()]

    # 最高・最低
    cursor.execute('''
    SELECT MAX(level), MIN(level) FROM stress_levels
    WHERE created_at >= ?
    ''', (cutoff_date,))
    max_min = cursor.fetchone()

    conn.close()
    return {
        'total': total,
        'avg_level': round(avg_level, 1),
        'by_category': by_category,
        'max': max_min[0] if max_min[0] else 0,
        'min': max_min[1] if max_min[1] else 0
    }

if __name__ == '__main__':
    init_db()
