#!/usr/bin/env python3
"""
予算管理エージェント #19
- 予算の設定と追跡
- 支出の記録
- 統計機能
"""

import sqlite3
from pathlib import Path
from datetime import datetime, timedelta

DB_PATH = Path(__file__).parent / "budget.db"

def init_db():
    """データベース初期化"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 予算テーブル
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS budgets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT NOT NULL,
        amount REAL NOT NULL,
        currency TEXT DEFAULT 'JPY',
        start_date DATE NOT NULL,
        end_date DATE NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # 支出テーブル
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        budget_id INTEGER,
        category TEXT NOT NULL,
        amount REAL NOT NULL,
        description TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (budget_id) REFERENCES budgets(id) ON DELETE CASCADE
    )
    ''')

    # インデックス
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_budgets_category ON budgets(category)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_budgets_dates ON budgets(start_date, end_date)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_expenses_category ON expenses(category)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_expenses_created ON expenses(created_at)')

    conn.commit()
    conn.close()
    print("✅ データベース初期化完了")

def add_budget(category, amount, start_date, end_date):
    """予算追加"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO budgets (category, amount, start_date, end_date)
    VALUES (?, ?, ?, ?)
    ''', (category, amount, start_date, end_date))

    budget_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return budget_id

def add_expense(category, amount, description=None):
    """支出追加"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO expenses (category, amount, description)
    VALUES (?, ?, ?)
    ''', (category, amount, description))

    expense_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return expense_id

def get_budget_status(budget_id):
    """予算状況取得"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 予算取得
    cursor.execute('''
    SELECT category, amount, start_date, end_date
    FROM budgets
    WHERE id = ?
    ''', (budget_id,))
    budget = cursor.fetchone()

    if not budget:
        return None

    category, budget_amount, start_date, end_date = budget

    # 支出合計
    cursor.execute('''
    SELECT SUM(amount) as total
    FROM expenses
    WHERE category = ? AND created_at >= ? AND created_at <= ?
    ''', (category, start_date, end_date))

    result = cursor.fetchone()
    total_spent = result[0] or 0

    conn.close()

    remaining = budget_amount - total_spent
    over_budget = total_spent > budget_amount

    return {
        'category': category,
        'budget': budget_amount,
        'spent': total_spent,
        'remaining': remaining,
        'over_budget': over_budget,
        'start_date': start_date,
        'end_date': end_date
    }

def list_budgets():
    """予算一覧"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT id, category, amount, start_date, end_date
    FROM budgets
    ORDER BY end_date DESC
    ''')

    budgets = cursor.fetchall()
    conn.close()
    return budgets

if __name__ == '__main__':
    init_db()
