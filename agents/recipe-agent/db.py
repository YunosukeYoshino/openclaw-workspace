#!/usr/bin/env python3
"""
Recipe Agent #29
- Recipe recording
"""

import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / "recipes.db"

def init_db():
    """Initialize database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS recipes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        cuisine TEXT,
        category TEXT,
        servings INTEGER,
        prep_time INTEGER,
        cook_time INTEGER,
        difficulty TEXT DEFAULT 'medium' CHECK(difficulty IN ('easy', 'medium', 'hard')),
        ingredients TEXT,
        instructions TEXT,
        tags TEXT,
        source TEXT,
        rating INTEGER CHECK(rating IN (1,2,3,4,5)),
        notes TEXT,
        status TEXT DEFAULT 'active' CHECK(status IN ('active', 'archived')),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS recipe_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        recipe_id INTEGER NOT NULL,
        cook_date DATE,
        notes TEXT,
        rating INTEGER CHECK(rating IN (1,2,3,4,5)),
        modifications TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (recipe_id) REFERENCES recipes(id) ON DELETE CASCADE
    )
    ''')

    cursor.execute('CREATE INDEX IF NOT EXISTS idx_recipes_status ON recipes(status)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_recipes_category ON recipes(category)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_recipes_cuisine ON recipes(cuisine)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_recipe_logs_recipe ON recipe_logs(recipe_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_recipe_logs_date ON recipe_logs(cook_date)')

    conn.commit()
    conn.close()
    print("✅ Database initialized")

def add_recipe(name, description=None, cuisine=None, category=None, servings=None, prep_time=None, cook_time=None, difficulty='medium', ingredients=None, instructions=None, tags=None, source=None, rating=None, notes=None):
    """Add recipe"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO recipes (name, description, cuisine, category, servings, prep_time, cook_time, difficulty, ingredients, instructions, tags, source, rating, notes)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (name, description, cuisine, category, servings, prep_time, cook_time, difficulty, ingredients, instructions, tags, source, rating, notes))

    recipe_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return recipe_id

def log_cooking(recipe_id, cook_date=None, notes=None, rating=None, modifications=None):
    """Log cooking session"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    if not cook_date:
        cook_date = datetime.now().strftime("%Y-%m-%d")

    cursor.execute('''
    INSERT INTO recipe_logs (recipe_id, cook_date, notes, rating, modifications)
    VALUES (?, ?, ?, ?, ?)
    ''', (recipe_id, cook_date, notes, rating, modifications))

    log_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return log_id

def update_rating(recipe_id, rating):
    """Update recipe rating"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    UPDATE recipes SET rating = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?
    ''', (rating, recipe_id))

    conn.commit()
    conn.close()

def list_recipes(category=None, cuisine=None, difficulty=None, status=None, limit=50):
    """List recipes"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    query = '''
    SELECT id, name, description, cuisine, category, servings, prep_time, cook_time, difficulty, tags, rating, created_at
    FROM recipes
    '''

    params = []
    conditions = []

    if category:
        conditions.append('category = ?')
        params.append(category)

    if cuisine:
        conditions.append('cuisine = ?')
        params.append(cuisine)

    if difficulty:
        conditions.append('difficulty = ?')
        params.append(difficulty)

    if status:
        conditions.append('status = ?')
        params.append(status)

    if conditions:
        query += ' WHERE ' + ' AND '.join(conditions)

    query += ' ORDER BY rating DESC, created_at DESC LIMIT ?'
    params.append(limit)

    cursor.execute(query, params)
    recipes = cursor.fetchall()
    conn.close()
    return recipes

def search_recipes(keyword):
    """Search recipes"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT id, name, description, cuisine, category, servings, prep_time, cook_time, difficulty, tags, rating, created_at
    FROM recipes
    WHERE name LIKE ? OR description LIKE ? OR ingredients LIKE ? OR tags LIKE ?
    ORDER BY rating DESC, created_at DESC
    ''', (f'%{keyword}%', f'%{keyword}%', f'%{keyword}%', f'%{keyword}%'))

    recipes = cursor.fetchall()
    conn.close()
    return recipes

def get_recipe_details(recipe_id):
    """Get full recipe details"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT id, name, description, cuisine, category, servings, prep_time, cook_time, difficulty, ingredients, instructions, tags, source, rating, notes, created_at
    FROM recipes
    WHERE id = ?
    ''', (recipe_id,))

    recipe = cursor.fetchone()
    conn.close()
    return recipe

def get_cooking_logs(recipe_id, limit=10):
    """Get cooking logs for recipe"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT id, cook_date, notes, rating, modifications, created_at
    FROM recipe_logs
    WHERE recipe_id = ?
    ORDER BY cook_date DESC LIMIT ?
    ''', (recipe_id, limit))

    logs = cursor.fetchall()
    conn.close()
    return logs

def get_stats():
    """Get recipe statistics"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    stats = {}

    cursor.execute('SELECT COUNT(*) FROM recipes WHERE status = "active"')
    stats['total_recipes'] = cursor.fetchone()[0]

    for difficulty in ['easy', 'medium', 'hard']:
        cursor.execute('SELECT COUNT(*) FROM recipes WHERE difficulty = ?', (difficulty,))
        stats[difficulty] = cursor.fetchone()[0]

    cursor.execute('SELECT AVG(rating) FROM recipes WHERE rating IS NOT NULL')
    avg_rating = cursor.fetchone()[0]
    stats['average_rating'] = round(avg_rating, 2) if avg_rating else 0

    cursor.execute('SELECT COUNT(*) FROM recipe_logs')
    stats['total_cooks'] = cursor.fetchone()[0]

    conn.close()
    return stats

if __name__ == '__main__':
    init_db()
