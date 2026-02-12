#!/usr/bin/env python3
"""
旅行エージェント #30
- 旅行計画管理
- 目的地・日程・予算・宿泊先
"""

import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / "travels.db"

def init_db():
    """データベース初期化"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 旅行テーブル
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS travels (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        destination TEXT NOT NULL,
        departure_date DATE,
        return_date DATE,
        budget INTEGER,
        accommodation TEXT,
        transportation TEXT,
        notes TEXT,
        status TEXT DEFAULT 'planning' CHECK(status IN ('planning', 'scheduled', 'completed', 'cancelled')),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # 更新トリガー
    cursor.execute('''
    CREATE TRIGGER IF NOT EXISTS update_travels_updated_at
    AFTER UPDATE ON travels
    BEGIN
        UPDATE travels SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
    END
    ''')

    # インデックス
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_travels_status ON travels(status)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_travels_departure ON travels(departure_date)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_travels_destination ON travels(destination)')

    conn.commit()
    conn.close()
    print("✅ データベース初期化完了")

def add_travel(destination, departure_date=None, return_date=None, budget=None, accommodation=None, transportation=None, notes=None):
    """旅行追加"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO travels (destination, departure_date, return_date, budget, accommodation, transportation, notes)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (destination, departure_date, return_date, budget, accommodation, transportation, notes))

    travel_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return travel_id

def update_travel(travel_id, destination=None, departure_date=None, return_date=None, budget=None, accommodation=None, transportation=None, notes=None, status=None):
    """旅行更新"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    updates = []
    params = []

    if destination:
        updates.append("destination = ?")
        params.append(destination)
    if departure_date:
        updates.append("departure_date = ?")
        params.append(departure_date)
    if return_date:
        updates.append("return_date = ?")
        params.append(return_date)
    if budget is not None:
        updates.append("budget = ?")
        params.append(budget)
    if accommodation:
        updates.append("accommodation = ?")
        params.append(accommodation)
    if transportation:
        updates.append("transportation = ?")
        params.append(transportation)
    if notes:
        updates.append("notes = ?")
        params.append(notes)
    if status:
        updates.append("status = ?")
        params.append(status)

    if updates:
        query = f"UPDATE travels SET {', '.join(updates)} WHERE id = ?"
        params.append(travel_id)
        cursor.execute(query, params)
        conn.commit()

    conn.close()

def delete_travel(travel_id):
    """旅行削除"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('DELETE FROM travels WHERE id = ?', (travel_id,))

    conn.commit()
    conn.close()

def list_travels(status=None, limit=20):
    """旅行一覧"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    query = '''
    SELECT id, destination, departure_date, return_date, budget, accommodation, transportation, notes, status, created_at
    FROM travels
    '''

    params = []
    if status:
        query += ' WHERE status = ?'
        params.append(status)

    query += ' ORDER BY departure_date DESC, created_at DESC LIMIT ?'
    params.append(limit)

    cursor.execute(query, params)
    travels = cursor.fetchall()
    conn.close()
    return travels

def search_travels(keyword):
    """旅行検索"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT id, destination, departure_date, return_date, budget, accommodation, transportation, notes, status, created_at
    FROM travels
    WHERE destination LIKE ? OR accommodation LIKE ? OR notes LIKE ?
    ORDER BY departure_date DESC, created_at DESC
    ''', (f'%{keyword}%', f'%{keyword}%', f'%{keyword}%'))

    travels = cursor.fetchall()
    conn.close()
    return travels

def get_travel(travel_id):
    """旅行詳細取得"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT id, destination, departure_date, return_date, budget, accommodation, transportation, notes, status, created_at
    FROM travels
    WHERE id = ?
    ''', (travel_id,))

    travel = cursor.fetchone()
    conn.close()
    return travel

def get_stats():
    """統計情報"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    stats = {}

    # 全旅行数
    cursor.execute('SELECT COUNT(*) FROM travels WHERE status != "cancelled"')
    stats['total'] = cursor.fetchone()[0]

    # 計画中
    cursor.execute('SELECT COUNT(*) FROM travels WHERE status = "planning"')
    stats['planning'] = cursor.fetchone()[0]

    # 予定済み
    cursor.execute('SELECT COUNT(*) FROM travels WHERE status = "scheduled"')
    stats['scheduled'] = cursor.fetchone()[0]

    # 完了
    cursor.execute('SELECT COUNT(*) FROM travels WHERE status = "completed"')
    stats['completed'] = cursor.fetchone()[0]

    conn.close()
    return stats

if __name__ == '__main__':
    init_db()
