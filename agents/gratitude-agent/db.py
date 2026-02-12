#!/usr/bin/env python3
"""
グラティチュードエージェント #44
- 感謝日記
- 日付・感謝リスト・メモ
"""

import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / "gratitude.db"

def init_db():
    """データベース初期化"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 感謝テーブル
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS gratitude (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date DATE NOT NULL,
        item TEXT NOT NULL,
        category TEXT,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # インデックス
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_gratitude_date ON gratitude(date)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_gratitude_category ON gratitude(category)')

    conn.commit()
    conn.close()
    print("✅ データベース初期化完了")

def add_gratitude(date, item, category=None, notes=None):
    """感謝を追加"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO gratitude (date, item, category, notes)
    VALUES (?, ?, ?, ?)
    ''', (date, item, category, notes))

    gratitude_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return gratitude_id

def update_gratitude(gratitude_id, date=None, item=None, category=None, notes=None):
    """感謝を更新"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    updates = []
    params = []

    if date:
        updates.append("date = ?")
        params.append(date)
    if item:
        updates.append("item = ?")
        params.append(item)
    if category:
        updates.append("category = ?")
        params.append(category)
    if notes:
        updates.append("notes = ?")
        params.append(notes)

    if updates:
        query = f"UPDATE gratitude SET {', '.join(updates)} WHERE id = ?"
        params.append(gratitude_id)
        cursor.execute(query, params)
        conn.commit()

    conn.close()

def delete_gratitude(gratitude_id):
    """感謝を削除"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('DELETE FROM gratitude WHERE id = ?', (gratitude_id,))

    conn.commit()
    conn.close()

def list_gratitude(date_from=None, date_to=None, category=None, limit=30):
    """感謝一覧"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    query = '''
    SELECT id, date, item, category, notes, created_at
    FROM gratitude
    '''

    params = []
    conditions = []

    if date_from:
        conditions.append("date >= ?")
        params.append(date_from)
    if date_to:
        conditions.append("date <= ?")
        params.append(date_to)
    if category:
        conditions.append("category = ?")
        params.append(category)

    if conditions:
        query += ' WHERE ' + ' AND '.join(conditions)

    query += ' ORDER BY date DESC, created_at DESC LIMIT ?'
    params.append(limit)

    cursor.execute(query, params)
    gratitude_list = cursor.fetchall()
    conn.close()
    return gratitude_list

def get_by_date(date):
    """日付で感謝取得"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT id, date, item, category, notes, created_at
    FROM gratitude
    WHERE date = ?
    ORDER BY created_at ASC
    ''', (date,))

    gratitude_list = cursor.fetchall()
    conn.close()
    return gratitude_list

def search_gratitude(keyword):
    """感謝を検索"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT id, date, item, category, notes, created_at
    FROM gratitude
    WHERE item LIKE ? OR notes LIKE ? OR category LIKE ?
    ORDER BY date DESC, created_at DESC
    ''', (f'%{keyword}%', f'%{keyword}%', f'%{keyword}%'))

    gratitude_list = cursor.fetchall()
    conn.close()
    return gratitude_list

def get_categories():
    """カテゴリ一覧"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT category, COUNT(*) as count
    FROM gratitude
    WHERE category IS NOT NULL
    GROUP BY category
    ORDER BY count DESC
    ''')

    categories = cursor.fetchall()
    conn.close()
    return categories

def get_stats():
    """統計情報"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    stats = {}

    # 全記録数
    cursor.execute('SELECT COUNT(*) FROM gratitude')
    stats['total'] = cursor.fetchone()[0]

    # 今日
    today = datetime.now().strftime("%Y-%m-%d")
    cursor.execute('SELECT COUNT(*) FROM gratitude WHERE date = ?', (today,))
    stats['today'] = cursor.fetchone()[0]

    # 今月
    current_month = datetime.now().strftime("%Y-%m")
    cursor.execute('SELECT COUNT(*) FROM gratitude WHERE date LIKE ?', (f'{current_month}%',))
    stats['this_month'] = cursor.fetchone()[0]

    # 今週
    from datetime import timedelta
    week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    cursor.execute('SELECT COUNT(*) FROM gratitude WHERE date >= ?', (week_ago,))
    stats['this_week'] = cursor.fetchone()[0]

    # 連続記録日数
    cursor.execute('''
    SELECT COUNT(DISTINCT date) FROM gratitude
    ORDER BY date DESC
    ''')
    total_days = cursor.fetchone()[0]
    stats['total_days'] = total_days

    conn.close()
    return stats

if __name__ == '__main__':
    init_db()
