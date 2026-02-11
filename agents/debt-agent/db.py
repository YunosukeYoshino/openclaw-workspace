#!/usr/bin/env python3
"""
借金管理エージェント #55
- 借入先・金額・金利・支払い記録
- 返済予定・返済プラン
"""

import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / "debt.db"

def init_db():
    """データベース初期化"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 借金テーブル
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS debts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        lender TEXT,
        principal_amount REAL NOT NULL,
        interest_rate REAL,
        interest_type TEXT CHECK(interest_type IN ('fixed', 'variable')),
        due_date DATE,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # 支払い記録テーブル
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS payments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        debt_id INTEGER NOT NULL,
        amount REAL NOT NULL,
        payment_date DATE NOT NULL,
        type TEXT CHECK(type IN ('principal', 'interest')),
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (debt_id) REFERENCES debts(id) ON DELETE CASCADE
    )
    ''')

    # 返済プランテーブル
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS repayment_plans (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        debt_id INTEGER NOT NULL,
        monthly_payment REAL,
        start_date DATE NOT NULL,
        end_date DATE,
        status TEXT DEFAULT 'active' CHECK(status IN ('active', 'completed', 'cancelled')),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (debt_id) REFERENCES debts(id) ON DELETE CASCADE
    )
    ''')

    # 更新トリガー
    cursor.execute('''
    CREATE TRIGGER IF NOT EXISTS update_debts_updated_at
    AFTER UPDATE ON debts
    BEGIN
        UPDATE debts SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
    END
    ''')

    # インデックス
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_payments_debt_id ON payments(debt_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_payments_date ON payments(payment_date)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_repayment_plans_debt_id ON repayment_plans(debt_id)')

    conn.commit()
    conn.close()
    print("✅ データベース初期化完了")

def add_debt(name, lender=None, principal_amount=None, interest_rate=None, interest_type='fixed', due_date=None, notes=None):
    """借金追加"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO debts (name, lender, principal_amount, interest_rate, interest_type, due_date, notes)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (name, lender, principal_amount, interest_rate, interest_type, due_date, notes))

    debt_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return debt_id

def add_payment(debt_id, amount, payment_date=None, type='principal', notes=None):
    """支払い追加"""
    if not payment_date:
        payment_date = datetime.now().strftime("%Y-%m-%d")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO payments (debt_id, amount, payment_date, type, notes)
    VALUES (?, ?, ?, ?, ?)
    ''', (debt_id, amount, payment_date, type, notes))

    payment_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return payment_id

def add_repayment_plan(debt_id, monthly_payment, start_date, end_date):
    """返済プラン追加"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO repayment_plans (debt_id, monthly_payment, start_date, end_date)
    VALUES (?, ?, ?, ?)
    ''', (debt_id, monthly_payment, start_date, end_date))

    plan_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return plan_id

def get_balance(debt_id):
    """残高を取得"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 元本
    cursor.execute('''
    SELECT principal_amount
    FROM debts
    WHERE id = ?
    ''', (debt_id,))

    result = cursor.fetchone()
    if not result:
        return None

    principal = result[0]

    # 支払い合計
    cursor.execute('''
    SELECT COALESCE(SUM(amount), 0)
    FROM payments
    WHERE debt_id = ? AND type = 'principal'
    ''', (debt_id,))

    paid = cursor.fetchone()[0]

    conn.close()

    return principal - paid

def get_payment_summary(debt_id):
    """支払いサマリーを取得"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT type, SUM(amount) as total, COUNT(*) as count
    FROM payments
    WHERE debt_id = ?
    GROUP BY type
    ''', (debt_id,))

    results = cursor.fetchall()
    conn.close()

    summary = {'principal': 0, 'interest': 0, 'total': 0, 'count': 0}

    for type, total, count in results:
        summary[type] = total
        summary['total'] += total
        summary['count'] += count

    return summary

def list_debts():
    """借金一覧"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT id, name, lender, principal_amount, interest_rate, interest_type, due_date, notes, created_at
    FROM debts
    ORDER BY created_at DESC
    ''')

    debts = cursor.fetchall()
    conn.close()
    return debts

def list_payments(debt_id, limit=20):
    """支払い一覧"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT id, debt_id, amount, payment_date, type, notes, created_at
    FROM payments
    WHERE debt_id = ?
    ORDER BY payment_date DESC
    LIMIT ?
    ''', (debt_id, limit))

    payments = cursor.fetchall()
    conn.close()
    return payments

if __name__ == '__main__':
    init_db()
