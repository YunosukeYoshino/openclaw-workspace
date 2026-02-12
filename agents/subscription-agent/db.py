#!/usr/bin/env python3
"""
サブスクリプション管理エージェント #56
- サービス・課金日付・請求額
"""

import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / "subscriptions.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS subscriptions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        service TEXT,
        amount INTEGER NOT NULL,
        currency TEXT DEFAULT 'JPY',
        billing_cycle TEXT CHECK(billing_cycle IN ('monthly', 'yearly', 'quarterly', 'weekly')),
        next_billing_date DATE,
        status TEXT DEFAULT 'active' CHECK(status IN ('active', 'paused', 'cancelled')),
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    cursor.execute('''
    CREATE TRIGGER IF NOT EXISTS update_subscriptions_updated_at
    AFTER UPDATE ON subscriptions
    BEGIN
        UPDATE subscriptions SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
    END
    ''')

    cursor.execute('CREATE INDEX IF NOT EXISTS idx_subscriptions_status ON subscriptions(status)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_subscriptions_next_billing ON subscriptions(next_billing_date)')

    conn.commit()
    conn.close()

def add_subscription(name, service=None, amount=None, currency='JPY', billing_cycle='monthly', next_billing_date=None, notes=None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO subscriptions (name, service, amount, currency, billing_cycle, next_billing_date, notes)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (name, service, amount, currency, billing_cycle, next_billing_date, notes))

    sub_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return sub_id

def update_subscription(sub_id, status=None, next_billing_date=None, amount=None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    updates = []
    params = []

    if status:
        updates.append("status = ?")
        params.append(status)
    if next_billing_date:
        updates.append("next_billing_date = ?")
        params.append(next_billing_date)
    if amount:
        updates.append("amount = ?")
        params.append(amount)

    if updates:
        query = f"UPDATE subscriptions SET {', '.join(updates)} WHERE id = ?"
        params.append(sub_id)
        cursor.execute(query, params)
        conn.commit()

    conn.close()

def list_subscriptions(status=None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    query = 'SELECT id, name, service, amount, currency, billing_cycle, next_billing_date, status, notes, created_at FROM subscriptions'

    params = []
    if status:
        query += ' WHERE status = ?'
        params.append(status)

    query += ' ORDER BY next_billing_date ASC'

    cursor.execute(query, params)
    subs = cursor.fetchall()
    conn.close()
    return subs

def get_monthly_total():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT SUM(amount) as total
    FROM subscriptions
    WHERE status = 'active' AND billing_cycle = 'monthly'
    ''')

    result = cursor.fetchone()
    conn.close()
    return result[0] if result else 0

if __name__ == '__main__':
    init_db()
