#!/usr/bin/env python3
"""
投資管理エージェント #53
- 株・債券・ポートフォリオ管理
- 買付価格・現在価格・損益
- 配当・再投資
"""

import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / "investments.db"

def init_db():
    """データベース初期化"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 投資テーブル
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS investments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        type TEXT CHECK(type IN ('stock', 'bond', 'etf', 'mutual_fund', 'crypto', 'other')),
        symbol TEXT,
        shares REAL,
        purchase_price REAL,
        current_price REAL,
        currency TEXT DEFAULT 'JPY',
        purchase_date DATE,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # 配当テーブル
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS dividends (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        investment_id INTEGER NOT NULL,
        amount REAL NOT NULL,
        currency TEXT DEFAULT 'JPY',
        payment_date DATE,
        reinvested BOOLEAN DEFAULT 0,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (investment_id) REFERENCES investments(id) ON DELETE CASCADE
    )
    ''')

    # 更新トリガー
    cursor.execute('''
    CREATE TRIGGER IF NOT EXISTS update_investments_updated_at
    AFTER UPDATE ON investments
    BEGIN
        UPDATE investments SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
    END
    ''')

    # インデックス
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_investments_type ON investments(type)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_dividends_investment_id ON dividends(investment_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_dividends_payment_date ON dividends(payment_date)')

    conn.commit()
    conn.close()
    print("✅ データベース初期化完了")

def add_investment(name, type, symbol=None, shares=None, purchase_price=None, current_price=None, currency='JPY', purchase_date=None, notes=None):
    """投資追加"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO investments (name, type, symbol, shares, purchase_price, current_price, currency, purchase_date, notes)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (name, type, symbol, shares, purchase_price, current_price, currency, purchase_date, notes))

    investment_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return investment_id

def update_price(investment_id, current_price):
    """現在価格を更新"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    UPDATE investments
    SET current_price = ?
    WHERE id = ?
    ''', (current_price, investment_id))

    conn.commit()
    conn.close()

def calculate_pnl(investment_id):
    """損益を計算"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT shares, purchase_price, current_price, currency
    FROM investments
    WHERE id = ?
    ''', (investment_id,))

    result = cursor.fetchone()
    conn.close()

    if not result:
        return None

    shares, purchase_price, current_price, currency = result

    if not shares or not purchase_price or not current_price:
        return None

    purchase_value = shares * purchase_price
    current_value = shares * current_price
    pnl = current_value - purchase_value
    pnl_pct = (pnl / purchase_value) * 100 if purchase_value > 0 else 0

    return {
        'purchase_value': purchase_value,
        'current_value': current_value,
        'pnl': pnl,
        'pnl_pct': pnl_pct,
        'currency': currency
    }

def list_investments(investment_type=None, limit=20):
    """投資一覧"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    query = '''
    SELECT id, name, type, symbol, shares, purchase_price, current_price, currency, purchase_date, notes, created_at
    FROM investments
    '''

    params = []

    if investment_type:
        query += ' WHERE type = ?'
        params.append(investment_type)

    query += ' ORDER BY created_at DESC LIMIT ?'
    params.append(limit)

    cursor.execute(query, params)
    investments = cursor.fetchall()
    conn.close()
    return investments

def add_dividend(investment_id, amount, currency='JPY', payment_date=None, reinvested=False, notes=None):
    """配当追加"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO dividends (investment_id, amount, currency, payment_date, reinvested, notes)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', (investment_id, amount, currency, payment_date, reinvested, notes))

    dividend_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return dividend_id

def get_dividends(investment_id, limit=20):
    """配前一覧"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT id, investment_id, amount, currency, payment_date, reinvested, notes, created_at
    FROM dividends
    WHERE investment_id = ?
    ORDER BY payment_date DESC
    LIMIT ?
    ''', (investment_id, limit))

    dividends = cursor.fetchall()
    conn.close()
    return dividends

if __name__ == '__main__':
    init_db()
