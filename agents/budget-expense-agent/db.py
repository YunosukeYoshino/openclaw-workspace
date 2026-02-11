#!/usr/bin/env python3
"""
予算・支出管理エージェント #52
- 予算カテゴリ・支出記録
- 月次目標・サマリー・支出傾向分析
"""

import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / "budget.db"

def init_db():
    """データベース初期化"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 予算カテゴリーテーブル
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS budget_categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        monthly_limit INTEGER,
        description TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # 支出テーブル
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category_id INTEGER,
        amount INTEGER NOT NULL,
        description TEXT,
        date DATE NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (category_id) REFERENCES budget_categories(id) ON DELETE SET NULL
    )
    ''')

    # インデックス
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_expenses_category ON expenses(category_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_expenses_date ON expenses(date)')

    conn.commit()
    conn.close()
    print("✅ データベース初期化完了")

def add_category(name, monthly_limit=None, description=None):
    """カテゴリー追加"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO budget_categories (name, monthly_limit, description)
    VALUES (?, ?, ?)
    ''', (name, monthly_limit, description))

    category_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return category_id

def add_expense(category_id, amount, description=None, date=None):
    """支出追加"""
    if not date:
        date = datetime.now().strftime("%Y-%m-%d")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO expenses (category_id, amount, description, date)
    VALUES (?, ?, ?, ?)
    ''', (category_id, amount, description, date))

    expense_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return expense_id

def get_monthly_spending(category_id, year=None, month=None):
    """月次支出を取得"""
    if not year:
        year = datetime.now().year
    if not month:
        month = datetime.now().month

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT COALESCE(SUM(amount), 0) as total
    FROM expenses
    WHERE category_id = ? AND strftime('%Y', date) = ? AND strftime('%m', date) = ?
    ''', (category_id, str(year), str(month).zfill(2)))

    result = cursor.fetchone()
    conn.close()

    return result[0] if result else 0

def get_spending_trend(category_id, months=6):
    """支出傾向を取得"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT strftime('%Y-%m', date) as month, SUM(amount) as total
    FROM expenses
    WHERE category_id = ?
    GROUP BY month
    ORDER BY month DESC
    LIMIT ?
    ''', (category_id, months))

    results = cursor.fetchall()
    conn.close()

    return results

def list_categories():
    """カテゴリー一覧"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT id, name, monthly_limit, description, created_at
    FROM budget_categories
    ORDER BY name
    ''')

    categories = cursor.fetchall()
    conn.close()
    return categories

def list_expenses(category_id=None, date_from=None, date_to=None, limit=20):
    """支出一覧"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    query = '''
    SELECT e.id, e.category_id, e.amount, e.description, e.date, e.created_at,
           c.name as category_name
    FROM expenses e
    LEFT JOIN budget_categories c ON e.category_id = c.id
    '''

    params = []
    conditions = []

    if category_id:
        conditions.append("e.category_id = ?")
        params.append(category_id)
    if date_from:
        conditions.append("e.date >= ?")
        params.append(date_from)
    if date_to:
        conditions.append("e.date <= ?")
        params.append(date_to)

    if conditions:
        query += ' WHERE ' + ' AND '.join(conditions)

    query += ' ORDER BY e.date DESC LIMIT ?'
    params.append(limit)

    cursor.execute(query, params)
    expenses = cursor.fetchall()
    conn.close()
    return expenses

if __name__ == '__main__':
    init_db()
