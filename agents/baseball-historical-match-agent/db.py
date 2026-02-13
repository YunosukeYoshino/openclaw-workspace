#!/usr/bin/env python3
"""
野球歴史的名試合エージェント データベースモジュール
"""

import aiosqlite
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

class BaseballHistoricalMatchAgentDB:
    """野球歴史的名試合エージェント データベース管理"""

    def __init__(self, db_path=None, logger=None):
        if db_path is None:
            db_path = Path("data/baseball-historical-match-agent.db")
        self.db_path = str(db_path)
        self.logger = logger or logging.getLogger(__name__)
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

    async def initialize(self):
        """データベースを初期化"""
        self.connection = await aiosqlite.connect(self.db_path)
        await self._create_tables()
        await self._create_indexes()
        self.logger.info(f"Database initialized: {self.db_path}")

    async def _create_tables(self):
        """テーブルを作成"""
        await self.connection.execute("""
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                content TEXT,
                category TEXT,
                tags TEXT,
                metadata TEXT,
                user_id TEXT,
                rating REAL DEFAULT 0,
                view_count INTEGER DEFAULT 0,
                is_public BOOLEAN DEFAULT 0,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        await self.connection.execute("""
            CREATE TABLE IF NOT EXISTS tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        await self.connection.execute("""
            CREATE TABLE IF NOT EXISTS item_tags (
                item_id INTEGER,
                tag_id INTEGER,
                PRIMARY KEY (item_id, tag_id),
                FOREIGN KEY (item_id) REFERENCES items(id) ON DELETE CASCADE,
                FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
            )
        """)

        await self.connection.execute("""
            CREATE TABLE IF NOT EXISTS favorites (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                item_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (item_id) REFERENCES items(id) ON DELETE CASCADE,
                UNIQUE(user_id, item_id)
            )
        """)

        await self.connection.execute("""
            CREATE TABLE IF NOT EXISTS activity_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                action TEXT NOT NULL,
                item_id INTEGER,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        await self.connection.commit()

    async def _create_indexes(self):
        """インデックスを作成"""
        indexes = [
            'CREATE INDEX IF NOT EXISTS idx_items_category ON items(category)',
            'CREATE INDEX IF NOT EXISTS idx_items_status ON items(status)',
            'CREATE INDEX IF NOT EXISTS idx_items_rating ON items(rating)',
            'CREATE INDEX IF NOT EXISTS idx_items_created_at ON items(created_at)',
            'CREATE INDEX IF NOT EXISTS idx_activity_log_user_id ON activity_log(user_id)',
            'CREATE INDEX IF NOT EXISTS idx_activity_log_action ON activity_log(action)',
            'CREATE INDEX IF NOT EXISTS idx_favorites_user_id ON favorites(user_id)'
        ]

        for index in indexes:
            await self.connection.execute(index)
        await self.connection.commit()

    async def add(self, data: Dict[str, Any]) -> int:
        """アイテムを追加"""
        async with self.connection.execute('''
            INSERT INTO items (title, description, content, category, tags, metadata, user_id, rating, is_public)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data.get('title', ''),
            data.get('description', ''),
            data.get('content', ''),
            data.get('category', 'general'),
            json.dumps(data.get('tags', [])),
            json.dumps(data.get('metadata', {})),
            data.get('user_id'),
            data.get('rating', 0),
            data.get('is_public', False)
        )) as cursor:
            item_id = cursor.lastrowid
            await self.connection.commit()

            if 'tags' in data:
                await self._add_tags(item_id, data['tags'])

            await self._log_activity(data.get('user_id'), 'add', item_id)

            return item_id

    async def update(self, item_id: int, data: Dict[str, Any]) -> bool:
        """アイテムを更新"""
        update_fields = []
        values = []

        for field in ['title', 'description', 'content', 'category', 'rating', 'is_public', 'status']:
            if field in data:
                update_fields.append(f"{field} = ?")
                values.append(data[field])

        if not update_fields:
            return False

        update_fields.append("updated_at = CURRENT_TIMESTAMP")
        values.append(item_id)

        await self.connection.execute(f'''
            UPDATE items SET {', '.join(update_fields)}
            WHERE id = ?
        ''', values)

        await self.connection.commit()

        if 'tags' in data:
            await self._update_tags(item_id, data['tags'])

        await self._log_activity(None, 'update', item_id)

        return True

    async def delete(self, item_id: int) -> bool:
        """アイテムを削除"""
        await self.connection.execute('DELETE FROM items WHERE id = ?', (item_id,))
        await self.connection.commit()
        return True

    async def get(self, item_id: int) -> Optional[Dict[str, Any]]:
        """アイテムを取得"""
        async with self.connection.execute('''
            SELECT * FROM items WHERE id = ?
        ''', (item_id,)) as cursor:
            row = await cursor.fetchone()
            if row:
                return await self._row_to_dict(cursor, row)
        return None

    async def search(self, query: str, category: str = None, limit: int = 20) -> List[Dict[str, Any]]:
        """検索"""
        search_pattern = f'%{query}%'

        if category:
            async with self.connection.execute('''
                SELECT * FROM items
                WHERE (title LIKE ? OR description LIKE ? OR content LIKE ?)
                AND category = ?
                AND status = 'active'
                ORDER BY rating DESC, created_at DESC
                LIMIT ?
            ''', (search_pattern, search_pattern, search_pattern, category, limit)) as cursor:
                rows = await cursor.fetchall()
                return await self._rows_to_dicts(cursor, rows)
        else:
            async with self.connection.execute('''
                SELECT * FROM items
                WHERE (title LIKE ? OR description LIKE ? OR content LIKE ?)
                AND status = 'active'
                ORDER BY rating DESC, created_at DESC
                LIMIT ?
            ''', (search_pattern, search_pattern, search_pattern, limit)) as cursor:
                rows = await cursor.fetchall()
                return await self._rows_to_dicts(cursor, rows)

    async def get_statistics(self) -> Dict[str, Any]:
        """統計情報を取得"""
        async with self.connection.execute('SELECT COUNT(*) FROM items WHERE status = "active"') as cursor:
            total_items = (await cursor.fetchone())[0]

        async with self.connection.execute('SELECT category, COUNT(*) FROM items WHERE status = "active" GROUP BY category') as cursor:
            by_category = dict(await cursor.fetchall())

        async with self.connection.execute('SELECT AVG(rating) FROM items WHERE status = "active" AND rating > 0') as cursor:
            avg_rating = (await cursor.fetchone())[0] or 0

        async with self.connection.execute('SELECT COUNT(DISTINCT user_id) FROM items') as cursor:
            total_users = (await cursor.fetchone())[0]

        async with self.connection.execute('SELECT COUNT(*) FROM tags') as cursor:
            total_tags = (await cursor.fetchone())[0]

        return {
            "total_items": total_items,
            "by_category": by_category,
            "average_rating": round(avg_rating, 2),
            "total_users": total_users,
            "total_tags": total_tags
        }

    async def get_recommendations(self, user_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """おすすめを取得"""
        async with self.connection.execute('''
            SELECT * FROM items
            WHERE id NOT IN (SELECT item_id FROM favorites WHERE user_id = ?)
            AND status = 'active'
            AND is_public = 1
            ORDER BY rating DESC, view_count DESC
            LIMIT ?
        ''', (user_id, limit)) as cursor:
            rows = await cursor.fetchall()
            return await self._rows_to_dicts(cursor, rows)

    async def get_trending(self, limit: int = 10) -> List[Dict[str, Any]]:
        """トレンドを取得"""
        async with self.connection.execute('''
            SELECT * FROM items
            WHERE status = 'active'
            ORDER BY view_count DESC, rating DESC
            LIMIT ?
        ''', (limit,)) as cursor:
            rows = await cursor.fetchall()
            return await self._rows_to_dicts(cursor, rows)

    async def get_related(self, item_id: int, limit: int = 5) -> List[Dict[str, Any]]:
        """関連アイテムを取得"""
        item = await self.get(item_id)
        if not item:
            return []

        async with self.connection.execute('''
            SELECT * FROM items
            WHERE category = ?
            AND id != ?
            AND status = 'active'
            ORDER BY rating DESC
            LIMIT ?
        ''', (item.get('category'), item_id, limit)) as cursor:
            rows = await cursor.fetchall()
            return await self._rows_to_dicts(cursor, rows)

    async def _add_tags(self, item_id: int, tags: List[str]):
        """タグを追加"""
        for tag_name in tags:
            async with self.connection.execute(
                'SELECT id FROM tags WHERE name = ?',
                (tag_name,)
            ) as cursor:
                row = await cursor.fetchone()
                if row:
                    tag_id = row[0]
                    await self.connection.execute(
                        'UPDATE tags SET count = count + 1 WHERE id = ?',
                        (tag_id,)
                    )
                else:
                    await self.connection.execute(
                        'INSERT INTO tags (name, count) VALUES (?, 1)',
                        (tag_name,)
                    )
                    tag_id = cursor.lastrowid

            try:
                await self.connection.execute(
                    'INSERT INTO item_tags (item_id, tag_id) VALUES (?, ?)',
                    (item_id, tag_id)
                )
            except:
                pass

        await self.connection.commit()

    async def _update_tags(self, item_id: int, tags: List[str]):
        """タグを更新"""
        await self.connection.execute(
            'DELETE FROM item_tags WHERE item_id = ?',
            (item_id,)
        )
        await self._add_tags(item_id, tags)

    async def _log_activity(self, user_id: Optional[str], action: str, item_id: Optional[int]):
        """アクティビティを記録"""
        await self.connection.execute('''
            INSERT INTO activity_log (user_id, action, item_id)
            VALUES (?, ?, ?)
        ''', (user_id, action, item_id))
        await self.connection.commit()

    async def _rows_to_dicts(self, cursor, rows) -> List[Dict[str, Any]]:
        """行を辞書に変換"""
        results = []
        for row in rows:
            results.append(await self._row_to_dict(cursor, row))
        return results

    async def _row_to_dict(self, cursor, row) -> Dict[str, Any]:
        """行を辞書に変換"""
        columns = [description[0] for description in cursor.description]
        result = dict(zip(columns, row))

        for field in ['tags', 'metadata']:
            if field in result and result[field]:
                try:
                    result[field] = json.loads(result[field])
                except:
                    pass

        return result

    async def close(self):
        """接続を閉じる"""
        await self.connection.close()
        self.logger.info("Database connection closed")
