#!/usr/bin/env python3
"""
アチーブメントエージェント #45
- 実績・達成記録
- タイトル・日付・カテゴリ・説明・メモ
"""

import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / "achievement.db"

def init_db():
    """データベース初期化"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 実績テーブル
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS achievements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        date DATE NOT NULL,
        category TEXT,
        description TEXT,
        notes TEXT,
        status TEXT DEFAULT 'completed' CHECK(status IN ('completed','progress','planned')),
        priority INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # インデックス
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_achievements_date ON achievements(date)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_achievements_category ON achievements(category)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_achievements_status ON achievements(status)')

    conn.commit()
    conn.close()
    print("✅ データベース初期化完了")

def add_achievement(title, date=None, category=None, description=None, notes=None, status='completed', priority=0):
    """実績を追加"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")

    cursor.execute('''
    INSERT INTO achievements (title, date, category, description, notes, status, priority)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (title, date, category, description, notes, status, priority))

    achievement_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return achievement_id

def update_achievement(achievement_id, title=None, date=None, category=None, description=None,
                      notes=None, status=None, priority=None):
    """実績を更新"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    updates = []
    params = []

    if title:
        updates.append("title = ?")
        params.append(title)
    if date:
        updates.append("date = ?")
        params.append(date)
    if category:
        updates.append("category = ?")
        params.append(category)
    if description:
        updates.append("description = ?")
        params.append(description)
    if notes:
        updates.append("notes = ?")
        params.append(notes)
    if status:
        updates.append("status = ?")
        params.append(status)
    if priority is not None:
        updates.append("priority = ?")
        params.append(priority)

    if updates:
        query = f"UPDATE achievements SET {', '.join(updates)} WHERE id = ?"
        params.append(achievement_id)
        cursor.execute(query, params)
        conn.commit()

    conn.close()

def delete_achievement(achievement_id):
    """実績を削除"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('DELETE FROM achievements WHERE id = ?', (achievement_id,))

    conn.commit()
    conn.close()

def list_achievements(date_from=None, date_to=None, category=None, status=None, limit=20):
    """実績一覧"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    query = '''
    SELECT id, title, date, category, description, notes, status, priority, created_at
    FROM achievements
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
    if status:
        conditions.append("status = ?")
        params.append(status)

    if conditions:
        query += ' WHERE ' + ' AND '.join(conditions)

    query += ' ORDER BY date DESC, priority DESC LIMIT ?'
    params.append(limit)

    cursor.execute(query, params)
    achievements = cursor.fetchall()
    conn.close()
    return achievements

def get_by_date(date):
    """日付で実績取得"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT id, title, date, category, description, notes, status, priority, created_at
    FROM achievements
    WHERE date = ?
    ORDER BY priority DESC, created_at ASC
    ''', (date,))

    achievements = cursor.fetchall()
    conn.close()
    return achievements

def search_achievements(keyword):
    """実績を検索"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT id, title, date, category, description, notes, status, priority, created_at
    FROM achievements
    WHERE title LIKE ? OR description LIKE ? OR notes LIKE ? OR category LIKE ?
    ORDER BY date DESC, priority DESC
    ''', (f'%{keyword}%', f'%{keyword}%', f'%{keyword}%', f'%{keyword}%'))

    achievements = cursor.fetchall()
    conn.close()
    return achievements

def get_categories():
    """カテゴリ一覧"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT category, COUNT(*) as count
    FROM achievements
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

    # 全実績数
    cursor.execute('SELECT COUNT(*) FROM achievements')
    stats['total'] = cursor.fetchone()[0]

    # ステータス別
    cursor.execute('SELECT status, COUNT(*) FROM achievements GROUP BY status')
    status_counts = {}
    for row in cursor.fetchall():
        status_counts[row[0]] = row[1]
    stats['by_status'] = status_counts

    # 今日
    today = datetime.now().strftime("%Y-%m-%d")
    cursor.execute('SELECT COUNT(*) FROM achievements WHERE date = ?', (today,))
    stats['today'] = cursor.fetchone()[0]

    # 今月
    current_month = datetime.now().strftime("%Y-%m")
    cursor.execute('SELECT COUNT(*) FROM achievements WHERE date LIKE ?', (f'{current_month}%',))
    stats['this_month'] = cursor.fetchone()[0]

    # 今年
    current_year = datetime.now().strftime("%Y")
    cursor.execute('SELECT COUNT(*) FROM achievements WHERE date LIKE ?', (f'{current_year}%',))
    stats['this_year'] = cursor.fetchone()[0]

    conn.close()
    return stats

if __name__ == '__main__':
    init_db()
