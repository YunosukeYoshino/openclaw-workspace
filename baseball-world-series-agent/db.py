#!/usr/bin/env python3
"""
baseball-world-series-agent - データベース管理モジュール
"""

import sqlite3
import json
from datetime import datetime
from typing import Optional, Dict, List, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseManager:
    """データベース管理クラス"""

    def __init__(self, db_path: str = "baseball-world-series-agent.db"):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """データベース初期化"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # エントリーテーブル
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                content TEXT NOT NULL,
                metadata TEXT,
                status TEXT DEFAULT 'active',
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

        # エントリータグ関連テーブル
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS entry_tags (
                entry_id INTEGER,
                tag_id INTEGER,
                PRIMARY KEY (entry_id, tag_id),
                FOREIGN KEY (entry_id) REFERENCES entries(id) ON DELETE CASCADE,
                FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
            )
        ''')

        conn.commit()
        conn.close()

    def add_entry(self, title: Optional[str], content: str,
                  metadata: Optional[Dict] = None, tags: Optional[List[str]] = None) -> int:
        """エントリー追加"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        metadata_json = json.dumps(metadata) if metadata else None

        cursor.execute('''
            INSERT INTO entries (title, content, metadata)
            VALUES (?, ?, ?)
        ''', (title, content, metadata_json))

        entry_id = cursor.lastrowid

        # タグを追加
        if tags:
            for tag_name in tags:
                tag_id = self._get_or_create_tag(cursor, tag_name)
                cursor.execute('''
                    INSERT INTO entry_tags (entry_id, tag_id)
                    VALUES (?, ?)
                ''', (entry_id, tag_id))

        conn.commit()
        conn.close()

        logger.info(f"Entry added: ID={entry_id}")
        return entry_id

    def _get_or_create_tag(self, cursor, tag_name: str) -> int:
        """タグ取得または作成"""
        cursor.execute('SELECT id FROM tags WHERE name = ?', (tag_name,))
        row = cursor.fetchone()

        if row:
            return row[0]

        cursor.execute('INSERT INTO tags (name) VALUES (?)', (tag_name,))
        return cursor.lastrowid

    def get_entry(self, entry_id: int) -> Optional[Dict]:
        """エントリー取得"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT id, title, content, metadata, status, created_at, updated_at
            FROM entries WHERE id = ?
        ''', (entry_id,))

        row = cursor.fetchone()

        if not row:
            conn.close()
            return None

        # タグを取得
        cursor.execute('''
            SELECT t.name FROM tags t
            JOIN entry_tags et ON t.id = et.tag_id
            WHERE et.entry_id = ?
        ''', (entry_id,))
        tags = [tag_row[0] for tag_row in cursor.fetchall()]

        conn.close()

        return {
            "id": row[0],
            "title": row[1],
            "content": row[2],
            "metadata": json.loads(row[3]) if row[3] else None,
            "status": row[4],
            "tags": tags,
            "created_at": row[5],
            "updated_at": row[6]
        }

    def list_entries(self, status: Optional[str] = None,
                     limit: int = 100, offset: int = 0) -> List[Dict]:
        """エントリー一覧"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        if status:
            cursor.execute('''
                SELECT id, title, content, metadata, status, created_at, updated_at
                FROM entries WHERE status = ?
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
            ''', (status, limit, offset))
        else:
            cursor.execute('''
                SELECT id, title, content, metadata, status, created_at, updated_at
                FROM entries
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
            ''', (limit, offset))

        rows = cursor.fetchall()
        conn.close()

        return [{
            "id": row[0],
            "title": row[1],
            "content": row[2],
            "metadata": json.loads(row[3]) if row[3] else None,
            "status": row[4],
            "created_at": row[5],
            "updated_at": row[6]
        } for row in rows]

    def update_entry(self, entry_id: int, **kwargs) -> bool:
        """エントリー更新"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        updates = []
        params = []

        if 'title' in kwargs:
            updates.append("title = ?")
            params.append(kwargs['title'])
        if 'content' in kwargs:
            updates.append("content = ?")
            params.append(kwargs['content'])
        if 'metadata' in kwargs:
            updates.append("metadata = ?")
            params.append(json.dumps(kwargs['metadata']))
        if 'status' in kwargs:
            updates.append("status = ?")
            params.append(kwargs['status'])

        if not updates:
            conn.close()
            return False

        updates.append("updated_at = ?")
        params.append(datetime.now().isoformat())
        params.append(entry_id)

        cursor.execute(f'''
            UPDATE entries SET {', '.join(updates)}
            WHERE id = ?
        ''', params)

        conn.commit()
        conn.close()

        return cursor.rowcount > 0

    def delete_entry(self, entry_id: int) -> bool:
        """エントリー削除"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('DELETE FROM entries WHERE id = ?', (entry_id,))

        conn.commit()
        conn.close()

        return cursor.rowcount > 0

    def search_entries(self, query: str, limit: int = 100) -> List[Dict]:
        """エントリー検索"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT id, title, content, metadata, status, created_at, updated_at
            FROM entries
            WHERE title LIKE ? OR content LIKE ?
            ORDER BY created_at DESC
            LIMIT ?
        ''', (f'%{query}%', f'%{query}%', limit))

        rows = cursor.fetchall()
        conn.close()

        return [{
            "id": row[0],
            "title": row[1],
            "content": row[2],
            "metadata": json.loads(row[3]) if row[3] else None,
            "status": row[4],
            "created_at": row[5],
            "updated_at": row[6]
        } for row in rows]

    def get_stats(self) -> Dict:
        """統計情報取得"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('SELECT COUNT(*) FROM entries')
        total_entries = cursor.fetchone()[0]

        cursor.execute('SELECT COUNT(*) FROM tags')
        total_tags = cursor.fetchone()[0]

        cursor.execute("SELECT status, COUNT(*) FROM entries GROUP BY status")
        status_counts = {row[0]: row[1] for row in cursor.fetchall()}

        conn.close()

        return {
            "total_entries": total_entries,
            "total_tags": total_tags,
            "status_counts": status_counts
        }


def main():
    """メイン関数"""
    db = DatabaseManager()

    stats = db.get_stats()
    print(f"Stats: {json.dumps(stats, indent=2, ensure_ascii=False)}")


if __name__ == "__main__":
    main()
