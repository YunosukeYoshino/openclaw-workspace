#!/usr/bin/env python3
"""
ファイナンスエージェント #38
- 金融記録管理
- 収支・予算・投資・タグ
"""

import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / "finance.db"

def init_db():
    """データベース初期化"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 取引テーブル
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date DATE NOT NULL,
        type TEXT NOT NULL CHECK(type IN ('income', 'expense', 'transfer')),
        category TEXT,
        amount INTEGER NOT NULL,
        description TEXT,
        tags TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # 予算テーブル
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS budgets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT NOT NULL,
        amount INTEGER NOT NULL,
        period TEXT DEFAULT 'monthly' CHECK(period IN ('daily', 'weekly', 'monthly', 'yearly')),
        start_date DATE,
        end_date DATE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # インデックス
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(date)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_transactions_type ON transactions(type)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_transactions_category ON transactions(category)')

    conn.commit()
    conn.close()
    print("✅ データベース初期化完了")

def add_transaction(date, type, amount, category=None, description=None, tags=None):
    """取引追加"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO transactions (date, type, category, amount, description, tags)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', (date, type, amount, category, description, tags))

    trans_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return trans_id

def update_transaction(trans_id, date=None, type=None, amount=None, category=None, description=None, tags=None):
    """取引更新"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    updates = []
    params = []

    if date:
        updates.append("date = ?")
        params.append(date)
    if type:
        updates.append("type = ?")
        params.append(type)
    if amount is not None:
        updates.append("amount = ?")
        params.append(amount)
    if category:
        updates.append("category = ?")
        params.append(category)
    if description:
        updates.append("description = ?")
        params.append(description)
    if tags:
        updates.append("tags = ?")
        params.append(tags)

    if updates:
        query = f"UPDATE transactions SET {', '.join(updates)} WHERE id = ?"
        params.append(trans_id)
        cursor.execute(query, params)
        conn.commit()

    conn.close()

def delete_transaction(trans_id):
    """取引削除"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('DELETE FROM transactions WHERE id = ?', (trans_id,))

    conn.commit()
    conn.close()

def list_transactions(date_from=None, date_to=None, type=None, category=None, limit=20):
    """取引一覧"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    query = '''
    SELECT id, date, type, category, amount, description, tags, created_at
    FROM transactions
    '''

    params = []
    conditions = []

    if date_from:
        conditions.append("date >= ?")
        params.append(date_from)
    if date_to:
        conditions.append("date <= ?")
        params.append(date_to)
    if type:
        conditions.append("type = ?")
        params.append(type)
    if category:
        conditions.append("category = ?")
        params.append(category)

    if conditions:
        query += ' WHERE ' + ' AND '.join(conditions)

    query += ' ORDER BY date DESC, created_at DESC LIMIT ?'
    params.append(limit)

    cursor.execute(query, params)
    transactions = cursor.fetchall()
    conn.close()
    return transactions

def search_transactions(keyword):
    """取引検索"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT id, date, type, category, amount, description, tags, created_at
    FROM transactions
    WHERE description LIKE ? OR category LIKE ? OR tags LIKE ?
    ORDER BY date DESC, created_at DESC
    ''', (f'%{keyword}%', f'%{keyword}%', f'%{keyword}%'))

    transactions = cursor.fetchall()
    conn.close()
    return transactions

def add_budget(category, amount, period='monthly', start_date=None, end_date=None):
    """予算追加"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO budgets (category, amount, period, start_date, end_date)
    VALUES (?, ?, ?, ?, ?)
    ''', (category, amount, period, start_date, end_date))

    budget_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return budget_id

def list_budgets(limit=20):
    """予算一覧"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT id, category, amount, period, start_date, end_date, created_at
    FROM budgets
    ORDER BY created_at DESC
    LIMIT ?
    ''', (limit,))

    budgets = cursor.fetchall()
    conn.close()
    return budgets

def get_stats():
    """統計情報"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    stats = {}

    # 全取引数
    cursor.execute('SELECT COUNT(*) FROM transactions')
    stats['total_transactions'] = cursor.fetchone()[0]

    # 今月の収入
    current_month = datetime.now().strftime("%Y-%m")
    cursor.execute('SELECT SUM(amount) FROM transactions WHERE date LIKE ? AND type = "income"', (f'{current_month}%',))
    month_income = cursor.fetchone()[0]
    stats['month_income'] = month_income if month_income else 0

    # 今月の支出
    cursor.execute('SELECT SUM(amount) FROM transactions WHERE date LIKE ? AND type = "expense"', (f'{current_month}%',))
    month_expense = cursor.fetchone()[0]
    stats['month_expense'] = month_expense if month_expense else 0

    # 今月の収支
    stats['month_balance'] = stats['month_income'] - stats['month_expense']

    # カテゴリ別支出
    cursor.execute('''
    SELECT category, SUM(amount) as total
    FROM transactions
    WHERE type = "expense" AND date LIKE ?
    GROUP BY category
    ORDER BY total DESC
    ''', (f'{current_month}%',))
    stats['expenses_by_category'] = cursor.fetchall()

    conn.close()
    return stats

if __name__ == '__main__':
    init_db()
