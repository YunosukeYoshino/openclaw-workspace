#!/usr/bin/env python3
"""
Inventory Agent #24
- Track inventory
"""

import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / "inventory.db"

def init_db():
    """Initialize database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS inventory (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        category TEXT,
        sku TEXT,
        quantity INTEGER DEFAULT 0,
        unit TEXT,
        location TEXT,
        min_stock INTEGER DEFAULT 0,
        max_stock INTEGER,
        cost_price REAL,
        sell_price REAL,
        status TEXT DEFAULT 'active' CHECK(status IN ('active', 'discontinued', 'out_of_stock')),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS inventory_transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        item_id INTEGER NOT NULL,
        transaction_type TEXT CHECK(transaction_type IN ('in', 'out', 'adjust')),
        quantity INTEGER NOT NULL,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (item_id) REFERENCES inventory(id) ON DELETE CASCADE
    )
    ''')

    cursor.execute('CREATE INDEX IF NOT EXISTS idx_inventory_status ON inventory(status)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_inventory_category ON inventory(category)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_inventory_location ON inventory(location)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_inventory_transactions_item ON inventory_transactions(item_id)')

    conn.commit()
    conn.close()
    print("✅ Database initialized")

def add_item(name, description=None, category=None, sku=None, quantity=0, unit=None, location=None, min_stock=0, max_stock=None, cost_price=None, sell_price=None):
    """Add inventory item"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO inventory (name, description, category, sku, quantity, unit, location, min_stock, max_stock, cost_price, sell_price)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (name, description, category, sku, quantity, unit, location, min_stock, max_stock, cost_price, sell_price))

    item_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return item_id

def update_quantity(item_id, quantity, transaction_type='adjust', notes=None):
    """Update item quantity"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    UPDATE inventory SET quantity = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?
    ''', (quantity, item_id))

    cursor.execute('''
    INSERT INTO inventory_transactions (item_id, transaction_type, quantity, notes)
    VALUES (?, ?, ?, ?)
    ''', (item_id, transaction_type, quantity, notes))

    conn.commit()
    conn.close()

def adjust_stock(item_id, change, notes=None):
    """Adjust stock level"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('SELECT quantity FROM inventory WHERE id = ?', (item_id,))
    result = cursor.fetchone()
    if result:
        current_qty = result[0]
        new_qty = current_qty + change

        cursor.execute('''
        UPDATE inventory SET quantity = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?
        ''', (new_qty, item_id))

        transaction_type = 'in' if change > 0 else 'out'
        cursor.execute('''
        INSERT INTO inventory_transactions (item_id, transaction_type, quantity, notes)
        VALUES (?, ?, ?, ?)
        ''', (item_id, transaction_type, abs(change), notes))

    conn.commit()
    conn.close()

def list_items(category=None, location=None, status=None, limit=50):
    """List inventory items"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    query = '''
    SELECT id, name, description, category, sku, quantity, unit, location, min_stock, cost_price, sell_price, status, created_at
    FROM inventory
    '''

    params = []
    conditions = []

    if category:
        conditions.append('category = ?')
        params.append(category)

    if location:
        conditions.append('location = ?')
        params.append(location)

    if status:
        conditions.append('status = ?')
        params.append(status)

    if conditions:
        query += ' WHERE ' + ' AND '.join(conditions)

    query += ' ORDER BY name ASC LIMIT ?'
    params.append(limit)

    cursor.execute(query, params)
    items = cursor.fetchall()
    conn.close()
    return items

def get_low_stock_items():
    """Get items below minimum stock"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT id, name, quantity, min_stock, unit
    FROM inventory
    WHERE quantity < min_stock AND status = 'active'
    ORDER BY quantity ASC
    ''')

    items = cursor.fetchall()
    conn.close()
    return items

def search_items(keyword):
    """Search inventory items"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT id, name, description, category, sku, quantity, unit, location, min_stock, cost_price, sell_price, status, created_at
    FROM inventory
    WHERE name LIKE ? OR description LIKE ? OR sku LIKE ?
    ORDER BY name ASC
    ''', (f'%{keyword}%', f'%{keyword}%', f'%{keyword}%'))

    items = cursor.fetchall()
    conn.close()
    return items

def get_transactions(item_id, limit=20):
    """Get transaction history for item"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT id, transaction_type, quantity, notes, created_at
    FROM inventory_transactions
    WHERE item_id = ?
    ORDER BY created_at DESC LIMIT ?
    ''', (item_id, limit))

    transactions = cursor.fetchall()
    conn.close()
    return transactions

def get_stats():
    """Get inventory statistics"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    stats = {}

    cursor.execute('SELECT COUNT(*) FROM inventory')
    stats['total_items'] = cursor.fetchone()[0]

    cursor.execute('SELECT SUM(quantity) FROM inventory WHERE status = "active"')
    total_qty = cursor.fetchone()[0]
    stats['total_quantity'] = total_qty if total_qty else 0

    cursor.execute('SELECT COUNT(*) FROM inventory WHERE quantity < min_stock AND status = "active"')
    stats['low_stock_count'] = cursor.fetchone()[0]

    cursor.execute('SELECT SUM(cost_price * quantity) FROM inventory WHERE status = "active"')
    total_value = cursor.fetchone()[0]
    stats['total_value'] = total_value if total_value else 0

    conn.close()
    return stats

if __name__ == '__main__':
    init_db()
