#!/usr/bin/env python3
"""
game-esports-tournament-agent - ゲームeスポーツ大会エージェント。大会運営・管理。
"""

import sqlite3
import json
from datetime import datetime
from typing import Optional, Dict, List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GameEsportsTournamentAgent:
    """game-esports-tournament-agent"""

    def __init__(self, db_path: str = "game-esports-tournament-agent.db"):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """データベース初期化"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                content TEXT NOT NULL,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        conn.commit()
        conn.close()

    def add_entry(self, title: Optional[str], content: str, metadata: Optional[Dict] = None) -> int:
        """エントリー追加"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        metadata_json = json.dumps(metadata) if metadata else None

        cursor.execute('''
            INSERT INTO entries (title, content, metadata)
            VALUES (?, ?, ?)
        ''', (title, content, metadata_json))

        entry_id = cursor.lastrowid
        conn.commit()
        conn.close()

        logger.info(f"Entry added: ID={entry_id}")
        return entry_id

    def get_entry(self, entry_id: int) -> Optional[Dict]:
        """エントリー取得"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT id, title, content, metadata, created_at, updated_at
            FROM entries WHERE id = ?
        ''', (entry_id,))

        row = cursor.fetchone()
        conn.close()

        if row:
            return {
                "id": row[0],
                "title": row[1],
                "content": row[2],
                "metadata": json.loads(row[3]) if row[3] else None,
                "created_at": row[4],
                "updated_at": row[5]
            }
        return None

    def list_entries(self, limit: int = 100, offset: int = 0) -> List[Dict]:
        """エントリー一覧"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT id, title, content, metadata, created_at, updated_at
            FROM entries ORDER BY created_at DESC
            LIMIT ? OFFSET ?
        ''', (limit, offset))

        rows = cursor.fetchall()
        conn.close()

        return [{
            "id": row[0],
            "title": row[1],
            "content": row[2],
            "metadata": json.loads(row[3]) if row[3] else None,
            "created_at": row[4],
            "updated_at": row[5]
        } for row in rows]

    def update_entry(self, entry_id: int, title: Optional[str] = None,
                    content: Optional[str] = None, metadata: Optional[Dict] = None) -> bool:
        """エントリー更新"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        updates = []
        params = []

        if title is not None:
            updates.append("title = ?")
            params.append(title)
        if content is not None:
            updates.append("content = ?")
            params.append(content)
        if metadata is not None:
            updates.append("metadata = ?")
            params.append(json.dumps(metadata))

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
            SELECT id, title, content, metadata, created_at, updated_at
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
            "created_at": row[4],
            "updated_at": row[5]
        } for row in rows]


def main():
    """メイン関数"""
    agent = GameEsportsTournamentAgent()

    # サンプル実行
    entry_id = agent.add_entry(
        title="サンプル",
        content="ゲームeスポーツ大会エージェント。大会運営・管理。",
        metadata={"version": "1.0"}
    )

    print(f"Created entry: {entry_id}")

    entry = agent.get_entry(entry_id)
    print(f"Entry: {entry}")


if __name__ == "__main__":
    main()
