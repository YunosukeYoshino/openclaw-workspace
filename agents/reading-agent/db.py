#!/usr/bin/env python3
"""
リーディングエージェント #41
- 読書記録
- 書名・著者・ページ数・評価・メモ・読了日
"""

import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / "reading.db"

def init_db():
    """データベース初期化"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 本テーブル
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS books (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        author TEXT,
        isbn TEXT,
        pages INTEGER,
        rating INTEGER CHECK(rating >= 1 AND rating <= 5),
        status TEXT DEFAULT 'reading' CHECK(status IN ('reading','completed','abandoned')),
        start_date DATE,
        finish_date DATE,
        notes TEXT,
        tags TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # ページ進捗テーブル
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS progress (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        book_id INTEGER NOT NULL,
        page INTEGER,
        note TEXT,
        recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE
    )
    ''')

    # インデックス
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_books_status ON books(status)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_books_rating ON books(rating)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_progress_book ON progress(book_id)')

    conn.commit()
    conn.close()
    print("✅ データベース初期化完了")

def add_book(title, author=None, isbn=None, pages=None, status='reading', start_date=None, notes=None, tags=None):
    """本を追加"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    if start_date is None:
        start_date = datetime.now().strftime("%Y-%m-%d")

    cursor.execute('''
    INSERT INTO books (title, author, isbn, pages, status, start_date, notes, tags)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (title, author, isbn, pages, status, start_date, notes, tags))

    book_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return book_id

def update_book(book_id, title=None, author=None, isbn=None, pages=None, rating=None, status=None,
                start_date=None, finish_date=None, notes=None, tags=None):
    """本を更新"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    updates = []
    params = []

    if title:
        updates.append("title = ?")
        params.append(title)
    if author:
        updates.append("author = ?")
        params.append(author)
    if isbn:
        updates.append("isbn = ?")
        params.append(isbn)
    if pages:
        updates.append("pages = ?")
        params.append(pages)
    if rating:
        updates.append("rating = ?")
        params.append(rating)
    if status:
        updates.append("status = ?")
        params.append(status)
    if start_date:
        updates.append("start_date = ?")
        params.append(start_date)
    if finish_date:
        updates.append("finish_date = ?")
        params.append(finish_date)
    if notes:
        updates.append("notes = ?")
        params.append(notes)
    if tags:
        updates.append("tags = ?")
        params.append(tags)

    updates.append("updated_at = ?")
    params.append(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    if updates:
        query = f"UPDATE books SET {', '.join(updates)} WHERE id = ?"
        params.append(book_id)
        cursor.execute(query, params)
        conn.commit()

    conn.close()

def delete_book(book_id):
    """本を削除"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('DELETE FROM books WHERE id = ?', (book_id,))
    conn.commit()
    conn.close()

def add_progress(book_id, page=None, note=None):
    """進捗を追加"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO progress (book_id, page, note)
    VALUES (?, ?, ?)
    ''', (book_id, page, note))

    progress_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return progress_id

def list_books(status=None, rating=None, limit=20):
    """本一覧"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    query = '''
    SELECT id, title, author, isbn, pages, rating, status, start_date, finish_date, notes, tags, created_at
    FROM books
    '''

    params = []
    conditions = []

    if status:
        conditions.append("status = ?")
        params.append(status)
    if rating:
        conditions.append("rating >= ?")
        params.append(rating)

    if conditions:
        query += ' WHERE ' + ' AND '.join(conditions)

    query += ' ORDER BY created_at DESC LIMIT ?'
    params.append(limit)

    cursor.execute(query, params)
    books = cursor.fetchall()
    conn.close()
    return books

def search_books(keyword):
    """本を検索"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT id, title, author, isbn, pages, rating, status, start_date, finish_date, notes, tags, created_at
    FROM books
    WHERE title LIKE ? OR author LIKE ? OR notes LIKE ? OR tags LIKE ?
    ORDER BY created_at DESC
    ''', (f'%{keyword}%', f'%{keyword}%', f'%{keyword}%', f'%{keyword}%'))

    books = cursor.fetchall()
    conn.close()
    return books

def get_book(book_id):
    """本を取得"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT id, title, author, isbn, pages, rating, status, start_date, finish_date, notes, tags, created_at
    FROM books
    WHERE id = ?
    ''', (book_id,))

    book = cursor.fetchone()
    conn.close()
    return book

def get_progress(book_id):
    """進捗を取得"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT id, page, note, recorded_at
    FROM progress
    WHERE book_id = ?
    ORDER BY recorded_at DESC
    ''', (book_id,))

    progress = cursor.fetchall()
    conn.close()
    return progress

def get_stats():
    """統計情報"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    stats = {}

    # 全本数
    cursor.execute('SELECT COUNT(*) FROM books')
    stats['total'] = cursor.fetchone()[0]

    # ステータス別
    cursor.execute('SELECT status, COUNT(*) FROM books GROUP BY status')
    status_counts = {}
    for row in cursor.fetchall():
        status_counts[row[0]] = row[1]
    stats['by_status'] = status_counts

    # 今月読了
    current_month = datetime.now().strftime("%Y-%m")
    cursor.execute('SELECT COUNT(*) FROM books WHERE finish_date LIKE ? AND status = ?', (f'{current_month}%', 'completed'))
    stats['completed_this_month'] = cursor.fetchone()[0]

    # 平均評価
    cursor.execute('SELECT AVG(rating) FROM books WHERE rating IS NOT NULL')
    avg_rating = cursor.fetchone()[0]
    stats['avg_rating'] = round(avg_rating, 1) if avg_rating else None

    # 総ページ数
    cursor.execute('SELECT SUM(pages) FROM books WHERE pages IS NOT NULL')
    total_pages = cursor.fetchone()[0]
    stats['total_pages'] = total_pages if total_pages else 0

    conn.close()
    return stats

if __name__ == '__main__':
    init_db()
