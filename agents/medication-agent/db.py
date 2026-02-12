#!/usr/bin/env python3
"""
薬服用エージェント #49
- 薬・用量・時間
- 頻度・メモ
"""

import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / "medication.db"

def init_db():
    """データベース初期化"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 薬テーブル
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS medications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        dosage REAL,
        unit TEXT DEFAULT 'mg',
        frequency TEXT,
        time_taken TIME,
        date DATE NOT NULL,
        notes TEXT,
        prescribed_by TEXT,
        reason TEXT,
        taken BOOLEAN DEFAULT 0,
        skipped BOOLEAN DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # インデックス
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_medications_date ON medications(date)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_medications_name ON medications(name)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_medications_taken ON medications(taken)')

    conn.commit()
    conn.close()
    print("✅ データベース初期化完了")

def add_medication(name, dosage=None, unit='mg', frequency=None, time_taken=None,
                   date=None, notes=None, prescribed_by=None, reason=None, taken=True):
    """薬を追加"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")

    if time_taken is None:
        time_taken = datetime.now().strftime("%H:%M")

    cursor.execute('''
    INSERT INTO medications (name, dosage, unit, frequency, time_taken, date, notes, prescribed_by, reason, taken)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (name, dosage, unit, frequency, time_taken, date, notes, prescribed_by, reason, taken))

    med_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return med_id

def update_medication(med_id, name=None, dosage=None, unit=None, frequency=None,
                      time_taken=None, date=None, notes=None, prescribed_by=None,
                      reason=None, taken=None, skipped=None):
    """薬を更新"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    updates = []
    params = []

    if name:
        updates.append("name = ?")
        params.append(name)
    if dosage is not None:
        updates.append("dosage = ?")
        params.append(dosage)
    if unit:
        updates.append("unit = ?")
        params.append(unit)
    if frequency:
        updates.append("frequency = ?")
        params.append(frequency)
    if time_taken:
        updates.append("time_taken = ?")
        params.append(time_taken)
    if date:
        updates.append("date = ?")
        params.append(date)
    if notes:
        updates.append("notes = ?")
        params.append(notes)
    if prescribed_by:
        updates.append("prescribed_by = ?")
        params.append(prescribed_by)
    if reason:
        updates.append("reason = ?")
        params.append(reason)
    if taken is not None:
        updates.append("taken = ?")
        params.append(taken)
    if skipped is not None:
        updates.append("skipped = ?")
        params.append(skipped)

    if updates:
        query = f"UPDATE medications SET {', '.join(updates)} WHERE id = ?"
        params.append(med_id)
        cursor.execute(query, params)
        conn.commit()

    conn.close()

def delete_medication(med_id):
    """薬を削除"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('DELETE FROM medications WHERE id = ?', (med_id,))

    conn.commit()
    conn.close()

def mark_taken(med_id, taken=True):
    """服用済みにマーク"""
    update_medication(med_id, taken=taken)

def mark_skipped(med_id):
    """スキップにマーク"""
    update_medication(med_id, skipped=True, taken=False)

def list_medications(date=None, name=None, taken=None, limit=30):
    """薬一覧"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    query = '''
    SELECT id, name, dosage, unit, frequency, time_taken, date, notes, prescribed_by, reason, taken, skipped, created_at
    FROM medications
    '''

    params = []
    conditions = []

    if date:
        conditions.append("date = ?")
        params.append(date)
    if name:
        conditions.append("name = ?")
        params.append(name)
    if taken is not None:
        conditions.append("taken = ?")
        params.append(taken)

    if conditions:
        query += ' WHERE ' + ' AND '.join(conditions)

    query += ' ORDER BY date DESC, time_taken ASC LIMIT ?'
    params.append(limit)

    cursor.execute(query, params)
    medications = cursor.fetchall()
    conn.close()
    return medications

def get_by_date(date):
    """日付で薬取得"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT id, name, dosage, unit, frequency, time_taken, date, notes, prescribed_by, reason, taken, skipped, created_at
    FROM medications
    WHERE date = ?
    ORDER BY time_taken ASC
    ''', (date,))

    medications = cursor.fetchall()
    conn.close()
    return medications

def search_medications(keyword):
    """薬を検索"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT id, name, dosage, unit, frequency, time_taken, date, notes, prescribed_by, reason, taken, skipped, created_at
    FROM medications
    WHERE name LIKE ? OR notes LIKE ? OR reason LIKE ? OR prescribed_by LIKE ?
    ORDER BY date DESC, time_taken ASC
    ''', (f'%{keyword}%', f'%{keyword}%', f'%{keyword}%', f'%{keyword}%'))

    medications = cursor.fetchall()
    conn.close()
    return medications

def get_medication_names():
    """薬の名前一覧"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT name, COUNT(*) as count, AVG(dosage) as avg_dosage
    FROM medications
    GROUP BY name
    ORDER BY count DESC
    ''')

    names = cursor.fetchall()
    conn.close()
    return names

def get_stats(date_from=None, date_to=None):
    """統計情報"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    stats = {}

    query = 'SELECT COUNT(*) FROM medications'
    params = []
    conditions = []

    if date_from:
        conditions.append("date >= ?")
        params.append(date_from)
    if date_to:
        conditions.append("date <= ?")
        params.append(date_to)

    if conditions:
        query += ' WHERE ' + ' AND '.join(conditions)

    cursor.execute(query, params)
    stats['total_records'] = cursor.fetchone()[0]

    # 服用済み
    query = 'SELECT COUNT(*) FROM medications WHERE taken = 1'
    params = []
    conditions = []

    if date_from:
        conditions.append("date >= ?")
        params.append(date_from)
    if date_to:
        conditions.append("date <= ?")
        params.append(date_to)

    if conditions:
        query += ' AND ' + ' AND '.join(conditions)

    cursor.execute(query, params)
    stats['taken'] = cursor.fetchone()[0]

    # スキップ
    query = 'SELECT COUNT(*) FROM medications WHERE skipped = 1'
    params = []
    conditions = []

    if date_from:
        conditions.append("date >= ?")
        params.append(date_from)
    if date_to:
        conditions.append("date <= ?")
        params.append(date_to)

    if conditions:
        query += ' AND ' + ' AND '.join(conditions)

    cursor.execute(query, params)
    stats['skipped'] = cursor.fetchone()[0]

    # 今日
    today = datetime.now().strftime("%Y-%m-%d")
    cursor.execute('SELECT COUNT(*), SUM(CASE WHEN taken = 1 THEN 1 ELSE 0 END), SUM(CASE WHEN skipped = 1 THEN 1 ELSE 0 END) FROM medications WHERE date = ?', (today,))
    today_stats = cursor.fetchone()
    stats['today_total'] = today_stats[0]
    stats['today_taken'] = today_stats[1]
    stats['today_skipped'] = today_stats[2]

    # 服用率
    if stats['taken'] + stats['skipped'] > 0:
        stats['adherence'] = (stats['taken'] / (stats['taken'] + stats['skipped'])) * 100
    else:
        stats['adherence'] = 100

    # 一意な薬の数
    cursor.execute('SELECT COUNT(DISTINCT name) FROM medications')
    stats['unique_medications'] = cursor.fetchone()[0]

    conn.close()
    return stats

if __name__ == '__main__':
    init_db()
