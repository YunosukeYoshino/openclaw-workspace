#!/usr/bin/env python3
import sqlite3
from pathlib import Path

# データベースパス
db_path = Path(__file__).parent / "data" / "lifelog.db"
db_path.parent.mkdir(parents=True, exist_ok=True)

# 接続
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# エントリーテーブル
cursor.execute('''
CREATE TABLE IF NOT EXISTS entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT NOT NULL CHECK(type IN ('idea', 'goal', 'project', 'vision', 'note')),
    title TEXT,
    content TEXT NOT NULL,
    status TEXT DEFAULT 'active' CHECK(status IN ('active', 'archived', 'completed')),
    priority INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')

# タグテーブル
cursor.execute('''
CREATE TABLE IF NOT EXISTS tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')

# エントリーとタグの紐付け
cursor.execute('''
CREATE TABLE IF NOT EXISTS entry_tags (
    entry_id INTEGER NOT NULL,
    tag_id INTEGER NOT NULL,
    PRIMARY KEY (entry_id, tag_id),
    FOREIGN KEY (entry_id) REFERENCES entries(id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
)
''')

# 更新トリガー
cursor.execute('''
CREATE TRIGGER IF NOT EXISTS update_entries_timestamp
AFTER UPDATE ON entries
BEGIN
    UPDATE entries SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END
''')

# インデックス
cursor.execute('CREATE INDEX IF NOT EXISTS idx_entries_type ON entries(type)')
cursor.execute('CREATE INDEX IF NOT EXISTS idx_entries_status ON entries(status)')
cursor.execute('CREATE INDEX IF NOT EXISTS idx_entries_created ON entries(created_at)')

conn.commit()
conn.close()

print(f"✨ DB created at: {db_path}")
print("Tables: entries, tags, entry_tags")
