#!/usr/bin/env python3
"""
Crypto Agent - Database Management
Supports Japanese and English
"""

import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / "crypto.db"

def init_db():
    """データベース初期化 / Initialize database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Holdings table (保有資産)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS holdings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        symbol TEXT NOT NULL,
        amount REAL NOT NULL,
        purchase_price REAL,
        purchase_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Price history table (価格履歴)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS price_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        symbol TEXT NOT NULL,
        price REAL NOT NULL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Alerts table (価格通知設定)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS alerts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        symbol TEXT NOT NULL,
        target_price REAL NOT NULL,
        alert_type TEXT CHECK(alert_type IN ('above', 'below')),
        status TEXT DEFAULT 'active' CHECK(status IN ('active', 'triggered', 'cancelled')),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Indices
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_holdings_symbol ON holdings(symbol)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_price_history_symbol ON price_history(symbol, timestamp)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_alerts_symbol ON alerts(symbol, status)')

    conn.commit()
    conn.close()
    print("✅ Database initialized / データベース初期化完了")

def add_holding(symbol, amount, purchase_price=None, purchase_date=None):
    """保有資産を追加 / Add holding"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    purchase_date = purchase_date or datetime.now().strftime("%Y-%m-%d %H:%M")

    cursor.execute('''
    INSERT INTO holdings (symbol, amount, purchase_price, purchase_date)
    VALUES (?, ?, ?, ?)
    ''', (symbol.upper(), amount, purchase_price, purchase_date))

    holding_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return holding_id

def list_holdings():
    """保有資産一覧 / List holdings"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT id, symbol, amount, purchase_price, purchase_date
    FROM holdings
    ORDER BY symbol
    ''')

    holdings = cursor.fetchall()
    conn.close()
    return holdings

def update_price(symbol, price):
    """価格を更新 / Update price"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO price_history (symbol, price)
    VALUES (?, ?)
    ''', (symbol.upper(), price))

    conn.commit()
    conn.close()

def get_latest_price(symbol):
    """最新価格を取得 / Get latest price"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT price, timestamp
    FROM price_history
    WHERE symbol = ?
    ORDER BY timestamp DESC
    LIMIT 1
    ''', (symbol.upper(),))

    result = cursor.fetchone()
    conn.close()
    return result

def add_alert(symbol, target_price, alert_type):
    """価格通知を追加 / Add price alert"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO alerts (symbol, target_price, alert_type)
    VALUES (?, ?, ?)
    ''', (symbol.upper(), target_price, alert_type))

    alert_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return alert_id

def list_alerts(status='active'):
    """通知一覧 / List alerts"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT id, symbol, target_price, alert_type, status, created_at
    FROM alerts
    WHERE status = ?
    ORDER BY created_at DESC
    ''', (status,))

    alerts = cursor.fetchall()
    conn.close()
    return alerts

def get_portfolio_value():
    """ポートフォリオ価値を計算 / Calculate portfolio value"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    holdings = list_holdings()
    total_value = 0.0
    details = []

    for holding in holdings:
        id, symbol, amount, purchase_price, purchase_date = holding
        latest = get_latest_price(symbol)
        if latest:
            current_price, _ = latest
            value = amount * current_price
            total_value += value
            details.append({
                'symbol': symbol,
                'amount': amount,
                'current_price': current_price,
                'value': value
            })

    conn.close()
    return {'total': total_value, 'details': details}

if __name__ == '__main__':
    init_db()
