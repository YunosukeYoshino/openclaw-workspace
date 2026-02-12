#!/usr/bin/env python3
"""
服飾管理エージェント データベースモジュール
Wardrobe Management Agent Database Module
"""

import sqlite3
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import json


class ClothingDatabase:
    def __init__(self, db_path: str = "clothing.db"):
        self.db_path = db_path
        self.conn = None
        self.init_db()

    def connect(self):
        if self.conn is None:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row

    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None

    def init_db(self):
        self.connect()
        cursor = self.conn.cursor()

        # アイテムテーブル
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                brand TEXT,
                color TEXT,
                size TEXT,
                material TEXT,
                purchase_date TEXT,
                purchase_price REAL,
                condition TEXT DEFAULT 'good',
                location TEXT,
                image_url TEXT,
                notes TEXT,
                tags TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # カテゴリテーブル
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                color TEXT,
                icon TEXT,
                sort_order INTEGER DEFAULT 0
            )
        """)

        # アウトフィットテーブル
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS outfits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                items TEXT NOT NULL,
                season TEXT,
                occasion TEXT,
                favorite BOOLEAN DEFAULT 0,
                last_worn TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 着用記録テーブル
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS wear_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_id INTEGER,
                outfit_id INTEGER,
                worn_date TEXT NOT NULL,
                notes TEXT,
                FOREIGN KEY (item_id) REFERENCES items(id),
                FOREIGN KEY (outfit_id) REFERENCES outfits(id)
            )
        """)

        # ショッピングリストテーブル
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS shopping_list (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT,
                priority TEXT DEFAULT 'medium',
                budget REAL,
                notes TEXT,
                url TEXT,
                purchased BOOLEAN DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                purchased_at TEXT
            )
        """)

        # クローゼット整理テーブル
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS closet_organizer (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                location TEXT NOT NULL,
                capacity INTEGER,
                current_count INTEGER DEFAULT 0,
                notes TEXT
            )
        """)

        # インデックス
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_items_category ON items(category)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_items_tags ON items(tags)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_wear_logs_date ON wear_logs(worn_date)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_outfits_season ON outfits(season)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_shopping_priority ON shopping_list(priority)")

        # デフォルトカテゴリを挿入
        default_categories = [
            ("トップス", "#e74c3c", "👕", 1),
            ("ボトムス", "#3498db", "👖", 2),
            ("アウター", "#9b59b6", "🧥", 3),
            ("靴", "#f39c12", "👟", 4),
            ("アクセサリー", "#1abc9c", "💍", 5),
            ("インナー", "#e91e63", "👙", 6),
            ("バッグ", "#00bcd4", "👜", 7),
            ("帽子", "#ff5722", "🎩", 8),
            ("スカーフ/マフラー", "#607d8b", "🧣", 9),
        ]

        for cat in default_categories:
            cursor.execute("""
                INSERT OR IGNORE INTO categories (name, color, icon, sort_order)
                VALUES (?, ?, ?, ?)
            """, cat)

        self.conn.commit()

    def add_item(self, name: str, category: str, **kwargs) -> int:
        self.connect()
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO items (name, category, brand, color, size, material,
                              purchase_date, purchase_price, condition,
                              location, image_url, notes, tags)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (name, category, kwargs.get('brand'), kwargs.get('color'),
              kwargs.get('size'), kwargs.get('material'),
              kwargs.get('purchase_date'), kwargs.get('purchase_price'),
              kwargs.get('condition', 'good'), kwargs.get('location'),
              kwargs.get('image_url'), kwargs.get('notes'),
              kwargs.get('tags')))
        self.conn.commit()
        return cursor.lastrowid

    def get_items(self, category: Optional[str] = None) -> List[Dict]:
        self.connect()
        cursor = self.conn.cursor()
        if category:
            cursor.execute("SELECT * FROM items WHERE category = ?", (category,))
        else:
            cursor.execute("SELECT * FROM items ORDER BY created_at DESC")
        return [dict(row) for row in cursor.fetchall()]

    def add_outfit(self, name: str, item_ids: List[int], **kwargs) -> int:
        self.connect()
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO outfits (name, description, items, season, occasion, favorite)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (name, kwargs.get('description'), json.dumps(item_ids),
              kwargs.get('season'), kwargs.get('occasion'), kwargs.get('favorite', False)))
        self.conn.commit()
        return cursor.lastrowid

    def get_outfits(self) -> List[Dict]:
        self.connect()
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM outfits ORDER BY created_at DESC")
        return [dict(row) for row in cursor.fetchall()]

    def log_wear(self, item_id: Optional[int] = None, outfit_id: Optional[int] = None,
                 notes: Optional[str] = None, worn_date: Optional[str] = None) -> int:
        self.connect()
        cursor = self.conn.cursor()
        if worn_date is None:
            worn_date = datetime.now().isoformat()
        cursor.execute("""
            INSERT INTO wear_logs (item_id, outfit_id, worn_date, notes)
            VALUES (?, ?, ?, ?)
        """, (item_id, outfit_id, worn_date, notes))
        self.conn.commit()
        return cursor.lastrowid

    def get_wear_stats(self) -> Dict:
        self.connect()
        cursor = self.conn.cursor()

        # アイテム別着用回数
        cursor.execute("""
            SELECT i.name, i.category, COUNT(w.id) as wear_count
            FROM items i
            LEFT JOIN wear_logs w ON i.id = w.item_id
            GROUP BY i.id
            ORDER BY wear_count DESC
        """)
        item_stats = [dict(row) for row in cursor.fetchall()]

        # 最近の着用
        cursor.execute("""
            SELECT w.worn_date, i.name, o.name as outfit_name
            FROM wear_logs w
            LEFT JOIN items i ON w.item_id = i.id
            LEFT JOIN outfits o ON w.outfit_id = o.id
            ORDER BY w.worn_date DESC
            LIMIT 10
        """)
        recent_wears = [dict(row) for row in cursor.fetchall()]

        return {
            'item_stats': item_stats,
            'recent_wears': recent_wears
        }

    def add_to_shopping_list(self, name: str, **kwargs) -> int:
        self.connect()
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO shopping_list (name, category, priority, budget, notes, url)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (name, kwargs.get('category'), kwargs.get('priority', 'medium'),
              kwargs.get('budget'), kwargs.get('notes'), kwargs.get('url')))
        self.conn.commit()
        return cursor.lastrowid

    def get_shopping_list(self, purchased: Optional[bool] = None) -> List[Dict]:
        self.connect()
        cursor = self.conn.cursor()
        if purchased is not None:
            cursor.execute("""
                SELECT * FROM shopping_list WHERE purchased = ?
                ORDER BY priority DESC, created_at DESC
            """, (purchased,))
        else:
            cursor.execute("SELECT * FROM shopping_list ORDER BY priority DESC, created_at DESC")
        return [dict(row) for row in cursor.fetchall()]

    def get_summary(self) -> Dict:
        self.connect()
        cursor = self.conn.cursor()

        cursor.execute("SELECT COUNT(*) as total FROM items")
        total_items = cursor.fetchone()['total']

        cursor.execute("SELECT category, COUNT(*) as count FROM items GROUP BY category")
        by_category = {row['category']: row['count'] for row in cursor.fetchall()}

        cursor.execute("SELECT COUNT(*) as total FROM shopping_list WHERE purchased = 0")
        shopping_pending = cursor.fetchone()['total']

        cursor.execute("SELECT COUNT(*) as total FROM outfits")
        total_outfits = cursor.fetchone()['total']

        return {
            'total_items': total_items,
            'by_category': by_category,
            'shopping_pending': shopping_pending,
            'total_outfits': total_outfits
        }
