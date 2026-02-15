#!/usr/bin/env python3
"""
Hacker News トレンドスクレイパー
Hacker News APIを使用（認証不要）
"""

import sqlite3
import json
import urllib.request
from datetime import datetime, date
from typing import List, Dict, Optional
import os

class HackerNewsProduct:
    """Hacker News プロダクト"""
    def __init__(self, id: str, title: str, url: str, score: int, by: str, time: int, descendants: int = 0):
        self.id = str(id)
        self.name = title
        self.description = f"Posted by {by}"
        self.url = url or f"https://news.ycombinator.com/item?id={id}"
        self.votes = score
        self.comments = descendants
        self.tagline = title
        self.topics = ["Hacker News"]
        self.launch_date = datetime.fromtimestamp(time).strftime('%Y-%m-%d')
        self.screenshot_url = None

class HackerNewsScraper:
    """Hacker Newsスクレイパー"""

    HN_API_BASE = "https://hacker-news.firebaseio.com/v0"

    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = os.path.join(
                os.path.dirname(__file__),
                "data",
                "producthunt_ideas.db"
            )
        self.db_path = db_path
        self._init_db()

    def _connect(self):
        """データベース接続"""
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        """データベース初期化"""
        conn = self._connect()
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                url TEXT NOT NULL,
                votes INTEGER DEFAULT 0,
                comments INTEGER DEFAULT 0,
                tagline TEXT,
                topics TEXT,
                launch_date TEXT,
                screenshot_url TEXT,
                scraped_at TEXT NOT NULL,
                UNIQUE(id)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scrape_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                scraped_at TEXT NOT NULL,
                products_count INTEGER NOT NULL,
                error_message TEXT
            )
        ''')

        conn.commit()
        conn.close()

    def get_top_stories(self, limit: int = 30) -> List[HackerNewsProduct]:
        """トップストーリーを取得"""
        try:
            top_ids_url = f"{self.HN_API_BASE}/topstories.json"
            with urllib.request.urlopen(top_ids_url, timeout=30) as response:
                top_ids = json.loads(response.read().decode('utf-8'))

            stories = []
            for story_id in top_ids[:limit]:
                story = self._get_story(story_id)
                if story:
                    stories.append(story)

            return stories

        except Exception as e:
            print(f"  エラー: {e}")
            return []

    def _get_story(self, story_id: int) -> Optional[HackerNewsProduct]:
        """ストーリー詳細を取得"""
        try:
            story_url = f"{self.HN_API_BASE}/item/{story_id}.json"
            with urllib.request.urlopen(story_url, timeout=10) as response:
                story_data = json.loads(response.read().decode('utf-8'))

            if story_data.get('type') != 'story':
                return None

            return HackerNewsProduct(
                id=story_data['id'],
                title=story_data['title'],
                url=story_data.get('url'),
                score=story_data.get('score', 0),
                by=story_data.get('by', 'unknown'),
                time=story_data.get('time', 0),
                descendants=story_data.get('descendants', 0)
            )

        except Exception as e:
            return None

    def save_products(self, products: List[HackerNewsProduct]) -> int:
        """プロダクトを保存"""
        conn = self._connect()
        cursor = conn.cursor()

        scraped_at = datetime.now().isoformat()

        for product in products:
            cursor.execute('''
                INSERT OR REPLACE INTO products
                (id, name, description, url, votes, comments, tagline, topics, launch_date, screenshot_url, scraped_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                product.id,
                product.name,
                product.description,
                product.url,
                product.votes,
                product.comments,
                product.tagline,
                json.dumps(product.topics),
                product.launch_date,
                product.screenshot_url,
                scraped_at
            ))

        cursor.execute('''
            INSERT INTO scrape_logs (scraped_at, products_count)
            VALUES (?, ?)
        ''', (scraped_at, len(products)))

        conn.commit()
        conn.close()

        return len(products)

    def clear_db(self):
        """データベースをクリア"""
        conn = self._connect()
        cursor = conn.cursor()

        cursor.execute('DELETE FROM products')
        cursor.execute('DELETE FROM scrape_logs')

        conn.commit()
        conn.close()

    def get_recent_products(self, days: int = 3) -> List[Dict]:
        """最近N日のプロダクトを取得"""
        conn = self._connect()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM products
            WHERE scraped_at >= date('now', ?)
            ORDER BY votes DESC
        ''', (f"-{days} days",))

        columns = [desc[0] for desc in cursor.description]
        products = [dict(zip(columns, row)) for row in cursor.fetchall()]

        for p in products:
            if p['topics']:
                p['topics'] = json.loads(p['topics'])

        conn.close()
        return products

def main():
    """メイン処理"""
    scraper = HackerNewsScraper()

    print("🔍 Hacker News トレンドを取得中...")
    stories = scraper.get_top_stories(limit=20)
    print(f"  {len(stories)} 件取得")

    if stories:
        scraper.print_stories(stories)

        print("\n💾 データベースに保存中...")
        saved = scraper.save_products(stories)
        print(f"  {saved} 件保存")

        # JSONエクスポート
        export_path = os.path.join(
            os.path.dirname(__file__),
            f"hackernews_export_{date.today().isoformat()}.json"
        )

        export_data = []
        conn = scraper._connect()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM products
            WHERE id IN ({})
            ORDER BY votes DESC
        '''.format(','.join('?' * len(stories))), [s.id for s in stories])

        columns = [desc[0] for desc in cursor.description]
        for row in cursor.fetchall():
            p = dict(zip(columns, row))
            if p['topics']:
                p['topics'] = json.loads(p['topics'])
            export_data.append(p)

        with open(export_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)

        print(f"\n📄 エクスポート: {export_path}")

        # 統計
        cursor.execute('SELECT COUNT(*) FROM products')
        total = cursor.fetchone()[0]
        print(f"\n📊 データベース内の総プロダクト数: {total}")

        conn.close()
    else:
        print("\n❌ ストーリーを取得できませんでした")

if __name__ == "__main__":
    main()
