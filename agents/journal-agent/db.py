#!/usr/bin/env python3
"""
日記エージェント #33
- 日記・メモ記録
- 日付・タイトル・内容・気分・タグ
"""

import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / "journal.db"

def init_db():
    """データベース初期化"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 日記テーブル
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS journal (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date DATE NOT NULL,
        title TEXT,
        content TEXT,
        mood TEXT CHECK(mood IN ('happy', 'sad', 'neutral', 'excited', 'calm', 'angry', 'anxious', 'tired')),
        weather TEXT,
        tags TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # 更新トリガー
    cursor.execute('''
    CREATE TRIGGER IF NOT EXISTS update_journal_updated_at
    AFTER UPDATE ON journal
    BEGIN
        UPDATE journal SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
    END
    ''')

    # インデックス
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_journal_date ON journal(date)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_journal_mood ON journal(mood)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_journal_tags ON journal(tags)')

    conn.commit()
    conn.close()
    print("✅ データベース初期化完了")

def add_journal(date, title=None, content=None, mood=None, weather=None, tags=None):
    """日記追加"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO journal (date, title, content, mood, weather, tags)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', (date, title, content, mood, weather, tags))

    journal_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return journal_id

def update_journal(journal_id, date=None, title=None, content=None, mood=None, weather=None, tags=None):
    """日記更新"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    updates = []
    params = []

    if date:
        updates.append("date = ?")
        params.append(date)
    if title:
        updates.append("title = ?")
        params.append(title)
    if content:
        updates.append("content = ?")
        params.append(content)
    if mood:
        updates.append("mood = ?")
        params.append(mood)
    if weather:
        updates.append("weather = ?")
        params.append(weather)
    if tags:
        updates.append("tags = ?")
        params.append(tags)

    if updates:
        query = f"UPDATE journal SET {', '.join(updates)} WHERE id = ?"
        params.append(journal_id)
        cursor.execute(query, params)
        conn.commit()

    conn.close()

def delete_journal(journal_id):
    """日記削除"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('DELETE FROM journal WHERE id = ?', (journal_id,))

    conn.commit()
    conn.close()

def list_journals(date_from=None, date_to=None, mood=None, limit=20):
    """日記一覧"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    query = '''
    SELECT id, date, title, content, mood, weather, tags, created_at
    FROM journal
    '''

    params = []
    conditions = []

    if date_from:
        conditions.append("date >= ?")
        params.append(date_from)
    if date_to:
        conditions.append("date <= ?")
        params.append(date_to)
    if mood:
        conditions.append("mood = ?")
        params.append(mood)

    if conditions:
        query += ' WHERE ' + ' AND '.join(conditions)

    query += ' ORDER BY date DESC, created_at DESC LIMIT ?'
    params.append(limit)

    cursor.execute(query, params)
    journals = cursor.fetchall()
    conn.close()
    return journals

def search_journals(keyword):
    """日記検索"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT id, date, title, content, mood, weather, tags, created_at
    FROM journal
    WHERE title LIKE ? OR content LIKE ? OR tags LIKE ?
    ORDER BY date DESC, created_at DESC
    ''', (f'%{keyword}%', f'%{keyword}%', f'%{keyword}%'))

    journals = cursor.fetchall()
    conn.close()
    return journals

def get_journal(journal_id):
    """日記詳細取得"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT id, date, title, content, mood, weather, tags, created_at
    FROM journal
    WHERE id = ?
    ''', (journal_id,))

    journal = cursor.fetchone()
    conn.close()
    return journal

def get_by_date(date):
    """日付で日記取得"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT id, date, title, content, mood, weather, tags, created_at
    FROM journal
    WHERE date = ?
    ORDER BY created_at DESC
    ''', (date,))

    journals = cursor.fetchall()
    conn.close()
    return journals

def get_stats():
    """統計情報"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    stats = {}

    # 全日記数
    cursor.execute('SELECT COUNT(*) FROM journal')
    stats['total'] = cursor.fetchone()[0]

    # 今日
    today = datetime.now().strftime("%Y-%m-%d")
    cursor.execute('SELECT COUNT(*) FROM journal WHERE date = ?', (today,))
    stats['today'] = cursor.fetchone()[0]

    # 今月
    current_month = datetime.now().strftime("%Y-%m")
    cursor.execute('SELECT COUNT(*) FROM journal WHERE date LIKE ?', (f'{current_month}%',))
    stats['this_month'] = cursor.fetchone()[0]

    # 気分分布
    cursor.execute('''
    SELECT mood, COUNT(*) as count
    FROM journal
    WHERE mood IS NOT NULL
    GROUP BY mood
    ORDER BY count DESC
    ''')
    stats['mood_distribution'] = cursor.fetchall()

    conn.close()
    return stats

if __name__ == '__main__':
    init_db()
