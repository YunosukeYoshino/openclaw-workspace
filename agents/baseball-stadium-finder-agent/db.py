#!/usr/bin/env python3
"""
野球スタジアム検索・情報エージェント / Baseball Stadium Finder and Information Agent
"""

import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / "baseball_stadium_finder.db"

def init_db():
    """データベース初期化"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        description TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    conn.commit()
    conn.close()
    print("✅ データベース初期化完了")

if __name__ == '__main__':
    init_db()
