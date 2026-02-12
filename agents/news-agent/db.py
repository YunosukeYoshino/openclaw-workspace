"""
Database management for News Agent
SQLite-based storage for news articles, user preferences, and categories
"""

import sqlite3
from datetime import datetime
from typing import List, Dict, Optional


class NewsDatabase:
    """Manages SQLite database for news agent"""

    def __init__(self, db_path: str = "news_agent.db"):
        self.db_path = db_path
        self.init_db()

    def get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        """Initialize database tables"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # User preferences
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_preferences (
                    user_id TEXT PRIMARY KEY,
                    language TEXT DEFAULT 'ja',
                    interests TEXT,
                    notification_enabled INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Categories
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    name_en TEXT NOT NULL,
                    name_ja TEXT NOT NULL,
                    UNIQUE(name)
                )
            """)

            # News articles
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS articles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    content TEXT,
                    summary TEXT,
                    url TEXT,
                    category_id INTEGER,
                    source TEXT,
                    published_at TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (category_id) REFERENCES categories(id)
                )
            """)

            # User-news interactions
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_article_interactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    article_id INTEGER NOT NULL,
                    read INTEGER DEFAULT 0,
                    liked INTEGER DEFAULT 0,
                    saved INTEGER DEFAULT 0,
                    shared INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (article_id) REFERENCES articles(id),
                    UNIQUE(user_id, article_id)
                )
            """)

            # Notifications
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS notifications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    article_id INTEGER NOT NULL,
                    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (article_id) REFERENCES articles(id)
                )
            """)

            conn.commit()

            # Initialize default categories if empty
            self._init_default_categories(cursor)
            conn.commit()

    def _init_default_categories(self, cursor):
        """Initialize default news categories"""
        default_categories = [
            ("technology", "Technology", "テクノロジー"),
            ("business", "Business", "ビジネス"),
            ("sports", "Sports", "スポーツ"),
            ("entertainment", "Entertainment", "エンターテイメント"),
            ("science", "Science", "科学"),
            ("health", "Health", "健康"),
            ("politics", "Politics", "政治"),
            ("world", "World", "世界")
        ]

        for name, name_en, name_ja in default_categories:
            cursor.execute("""
                INSERT OR IGNORE INTO categories (name, name_en, name_ja)
                VALUES (?, ?, ?)
            """, (name, name_en, name_ja))

    # User Preferences
    def save_user_preferences(self, user_id: str, language: str = 'ja',
                             interests: str = None, notification_enabled: bool = True) -> bool:
        """Save or update user preferences"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO user_preferences (user_id, language, interests, notification_enabled, updated_at)
                    VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
                    ON CONFLICT(user_id) DO UPDATE SET
                        language = excluded.language,
                        interests = excluded.interests,
                        notification_enabled = excluded.notification_enabled,
                        updated_at = CURRENT_TIMESTAMP
                """, (user_id, language, interests, int(notification_enabled)))
                conn.commit()
                return True
        except Exception as e:
            print(f"Error saving preferences: {e}")
            return False

    def get_user_preferences(self, user_id: str) -> Optional[Dict]:
        """Get user preferences"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT user_id, language, interests, notification_enabled
                    FROM user_preferences WHERE user_id = ?
                """, (user_id,))
                row = cursor.fetchone()
                if row:
                    return {
                        'user_id': row['user_id'],
                        'language': row['language'],
                        'interests': row['interests'],
                        'notification_enabled': bool(row['notification_enabled'])
                    }
                return None
        except Exception as e:
            print(f"Error getting preferences: {e}")
            return None

    # Articles
    def add_article(self, title: str, content: str, url: str, category: str,
                   source: str, published_at: datetime = None) -> Optional[int]:
        """Add a new article"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                # Get category ID
                cursor.execute("SELECT id FROM categories WHERE name = ?", (category,))
                category_row = cursor.fetchone()
                if not category_row:
                    # Create category if doesn't exist
                    cursor.execute("""
                        INSERT INTO categories (name, name_en, name_ja)
                        VALUES (?, ?, ?)
                    """, (category, category, category))
                    category_id = cursor.lastrowid
                else:
                    category_id = category_row['id']

                cursor.execute("""
                    INSERT INTO articles (title, content, url, category_id, source, published_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (title, content, url, category_id, source, published_at or datetime.now()))

                conn.commit()
                return cursor.lastrowid
        except Exception as e:
            print(f"Error adding article: {e}")
            return None

    def get_articles(self, category: str = None, limit: int = 20,
                    user_id: str = None) -> List[Dict]:
        """Get articles, optionally filtered by category and user interests"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                if category:
                    cursor.execute("""
                        SELECT a.*, c.name_en, c.name_ja
                        FROM articles a
                        JOIN categories c ON a.category_id = c.id
                        WHERE c.name = ?
                        ORDER BY a.published_at DESC
                        LIMIT ?
                    """, (category, limit))
                else:
                    cursor.execute("""
                        SELECT a.*, c.name_en, c.name_ja
                        FROM articles a
                        JOIN categories c ON a.category_id = c.id
                        ORDER BY a.published_at DESC
                        LIMIT ?
                    """, (limit,))

                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            print(f"Error getting articles: {e}")
            return []

    def update_article_summary(self, article_id: int, summary: str) -> bool:
        """Update article summary"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE articles SET summary = ? WHERE id = ?
                """, (summary, article_id))
                conn.commit()
                return True
        except Exception as e:
            print(f"Error updating summary: {e}")
            return False

    # Categories
    def get_categories(self, language: str = 'en') -> List[Dict]:
        """Get all categories in specified language"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                name_field = 'name_en' if language == 'en' else 'name_ja'
                cursor.execute(f"""
                    SELECT id, name, {name_field} as display_name
                    FROM categories
                """)
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            print(f"Error getting categories: {e}")
            return []

    # Notifications
    def add_notification(self, user_id: str, article_id: int) -> bool:
        """Record a notification sent to user"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO notifications (user_id, article_id)
                    VALUES (?, ?)
                """, (user_id, article_id))
                conn.commit()
                return True
        except Exception as e:
            print(f"Error adding notification: {e}")
            return False


# Initialize database
if __name__ == "__main__":
    db = NewsDatabase()
    print("News Agent Database initialized successfully!")
    print(f"Categories: {db.get_categories()}")
