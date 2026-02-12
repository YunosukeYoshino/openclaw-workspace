#!/usr/bin/env python3
"""
植物エージェント #40
- 植物管理
- 植物・水やり・肥料・健康・記録
"""

import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / "plants.db"

def init_db():
    """データベース初期化"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 植物テーブル
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS plants (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        species TEXT,
        location TEXT,
        acquired_date DATE,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # 水やり記録テーブル
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS waterings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        plant_id INTEGER NOT NULL,
        date DATE NOT NULL,
        time TIME,
        amount TEXT,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (plant_id) REFERENCES plants(id) ON DELETE CASCADE
    )
    ''')

    # 肥料記録テーブル
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS fertilizations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        plant_id INTEGER NOT NULL,
        date DATE NOT NULL,
        fertilizer TEXT,
        amount TEXT,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (plant_id) REFERENCES plants(id) ON DELETE CASCADE
    )
    ''')

    # 健康記録テーブル
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS health_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        plant_id INTEGER NOT NULL,
        date DATE NOT NULL,
        status TEXT,
        description TEXT,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (plant_id) REFERENCES plants(id) ON DELETE CASCADE
    )
    ''')

    # 更新トリガー
    cursor.execute('''
    CREATE TRIGGER IF NOT EXISTS update_plants_updated_at
    AFTER UPDATE ON plants
    BEGIN
        UPDATE plants SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
    END
    ''')

    # インデックス
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_waterings_plant_id ON waterings(plant_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_waterings_date ON waterings(date)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_fertilizations_plant_id ON fertilizations(plant_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_fertilizations_date ON fertilizations(date)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_health_records_plant_id ON health_records(plant_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_health_records_date ON health_records(date)')

    conn.commit()
    conn.close()
    print("✅ データベース初期化完了")

def add_plant(name, species=None, location=None, acquired_date=None, notes=None):
    """植物追加"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO plants (name, species, location, acquired_date, notes)
    VALUES (?, ?, ?, ?, ?)
    ''', (name, species, location, acquired_date, notes))

    plant_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return plant_id

def list_plants():
    """植物一覧"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT id, name, species, location, acquired_date, notes, created_at
    FROM plants
    ORDER BY created_at ASC
    ''')

    plants = cursor.fetchall()
    conn.close()
    return plants

def get_plant(plant_id):
    """植物取得"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT id, name, species, location, acquired_date, notes, created_at
    FROM plants
    WHERE id = ?
    ''', (plant_id,))

    plant = cursor.fetchone()
    conn.close()
    return plant

# 水やり関連
def add_watering(plant_id, date, amount=None, time=None, notes=None):
    """水やり追加"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO waterings (plant_id, date, amount, time, notes)
    VALUES (?, ?, ?, ?, ?)
    ''', (plant_id, date, amount, time, notes))

    watering_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return watering_id

def list_waterings(plant_id, date_from=None, date_to=None, limit=20):
    """水やり一覧"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    query = '''
    SELECT id, plant_id, date, time, amount, notes, created_at
    FROM waterings
    WHERE plant_id = ?
    '''

    params = [plant_id]

    if date_from:
        query += ' AND date >= ?'
        params.append(date_from)
    if date_to:
        query += ' AND date <= ?'
        params.append(date_to)

    query += ' ORDER BY date DESC, time DESC LIMIT ?'
    params.append(limit)

    cursor.execute(query, params)
    waterings = cursor.fetchall()
    conn.close()
    return waterings

# 肥料関連
def add_fertilization(plant_id, date, fertilizer=None, amount=None, notes=None):
    """肥料追加"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO fertilizations (plant_id, date, fertilizer, amount, notes)
    VALUES (?, ?, ?, ?, ?)
    ''', (plant_id, date, fertilizer, amount, notes))

    fertilization_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return fertilization_id

def list_fertilizations(plant_id, date_from=None, date_to=None, limit=20):
    """肥料一覧"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    query = '''
    SELECT id, plant_id, date, fertilizer, amount, notes, created_at
    FROM fertilizations
    WHERE plant_id = ?
    '''

    params = [plant_id]

    if date_from:
        query += ' AND date >= ?'
        params.append(date_from)
    if date_to:
        query += ' AND date <= ?'
        params.append(date_to)

    query += ' ORDER BY date DESC LIMIT ?'
    params.append(limit)

    cursor.execute(query, params)
    fertilizations = cursor.fetchall()
    conn.close()
    return fertilizations

# 健康記録関連
def add_health_record(plant_id, date, status, description=None, notes=None):
    """健康記録追加"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO health_records (plant_id, date, status, description, notes)
    VALUES (?, ?, ?, ?, ?)
    ''', (plant_id, date, status, description, notes))

    health_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return health_id

def list_health_records(plant_id, date_from=None, date_to=None, limit=20):
    """健康記録一覧"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    query = '''
    SELECT id, plant_id, date, status, description, notes, created_at
    FROM health_records
    WHERE plant_id = ?
    '''

    params = [plant_id]

    if date_from:
        query += ' AND date >= ?'
        params.append(date_from)
    if date_to:
        query += ' AND date <= ?'
        params.append(date_to)

    query += ' ORDER BY date DESC LIMIT ?'
    params.append(limit)

    cursor.execute(query, params)
    health_records = cursor.fetchall()
    conn.close()
    return health_records

if __name__ == '__main__':
    init_db()
