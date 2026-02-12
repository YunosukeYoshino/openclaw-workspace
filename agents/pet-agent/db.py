#!/usr/bin/env python3
"""
ペットエージェント #39
- ペット管理
- ペット・食事・散歩・健康・美容
"""

import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / "pets.db"

def init_db():
    """データベース初期化"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # ペットテーブル
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS pets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        species TEXT,
        breed TEXT,
        birth_date DATE,
        weight REAL,
        gender TEXT,
        microchip TEXT,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # 食事記録テーブル
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS meals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        pet_id INTEGER NOT NULL,
        date DATE NOT NULL,
        time TIME,
        food TEXT,
        amount TEXT,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (pet_id) REFERENCES pets(id) ON DELETE CASCADE
    )
    ''')

    # 散歩記録テーブル
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS walks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        pet_id INTEGER NOT NULL,
        date DATE NOT NULL,
        time TIME,
        duration INTEGER,
        distance REAL,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (pet_id) REFERENCES pets(id) ON DELETE CASCADE
    )
    ''')

    # 健康記録テーブル
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS health (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        pet_id INTEGER NOT NULL,
        date DATE NOT NULL,
        type TEXT,
        description TEXT,
        vet TEXT,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (pet_id) REFERENCES pets(id) ON DELETE CASCADE
    )
    ''')

    # 更新トリガー
    cursor.execute('''
    CREATE TRIGGER IF NOT EXISTS update_pets_updated_at
    AFTER UPDATE ON pets
    BEGIN
        UPDATE pets SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
    END
    ''')

    # インデックス
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_meals_pet_id ON meals(pet_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_meals_date ON meals(date)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_walks_pet_id ON walks(pet_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_walks_date ON walks(date)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_health_pet_id ON health(pet_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_health_date ON health(date)')

    conn.commit()
    conn.close()
    print("✅ データベース初期化完了")

def add_pet(name, species=None, breed=None, birth_date=None, weight=None, gender=None, microchip=None, notes=None):
    """ペット追加"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO pets (name, species, breed, birth_date, weight, gender, microchip, notes)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (name, species, breed, birth_date, weight, gender, microchip, notes))

    pet_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return pet_id

def list_pets():
    """ペット一覧"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT id, name, species, breed, birth_date, weight, gender, microchip, notes, created_at
    FROM pets
    ORDER BY created_at ASC
    ''')

    pets = cursor.fetchall()
    conn.close()
    return pets

def get_pet(pet_id):
    """ペット取得"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT id, name, species, breed, birth_date, weight, gender, microchip, notes, created_at
    FROM pets
    WHERE id = ?
    ''', (pet_id,))

    pet = cursor.fetchone()
    conn.close()
    return pet

# 食事関連
def add_meal(pet_id, date, food=None, amount=None, time=None, notes=None):
    """食事追加"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO meals (pet_id, date, food, amount, time, notes)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', (pet_id, date, food, amount, time, notes))

    meal_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return meal_id

def list_meals(pet_id, date_from=None, date_to=None, limit=20):
    """食事一覧"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    query = '''
    SELECT id, pet_id, date, time, food, amount, notes, created_at
    FROM meals
    WHERE pet_id = ?
    '''

    params = [pet_id]

    if date_from:
        query += ' AND date >= ?'
        params.append(date_from)
    if date_to:
        query += ' AND date <= ?'
        params.append(date_to)

    query += ' ORDER BY date DESC, time DESC LIMIT ?'
    params.append(limit)

    cursor.execute(query, params)
    meals = cursor.fetchall()
    conn.close()
    return meals

# 散歩関連
def add_walk(pet_id, date, duration=None, distance=None, time=None, notes=None):
    """散歩追加"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO walks (pet_id, date, duration, distance, time, notes)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', (pet_id, date, duration, distance, time, notes))

    walk_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return walk_id

def list_walks(pet_id, date_from=None, date_to=None, limit=20):
    """散歩一覧"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    query = '''
    SELECT id, pet_id, date, time, duration, distance, notes, created_at
    FROM walks
    WHERE pet_id = ?
    '''

    params = [pet_id]

    if date_from:
        query += ' AND date >= ?'
        params.append(date_from)
    if date_to:
        query += ' AND date <= ?'
        params.append(date_to)

    query += ' ORDER BY date DESC, time DESC LIMIT ?'
    params.append(limit)

    cursor.execute(query, params)
    walks = cursor.fetchall()
    conn.close()
    return walks

# 健康関連
def add_health(pet_id, date, type, description=None, vet=None, notes=None):
    """健康記録追加"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO health (pet_id, date, type, description, vet, notes)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', (pet_id, date, type, description, vet, notes))

    health_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return health_id

def list_health(pet_id, date_from=None, date_to=None, limit=20):
    """健康記録一覧"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    query = '''
    SELECT id, pet_id, date, type, description, vet, notes, created_at
    FROM health
    WHERE pet_id = ?
    '''

    params = [pet_id]

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
