#!/usr/bin/env python3
"""
言語学習エージェント #46
- 語彙・文法・練習記録
- 言語・レベル・進捗
"""

import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / "language.db"

def init_db():
    """データベース初期化"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 語彙テーブル
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS vocabulary (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        word TEXT NOT NULL,
        translation TEXT,
        language TEXT NOT NULL,
        part_of_speech TEXT,
        definition TEXT,
        example TEXT,
        tags TEXT,
        mastery_level INTEGER DEFAULT 0,
        review_count INTEGER DEFAULT 0,
        next_review DATE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # 文法テーブル
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS grammar (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        rule TEXT NOT NULL,
        explanation TEXT,
        language TEXT NOT NULL,
        example TEXT,
        difficulty TEXT DEFAULT 'intermediate',
        tags TEXT,
        mastery_level INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # 練習記録テーブル
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS practice (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        practice_type TEXT NOT NULL,
        language TEXT NOT NULL,
        duration INTEGER,
        content TEXT,
        date DATE NOT NULL,
        notes TEXT,
        rating INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # 進捗テーブル
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS progress (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        language TEXT NOT NULL,
        level TEXT NOT NULL,
        xp INTEGER DEFAULT 0,
        streak INTEGER DEFAULT 0,
        last_practice DATE,
        goal_xp INTEGER DEFAULT 100,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # インデックス
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_vocabulary_language ON vocabulary(language)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_vocabulary_mastery ON vocabulary(mastery_level)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_grammar_language ON grammar(language)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_practice_date ON practice(date)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_progress_language ON progress(language)')

    conn.commit()
    conn.close()
    print("✅ データベース初期化完了")

def add_vocabulary(word, translation=None, language=None, part_of_speech=None,
                   definition=None, example=None, tags=None, mastery_level=0):
    """語彙を追加"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO vocabulary (word, translation, language, part_of_speech, definition, example, tags, mastery_level)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (word, translation, language, part_of_speech, definition, example, tags, mastery_level))

    vocab_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return vocab_id

def add_grammar(rule, explanation, language, example=None, difficulty='intermediate', tags=None):
    """文法を追加"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO grammar (rule, explanation, language, example, difficulty, tags)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', (rule, explanation, language, example, difficulty, tags))

    grammar_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return grammar_id

def add_practice(practice_type, language, duration=None, content=None,
                 date=None, notes=None, rating=None):
    """練習を追加"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")

    cursor.execute('''
    INSERT INTO practice (practice_type, language, duration, content, date, notes, rating)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (practice_type, language, duration, content, date, notes, rating))

    practice_id = cursor.lastrowid

    # 進捗を更新
    update_progress(language, date, duration)

    conn.commit()
    conn.close()
    return practice_id

def update_progress(language, date, duration=None):
    """進捗を更新"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    xp_gain = duration if duration else 10

    cursor.execute('''
    SELECT id, xp, streak, last_practice FROM progress WHERE language = ?
    ''', (language,))

    result = cursor.fetchone()

    if result:
        progress_id, current_xp, streak, last_practice = result

        # 連続学習日数を計算
        new_streak = streak
        if last_practice:
            last_date = datetime.strptime(last_practice, "%Y-%m-%d").date()
            current_date = datetime.strptime(date, "%Y-%m-%d").date()
            delta = (current_date - last_date).days

            if delta == 1:
                new_streak = streak + 1
            elif delta > 1:
                new_streak = 1

        cursor.execute('''
        UPDATE progress
        SET xp = xp + ?, streak = ?, last_practice = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
        ''', (xp_gain, new_streak, date, progress_id))
    else:
        # 新しい言語の進捗を作成
        cursor.execute('''
        INSERT INTO progress (language, level, xp, streak, last_practice)
        VALUES (?, 'beginner', ?, 1, ?)
        ''', (language, xp_gain, date))

    conn.commit()
    conn.close()

def list_vocabulary(language=None, part_of_speech=None, mastery_level=None, limit=20):
    """語彙一覧"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    query = 'SELECT id, word, translation, language, part_of_speech, definition, example, mastery_level FROM vocabulary'
    params = []
    conditions = []

    if language:
        conditions.append("language = ?")
        params.append(language)
    if part_of_speech:
        conditions.append("part_of_speech = ?")
        params.append(part_of_speech)
    if mastery_level is not None:
        conditions.append("mastery_level = ?")
        params.append(mastery_level)

    if conditions:
        query += ' WHERE ' + ' AND '.join(conditions)

    query += ' ORDER BY mastery_level ASC, created_at DESC LIMIT ?'
    params.append(limit)

    cursor.execute(query, params)
    vocab_list = cursor.fetchall()
    conn.close()
    return vocab_list

def list_grammar(language=None, difficulty=None, limit=20):
    """文法一覧"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    query = 'SELECT id, rule, explanation, language, example, difficulty FROM grammar'
    params = []
    conditions = []

    if language:
        conditions.append("language = ?")
        params.append(language)
    if difficulty:
        conditions.append("difficulty = ?")
        params.append(difficulty)

    if conditions:
        query += ' WHERE ' + ' AND '.join(conditions)

    query += ' ORDER BY difficulty, created_at DESC LIMIT ?'
    params.append(limit)

    cursor.execute(query, params)
    grammar_list = cursor.fetchall()
    conn.close()
    return grammar_list

def list_practice(language=None, date=None, practice_type=None, limit=20):
    """練習一覧"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    query = 'SELECT id, practice_type, language, duration, content, date, notes, rating FROM practice'
    params = []
    conditions = []

    if language:
        conditions.append("language = ?")
        params.append(language)
    if date:
        conditions.append("date = ?")
        params.append(date)
    if practice_type:
        conditions.append("practice_type = ?")
        params.append(practice_type)

    if conditions:
        query += ' WHERE ' + ' AND '.join(conditions)

    query += ' ORDER BY date DESC, created_at DESC LIMIT ?'
    params.append(limit)

    cursor.execute(query, params)
    practice_list = cursor.fetchall()
    conn.close()
    return practice_list

def get_progress(language=None):
    """進捗を取得"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    if language:
        cursor.execute('''
        SELECT id, language, level, xp, streak, last_practice, goal_xp, updated_at
        FROM progress WHERE language = ?
        ''', (language,))
        result = cursor.fetchone()
        conn.close()
        return result
    else:
        cursor.execute('''
        SELECT id, language, level, xp, streak, last_practice, goal_xp, updated_at
        FROM progress ORDER BY updated_at DESC
        ''')
        results = cursor.fetchall()
        conn.close()
        return results

def search_vocabulary(keyword):
    """語彙を検索"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT id, word, translation, language, part_of_speech, definition, example, mastery_level
    FROM vocabulary
    WHERE word LIKE ? OR translation LIKE ? OR definition LIKE ? OR example LIKE ?
    ORDER BY mastery_level ASC
    ''', (f'%{keyword}%', f'%{keyword}%', f'%{keyword}%', f'%{keyword}%'))

    results = cursor.fetchall()
    conn.close()
    return results

def update_vocabulary(vocab_id, **kwargs):
    """語彙を更新"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    updates = []
    params = []

    for key, value in kwargs.items():
        if value is not None:
            updates.append(f"{key} = ?")
            params.append(value)

    if updates:
        query = f"UPDATE vocabulary SET {', '.join(updates)}, updated_at = CURRENT_TIMESTAMP WHERE id = ?"
        params.append(vocab_id)
        cursor.execute(query, params)
        conn.commit()

    conn.close()

def delete_vocabulary(vocab_id):
    """語彙を削除"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('DELETE FROM vocabulary WHERE id = ?', (vocab_id,))
    conn.commit()
    conn.close()

def get_stats(language=None):
    """統計情報"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    stats = {}

    # 語彙数
    query = 'SELECT COUNT(*) FROM vocabulary'
    params = []
    if language:
        query += ' WHERE language = ?'
        params.append(language)
    cursor.execute(query, params)
    stats['vocabulary_count'] = cursor.fetchone()[0]

    # 文法数
    query = 'SELECT COUNT(*) FROM grammar'
    params = []
    if language:
        query += ' WHERE language = ?'
        params.append(language)
    cursor.execute(query, params)
    stats['grammar_count'] = cursor.fetchone()[0]

    # 総練習時間
    query = 'SELECT COALESCE(SUM(duration), 0) FROM practice'
    params = []
    if language:
        query += ' WHERE language = ?'
        params.append(language)
    cursor.execute(query, params)
    stats['total_practice_minutes'] = cursor.fetchone()[0]

    # 練習回数
    query = 'SELECT COUNT(*) FROM practice'
    params = []
    if language:
        query += ' WHERE language = ?'
        params.append(language)
    cursor.execute(query, params)
    stats['practice_count'] = cursor.fetchone()[0]

    # 今日の練習
    today = datetime.now().strftime("%Y-%m-%d")
    query = 'SELECT COUNT(*) FROM practice WHERE date = ?'
    params = [today]
    if language:
        query += ' AND language = ?'
        params.append(language)
    cursor.execute(query, params)
    stats['today_practice'] = cursor.fetchone()[0]

    conn.close()
    return stats

if __name__ == '__main__':
    init_db()
