"""
RSS Agent Database Module
SQLite-based data storage for RSS feed management
"""
import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional

class RSSDB:
    """Database manager for RSS agent"""

    def __init__(self, db_path: str = "rss.db"):
        self.db_path = db_path
        self.init_db()

    def get_connection(self) -> sqlite3.Connection:
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        """Initialize database tables"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS feeds (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                url TEXT NOT NULL UNIQUE,
                category TEXT,
                update_interval INTEGER DEFAULT 3600,
                last_checked TIMESTAMP,
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                feed_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                link TEXT NOT NULL,
                description TEXT,
                content TEXT,
                published_date TEXT,
                author TEXT,
                tags TEXT,
                is_read INTEGER DEFAULT 0,
                is_favorite INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (feed_id) REFERENCES feeds(id)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                feed_id INTEGER,
                article_id INTEGER NOT NULL,
                notification_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                message TEXT,
                FOREIGN KEY (feed_id) REFERENCES feeds(id),
                FOREIGN KEY (article_id) REFERENCES articles(id)
            )
        ''')

        conn.commit()
        conn.close()

    def add_feed(self, name: str, url: str, category: str = None, update_interval: int = 3600) -> int:
        """Add a new RSS feed"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('''
                INSERT INTO feeds (name, url, category, update_interval)
                VALUES (?, ?, ?, ?)
            ''', (name, url, category, update_interval))
            feed_id = cursor.lastrowid
            conn.commit()
            conn.close()
            return feed_id
        except sqlite3.IntegrityError:
            conn.close()
            return None

    def get_feeds(self, is_active: bool = None) -> List[Dict]:
        """Get all RSS feeds"""
        conn = self.get_connection()
        cursor = conn.cursor()

        if is_active is not None:
            cursor.execute("SELECT * FROM feeds WHERE is_active = ?", (1 if is_active else 0,))
        else:
            cursor.execute("SELECT * FROM feeds ORDER BY created_at DESC")

        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def get_feed(self, feed_id: int) -> Optional[Dict]:
        """Get a specific RSS feed"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM feeds WHERE id = ?", (feed_id,))
        row = cursor.fetchone()
        conn.close()

        return dict(row) if row else None

    def update_feed_check_time(self, feed_id: int):
        """Update the last checked time for a feed"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            UPDATE feeds SET last_checked = CURRENT_TIMESTAMP WHERE id = ?
        ''', (feed_id,))

        conn.commit()
        conn.close()

    def toggle_feed_active(self, feed_id: int) -> bool:
        """Toggle feed active status"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT is_active FROM feeds WHERE id = ?", (feed_id,))
        result = cursor.fetchone()

        if result:
            new_status = 0 if result['is_active'] == 1 else 1
            cursor.execute("UPDATE feeds SET is_active = ? WHERE id = ?", (new_status, feed_id))
            conn.commit()
            conn.close()
            return new_status == 1

        conn.close()
        return False

    def delete_feed(self, feed_id: int) -> bool:
        """Delete a feed and its articles"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("DELETE FROM articles WHERE feed_id = ?", (feed_id,))
            cursor.execute("DELETE FROM feeds WHERE id = ?", (feed_id,))
            conn.commit()
            conn.close()
            return True
        except:
            conn.close()
            return False

    def add_article(self, feed_id: int, title: str, link: str, description: str = None,
                    content: str = None, published_date: str = None, author: str = None,
                    tags: str = None) -> int:
        """Add a new article"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Check if article already exists
        cursor.execute("SELECT id FROM articles WHERE link = ?", (link,))
        if cursor.fetchone():
            conn.close()
            return None

        cursor.execute('''
            INSERT INTO articles (feed_id, title, link, description, content, published_date, author, tags)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (feed_id, title, link, description, content, published_date, author, tags))

        article_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return article_id

    def get_articles(self, feed_id: int = None, is_read: bool = None, is_favorite: bool = None,
                    limit: int = 50) -> List[Dict]:
        """Get articles with optional filters"""
        conn = self.get_connection()
        cursor = conn.cursor()

        query = "SELECT * FROM articles WHERE 1=1"
        params = []

        if feed_id:
            query += " AND feed_id = ?"
            params.append(feed_id)

        if is_read is not None:
            query += " AND is_read = ?"
            params.append(1 if is_read else 0)

        if is_favorite is not None:
            query += " AND is_favorite = ?"
            params.append(1 if is_favorite else 0)

        query += " ORDER BY published_date DESC, created_at DESC LIMIT ?"
        params.append(limit)

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def mark_article_read(self, article_id: int) -> bool:
        """Mark an article as read"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("UPDATE articles SET is_read = 1 WHERE id = ?", (article_id,))
        conn.commit()
        conn.close()
        return True

    def mark_article_favorite(self, article_id: int) -> bool:
        """Mark an article as favorite"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("UPDATE articles SET is_favorite = 1 WHERE id = ?", (article_id,))
        conn.commit()
        conn.close()
        return True

    def get_unread_articles(self, feed_id: int = None, limit: int = 20) -> List[Dict]:
        """Get unread articles"""
        return self.get_articles(feed_id=feed_id, is_read=False, limit=limit)

    def create_notification(self, feed_id: int, article_id: int, message: str = None) -> int:
        """Create a notification log"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO notifications (feed_id, article_id, message)
            VALUES (?, ?, ?)
        ''', (feed_id, article_id, message))

        notif_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return notif_id

    def get_feed_stats(self, feed_id: int = None) -> Dict:
        """Get statistics for feeds"""
        conn = self.get_connection()
        cursor = conn.cursor()

        if feed_id:
            cursor.execute('''
                SELECT
                    COUNT(*) as total_articles,
                    SUM(CASE WHEN is_read = 0 THEN 1 ELSE 0 END) as unread_count,
                    SUM(CASE WHEN is_favorite = 1 THEN 1 ELSE 0 END) as favorite_count
                FROM articles WHERE feed_id = ?
            ''', (feed_id,))
        else:
            cursor.execute('''
                SELECT
                    COUNT(*) as total_articles,
                    SUM(CASE WHEN is_read = 0 THEN 1 ELSE 0 END) as unread_count,
                    SUM(CASE WHEN is_favorite = 1 THEN 1 ELSE 0 END) as favorite_count
                FROM articles
            ''')

        result = cursor.fetchone()
        conn.close()
        return dict(result) if result else {}
