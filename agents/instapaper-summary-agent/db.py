#!/usr/bin/env python3
"""
Database Module for Instapaper Summary Agent
URLの重複チェック・管理のためのデータベース
"""

import os
import sqlite3
import logging
from datetime import datetime, timedelta
from typing import Optional

logger = logging.getLogger(__name__)


class Database:
    """データベース管理クラス"""

    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            db_path = os.getenv('INSTAPAPER_DB_PATH', 'instapaper_cache.db')

        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """データベースを初期化"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # テーブル作成
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS urls (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT UNIQUE NOT NULL,
                    title TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # インデックス作成
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_url ON urls(url)
            ''')
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_created_at ON urls(created_at)
            ''')

            conn.commit()
            conn.close()
            logger.info(f"Database initialized: {self.db_path}")

        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise

    def url_exists(self, url: str) -> bool:
        """URLが既に存在するかチェック"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('SELECT 1 FROM urls WHERE url = ? LIMIT 1', (url,))
            exists = cursor.fetchone() is not None

            conn.close()
            return exists

        except Exception as e:
            logger.error(f"Failed to check URL existence: {e}")
            return False

    def save_url(self, url: str, title: Optional[str] = None) -> bool:
        """URLを保存"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                INSERT OR IGNORE INTO urls (url, title)
                VALUES (?, ?)
            ''', (url, title))

            conn.commit()
            conn.close()
            logger.info(f"URL saved: {url}")
            return True

        except Exception as e:
            logger.error(f"Failed to save URL: {e}")
            return False

    def cleanup_old_entries(self, days: int = 30):
        """古いエントリーを削除"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cutoff_date = datetime.now() - timedelta(days=days)

            cursor.execute('''
                DELETE FROM urls
                WHERE created_at < ?
            ''', (cutoff_date.isoformat(),))

            deleted = cursor.rowcount
            conn.commit()
            conn.close()

            logger.info(f"Cleaned up {deleted} old entries (older than {days} days)")

        except Exception as e:
            logger.error(f"Failed to cleanup old entries: {e}")

    def get_all_urls(self) -> list:
        """全てのURLを取得"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('SELECT url, title, created_at FROM urls ORDER BY created_at DESC')
            rows = cursor.fetchall()

            conn.close()
            return rows

        except Exception as e:
            logger.error(f"Failed to get all URLs: {e}")
            return []

    def get_stats(self) -> dict:
        """統計情報を取得"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # 総数
            cursor.execute('SELECT COUNT(*) FROM urls')
            total = cursor.fetchone()[0]

            # 今日の数
            today = datetime.now().date()
            cursor.execute('''
                SELECT COUNT(*) FROM urls
                WHERE date(created_at) = ?
            ''', (today.isoformat(),))
            today_count = cursor.fetchone()[0]

            # 過去7日間の数
            week_ago = datetime.now() - timedelta(days=7)
            cursor.execute('''
                SELECT COUNT(*) FROM urls
                WHERE created_at >= ?
            ''', (week_ago.isoformat(),))
            week_count = cursor.fetchone()[0]

            conn.close()

            return {
                'total': total,
                'today': today_count,
                'week': week_count
            }

        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            return {'total': 0, 'today': 0, 'week': 0}
