const Database = require('better-sqlite3');
const path = require('path');

// DBファイルのパス
const dbPath = path.join(__dirname, 'data', 'lifelog.db');
const db = new Database(dbPath);

// 外部キー制約を有効化
db.pragma('foreign_keys = ON');

// エントリーテーブル
db.exec(`
  CREATE TABLE IF NOT EXISTS entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT NOT NULL CHECK(type IN ('idea', 'goal', 'project', 'vision', 'note')),
    title TEXT,
    content TEXT NOT NULL,
    status TEXT DEFAULT 'active' CHECK(status IN ('active', 'archived', 'completed')),
    priority INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
  );
`);

// タグテーブル
db.exec(`
  CREATE TABLE IF NOT EXISTS tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
  );
`);

// エントリーとタグの紐付け
db.exec(`
  CREATE TABLE IF NOT EXISTS entry_tags (
    entry_id INTEGER NOT NULL,
    tag_id INTEGER NOT NULL,
    PRIMARY KEY (entry_id, tag_id),
    FOREIGN KEY (entry_id) REFERENCES entries(id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
  );
`);

// 更新時のタイムスタンプ自動更新用トリガー
db.exec(`
  CREATE TRIGGER IF NOT EXISTS update_entries_timestamp
  AFTER UPDATE ON entries
  BEGIN
    UPDATE entries SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
  END;
`);

// 検索用インデックス
db.exec(`
  CREATE INDEX IF NOT EXISTS idx_entries_type ON entries(type);
  CREATE INDEX IF NOT EXISTS idx_entries_status ON entries(status);
  CREATE INDEX IF NOT EXISTS idx_entries_created ON entries(created_at);
`);

console.log('✨ Database created:', dbPath);
console.log('📊 Tables: entries, tags, entry_tags');

// 確認クエリ
const tables = db.prepare("SELECT name FROM sqlite_master WHERE type='table'").all();
console.log('📋 Tables:', tables.map(t => t.name).join(', '));

db.close();
