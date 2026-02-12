#!/usr/bin/env python3
"""
貯金管理エージェント #54
- 目標設定・入出金記録
- 進捗・利率・定期積立
"""

import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / "savings.db"

def init_db():
    """データベース初期化"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 貯金目標テーブル
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS goals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        target_amount INTEGER NOT NULL,
        current_amount INTEGER DEFAULT 0,
        target_date DATE,
        interest_rate REAL,
        description TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # 入出金記録テーブル
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        goal_id INTEGER,
        type TEXT NOT NULL CHECK(type IN ('deposit', 'withdrawal')),
        amount INTEGER NOT NULL,
        date DATE NOT NULL,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (goal_id) REFERENCES goals(id) ON DELETE SET NULL
    )
    ''')

    # 定期積立テーブル
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS scheduled_deposits (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        goal_id INTEGER NOT NULL,
        amount INTEGER NOT NULL,
        frequency TEXT CHECK(frequency IN ('daily', 'weekly', 'biweekly', 'monthly', 'yearly')),
        next_date DATE NOT NULL,
        active BOOLEAN DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (goal_id) REFERENCES goals(id) ON DELETE CASCADE
    )
    ''')

    # 更新トリガー
    cursor.execute('''
    CREATE TRIGGER IF NOT EXISTS update_goals_updated_at
    AFTER UPDATE ON goals
    BEGIN
        UPDATE goals SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
    END
    ''')

    # インデックス
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_transactions_goal_id ON transactions(goal_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(date)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_scheduled_deposits_goal_id ON scheduled_deposits(goal_id)')

    conn.commit()
    conn.close()
    print("✅ データベース初期化完了")

def add_goal(name, target_amount, target_date=None, interest_rate=None, description=None):
    """目標追加"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO goals (name, target_amount, target_date, interest_rate, description)
    VALUES (?, ?, ?, ?, ?)
    ''', (name, target_amount, target_date, interest_rate, description))

    goal_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return goal_id

def add_transaction(goal_id, type, amount, date=None, notes=None):
    """入出金追加"""
    if not date:
        date = datetime.now().strftime("%Y-%m-%d")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO transactions (goal_id, type, amount, date, notes)
    VALUES (?, ?, ?, ?, ?)
    ''', (goal_id, type, amount, date, notes))

    # 目標の現在額を更新
    if goal_id:
        if type == 'deposit':
            cursor.execute('''
            UPDATE goals
            SET current_amount = current_amount + ?
            WHERE id = ?
            ''', (amount, goal_id))
        elif type == 'withdrawal':
            cursor.execute('''
            UPDATE goals
            SET current_amount = current_amount - ?
            WHERE id = ?
            ''', (amount, goal_id))

    transaction_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return transaction_id

def add_scheduled_deposit(goal_id, amount, frequency, next_date):
    """定期積立追加"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO scheduled_deposits (goal_id, amount, frequency, next_date)
    VALUES (?, ?, ?, ?)
    ''', (goal_id, amount, frequency, next_date))

    deposit_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return deposit_id

def get_progress(goal_id):
    """進捗を取得"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT target_amount, current_amount, target_date
    FROM goals
    WHERE id = ?
    ''', (goal_id,))

    result = cursor.fetchone()
    conn.close()

    if not result:
        return None

    target_amount, current_amount, target_date = result
    progress_pct = (current_amount / target_amount) * 100 if target_amount > 0 else 0

    return {
        'target_amount': target_amount,
        'current_amount': current_amount,
        'progress_pct': progress_pct,
        'remaining': target_amount - current_amount
    }

def list_goals():
    """目標一覧"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT id, name, target_amount, current_amount, target_date, interest_rate, description, created_at
    FROM goals
    ORDER BY created_at DESC
    ''')

    goals = cursor.fetchall()
    conn.close()
    return goals

def list_transactions(goal_id, limit=20):
    """入出金一覧"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT id, goal_id, type, amount, date, notes, created_at
    FROM transactions
    WHERE goal_id = ?
    ORDER BY date DESC
    LIMIT ?
    ''', (goal_id, limit))

    transactions = cursor.fetchall()
    conn.close()
    return transactions

if __name__ == '__main__':
    init_db()
