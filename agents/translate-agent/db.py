#!/usr/bin/env python3
"""
Translation Agent
- Multi-language translation
- Text translation
- Translation history
"""

import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / "translations.db"

def init_db():
    """Initialize database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Translation history table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS translation_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        source_text TEXT NOT NULL,
        translated_text TEXT NOT NULL,
        source_lang TEXT NOT NULL,
        target_lang TEXT NOT NULL,
        translation_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        bookmarked BOOLEAN DEFAULT 0
    )
    ''')

    # Bookmarked translations table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS bookmarked_translations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        translation_id INTEGER NOT NULL,
        name TEXT,
        note TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (translation_id) REFERENCES translation_history(id) ON DELETE CASCADE
    )
    ''')

    # Language preferences table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS language_preferences (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        source_lang TEXT,
        target_lang TEXT,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(user_id)
    )
    ''')

    # Common translations table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS common_translations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        phrase TEXT NOT NULL,
        source_lang TEXT NOT NULL,
        translated TEXT NOT NULL,
        target_lang TEXT NOT NULL,
        usage_count INTEGER DEFAULT 0,
        UNIQUE(phrase, source_lang, target_lang)
    )
    ''')

    # Indexes
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_translation_timestamp ON translation_history(translation_timestamp)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_translation_langs ON translation_history(source_lang, target_lang)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_translation_bookmarked ON translation_history(bookmarked)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_common_translations_phrase ON common_translations(phrase)')

    conn.commit()
    conn.close()
    print("✅ Database initialized")

def add_translation(source_text, translated_text, source_lang, target_lang):
    """Add translation to history"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO translation_history (source_text, translated_text, source_lang, target_lang)
    VALUES (?, ?, ?, ?)
    ''', (source_text, translated_text, source_lang, target_lang))

    translation_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return translation_id

def get_translation_history(limit=20, source_lang=None, target_lang=None):
    """Get translation history"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    if source_lang and target_lang:
        cursor.execute('''
        SELECT * FROM translation_history
        WHERE source_lang = ? AND target_lang = ?
        ORDER BY translation_timestamp DESC
        LIMIT ?
        ''', (source_lang, target_lang, limit))
    else:
        cursor.execute('''
        SELECT * FROM translation_history
        ORDER BY translation_timestamp DESC
        LIMIT ?
        ''', (limit,))

    history = cursor.fetchall()
    conn.close()
    return history

def bookmark_translation(translation_id, name=None, note=None):
    """Bookmark translation"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute('''
        INSERT INTO bookmarked_translations (translation_id, name, note)
        VALUES (?, ?, ?)
        ''', (translation_id, name, note))

        # Mark as bookmarked
        cursor.execute('UPDATE translation_history SET bookmarked = 1 WHERE id = ?', (translation_id,))

        bookmark_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return bookmark_id
    except sqlite3.IntegrityError:
        conn.close()
        return None

def get_bookmarked_translations():
    """Get bookmarked translations"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT bt.id, bt.name, bt.note, bt.created_at,
           th.source_text, th.translated_text, th.source_lang, th.target_lang
    FROM bookmarked_translations bt
    JOIN translation_history th ON bt.translation_id = th.id
    ORDER BY bt.created_at DESC
    ''')

    bookmarked = cursor.fetchall()
    conn.close()
    return bookmarked

def set_language_preference(user_id, source_lang=None, target_lang=None):
    """Set language preference for user"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT OR REPLACE INTO language_preferences (user_id, source_lang, target_lang, updated_at)
    VALUES (?, COALESCE(?, (SELECT source_lang FROM language_preferences WHERE user_id = ?)),
            COALESCE(?, (SELECT target_lang FROM language_preferences WHERE user_id = ?)), ?)
    ''', (user_id, source_lang, user_id, target_lang, user_id, datetime.now()))

    conn.commit()
    conn.close()

def get_language_preference(user_id):
    """Get language preference for user"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT source_lang, target_lang FROM language_preferences WHERE user_id = ?
    ''', (user_id,))

    result = cursor.fetchone()
    conn.close()
    return result

def add_common_translation(phrase, translated, source_lang, target_lang):
    """Add common translation"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute('''
        INSERT INTO common_translations (phrase, source_lang, translated, target_lang, usage_count)
        VALUES (?, ?, ?, ?, 1)
        ''', (phrase, source_lang, translated, target_lang))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        # Update usage count
        cursor.execute('''
        UPDATE common_translations
        SET usage_count = usage_count + 1
        WHERE phrase = ? AND source_lang = ? AND target_lang = ?
        ''', (phrase, source_lang, target_lang))
        conn.commit()
        conn.close()
        return False

def get_common_translations(source_lang, target_lang, limit=20):
    """Get common translations"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT * FROM common_translations
    WHERE source_lang = ? AND target_lang = ?
    ORDER BY usage_count DESC
    LIMIT ?
    ''', (source_lang, target_lang, limit))

    common = cursor.fetchall()
    conn.close()
    return common

def search_translations(keyword):
    """Search translations by keyword"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT * FROM translation_history
    WHERE source_text LIKE ? OR translated_text LIKE ?
    ORDER BY translation_timestamp DESC
    ''', (f'%{keyword}%', f'%{keyword}%'))

    results = cursor.fetchall()
    conn.close()
    return results

def delete_translation(translation_id):
    """Delete translation from history"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('DELETE FROM translation_history WHERE id = ?', (translation_id,))
    conn.commit()
    conn.close()

def unbookmark_translation(bookmark_id):
    """Unbookmark translation"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Get translation_id first
    cursor.execute('SELECT translation_id FROM bookmarked_translations WHERE id = ?', (bookmark_id,))
    result = cursor.fetchone()

    if result:
        translation_id = result[0]
        cursor.execute('DELETE FROM bookmarked_translations WHERE id = ?', (bookmark_id,))
        # Check if still bookmarked
        cursor.execute('SELECT COUNT(*) FROM bookmarked_translations WHERE translation_id = ?', (translation_id,))
        count = cursor.fetchone()[0]
        if count == 0:
            cursor.execute('UPDATE translation_history SET bookmarked = 0 WHERE id = ?', (translation_id,))

    conn.commit()
    conn.close()

def get_stats():
    """Get translation statistics"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    stats = {}

    # Total translations
    cursor.execute('SELECT COUNT(*) FROM translation_history')
    stats['total_translations'] = cursor.fetchone()[0]

    # By language pair
    cursor.execute('''
    SELECT source_lang || ' -> ' || target_lang, COUNT(*)
    FROM translation_history
    GROUP BY source_lang, target_lang
    ORDER BY COUNT(*) DESC
    ''')
    stats['by_language_pair'] = dict(cursor.fetchall())

    # Bookmarked translations
    cursor.execute('SELECT COUNT(*) FROM bookmarked_translations')
    stats['bookmarked'] = cursor.fetchone()[0]

    # Common translations
    cursor.execute('SELECT COUNT(*) FROM common_translations')
    stats['common_translations'] = cursor.fetchone()[0]

    # Recent translations (last 7 days)
    cursor.execute('''
    SELECT COUNT(*) FROM translation_history
    WHERE translation_timestamp >= datetime('now', '-7 days')
    ''')
    stats['recent_translations'] = cursor.fetchone()[0]

    conn.close()
    return stats

if __name__ == '__main__':
    init_db()
