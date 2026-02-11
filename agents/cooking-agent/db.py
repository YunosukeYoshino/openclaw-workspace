#!/usr/bin/env python3
"""
料理エージェント #36
- レシピ管理
- 料理名・材料・手順・時間・難易度・タグ
"""

import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / "cooking.db"

def init_db():
    """データベース初期化"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # レシピテーブル
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS recipes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        ingredients TEXT,
        steps TEXT,
        prep_time INTEGER,
        cook_time INTEGER,
        servings INTEGER DEFAULT 1,
        difficulty TEXT CHECK(difficulty IN ('easy', 'medium', 'hard')),
        tags TEXT,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # 更新トリガー
    cursor.execute('''
    CREATE TRIGGER IF NOT EXISTS update_recipes_updated_at
    AFTER UPDATE ON recipes
    BEGIN
        UPDATE recipes SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
    END
    ''')

    # インデックス
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_recipes_name ON recipes(name)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_recipes_difficulty ON recipes(difficulty)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_recipes_tags ON recipes(tags)')

    conn.commit()
    conn.close()
    print("✅ データベース初期化完了")

def add_recipe(name, ingredients=None, steps=None, prep_time=None, cook_time=None, servings=1, difficulty=None, tags=None, notes=None):
    """レシピ追加"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO recipes (name, ingredients, steps, prep_time, cook_time, servings, difficulty, tags, notes)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (name, ingredients, steps, prep_time, cook_time, servings, difficulty, tags, notes))

    recipe_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return recipe_id

def update_recipe(recipe_id, name=None, ingredients=None, steps=None, prep_time=None, cook_time=None, servings=None, difficulty=None, tags=None, notes=None):
    """レシピ更新"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    updates = []
    params = []

    if name:
        updates.append("name = ?")
        params.append(name)
    if ingredients:
        updates.append("ingredients = ?")
        params.append(ingredients)
    if steps:
        updates.append("steps = ?")
        params.append(steps)
    if prep_time is not None:
        updates.append("prep_time = ?")
        params.append(prep_time)
    if cook_time is not None:
        updates.append("cook_time = ?")
        params.append(cook_time)
    if servings is not None:
        updates.append("servings = ?")
        params.append(servings)
    if difficulty:
        updates.append("difficulty = ?")
        params.append(difficulty)
    if tags:
        updates.append("tags = ?")
        params.append(tags)
    if notes:
        updates.append("notes = ?")
        params.append(notes)

    if updates:
        query = f"UPDATE recipes SET {', '.join(updates)} WHERE id = ?"
        params.append(recipe_id)
        cursor.execute(query, params)
        conn.commit()

    conn.close()

def delete_recipe(recipe_id):
    """レシピ削除"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('DELETE FROM recipes WHERE id = ?', (recipe_id,))

    conn.commit()
    conn.close()

def list_recipes(difficulty=None, tags=None, limit=20):
    """レシピ一覧"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    query = '''
    SELECT id, name, ingredients, steps, prep_time, cook_time, servings, difficulty, tags, notes, created_at
    FROM recipes
    '''

    params = []
    conditions = []

    if difficulty:
        conditions.append("difficulty = ?")
        params.append(difficulty)
    if tags:
        conditions.append("tags LIKE ?")
        params.append(f'%{tags}%')

    if conditions:
        query += ' WHERE ' + ' AND '.join(conditions)

    query += ' ORDER BY created_at DESC LIMIT ?'
    params.append(limit)

    cursor.execute(query, params)
    recipes = cursor.fetchall()
    conn.close()
    return recipes

def search_recipes(keyword):
    """レシピ検索"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT id, name, ingredients, steps, prep_time, cook_time, servings, difficulty, tags, notes, created_at
    FROM recipes
    WHERE name LIKE ? OR ingredients LIKE ? OR tags LIKE ? OR notes LIKE ?
    ORDER BY created_at DESC
    ''', (f'%{keyword}%', f'%{keyword}%', f'%{keyword}%', f'%{keyword}%'))

    recipes = cursor.fetchall()
    conn.close()
    return recipes

def get_recipe(recipe_id):
    """レシピ詳細取得"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT id, name, ingredients, steps, prep_time, cook_time, servings, difficulty, tags, notes, created_at
    FROM recipes
    WHERE id = ?
    ''', (recipe_id,))

    recipe = cursor.fetchone()
    conn.close()
    return recipe

def get_stats():
    """統計情報"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    stats = {}

    # 全レシピ数
    cursor.execute('SELECT COUNT(*) FROM recipes')
    stats['total'] = cursor.fetchone()[0]

    # 難易度別
    for difficulty in ['easy', 'medium', 'hard']:
        cursor.execute('SELECT COUNT(*) FROM recipes WHERE difficulty = ?', (difficulty,))
        stats[difficulty] = cursor.fetchone()[0]

    conn.close()
    return stats

if __name__ == '__main__':
    init_db()
