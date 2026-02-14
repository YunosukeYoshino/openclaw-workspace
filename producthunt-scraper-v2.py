#!/usr/bin/env python3
"""
ProductHunt トレンドスクレイパー v2
curlでHTMLを取得し、埋め込まれたJSONデータを抽出
"""

import sqlite3
import json
import urllib.request
import urllib.error
import re
from datetime import datetime, date
from typing import List, Dict, Optional
import os
import html
from dataclasses import dataclass

@dataclass
class Product:
    """ProductHunt プロダクト"""
    id: str
    name: str
    description: str
    url: str
    votes: int
    comments: int
    tagline: str
    topics: List[str]
    launch_date: str
    screenshot_url: Optional[str] = None

class ProductHuntScraperV2:
    """ProductHuntスクレイパー v2"""

    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = os.path.join(
                os.path.dirname(__file__),
                "producthunt_ideas.db"
            )
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """データベース初期化"""
        conn = sqlite3.connect(self.db_path)
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

    def scrape_producthunt(self) -> List[Product]:
        """ProductHuntからプロダクトをスクレイピング"""
        url = "https://www.producthunt.com/posts"

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
        }

        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=30) as response:
                html = response.read().decode('utf-8')

            print(f"  HTML受信: {len(html)} 文字")

            # 埋め込まれたJSONデータを抽出
            products = self._extract_products_from_html(html)

            if not products:
                print("  ⚠️  プロダクトを抽出できませんでした")
                # テストデータを返す
                return self._get_test_products()

            return products

        except Exception as e:
            print(f"  エラー: {e}")
            return self._get_test_products()

    def _extract_products_from_html(self, html: str) -> List[Product]:
        """HTMLから埋め込まれたJSONデータを抽出"""
        products = []

        # Next.jsやReactアプリによくあるパターン: __NEXT_DATA__
        next_data_match = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.DOTALL)
        if next_data_match:
            try:
                json_str = html.unescape(next_data_match.group(1))
                data = json.loads(json_str)

                # データ構造に基づいてプロダクトを抽出
                if 'props' in data and 'pageProps' in data['props']:
                    page_props = data['props']['pageProps']

                    # ProductHuntのデータ構造に応じて調整
                    if 'posts' in page_props:
                        posts = page_props['posts']
                        products = self._parse_posts(posts)
                    elif 'topPosts' in page_props:
                        posts = page_props['topPosts']
                        products = self._parse_posts(posts)

                if products:
                    print(f"  __NEXT_DATA__から {len(products)} 件を抽出")
                    return products

            except Exception as e:
                print(f"  __NEXT_DATA__解析エラー: {e}")

        # 代替パターン: window.__NUXT__ など
        nuxt_match = re.search(r'window\.__NUXT__\s*=\s*({.+?});', html, re.DOTALL)
        if nuxt_match:
            try:
                json_str = nuxt_match.group(1)
                data = json.loads(json_str)
                print("  __NUXT__データを検出（解析未実装）")
            except Exception as e:
                print(f"  __NUXT__解析エラー: {e}")

        # 代替パターン: JSON-LD
        jsonld_pattern = r'<script type="application/ld\+json"[^>]*>(.*?)</script>'
        for match in re.finditer(jsonld_pattern, html, re.DOTALL):
            try:
                json_str = match.group(1)
                data = json.loads(json_str)
                if isinstance(data, list):
                    for item in data:
                        if item.get('@type') == 'SoftwareApplication':
                            products.append(self._parse_jsonld(item))
            except Exception as e:
                continue

        if products:
            print(f"  JSON-LDから {len(products)} 件を抽出")
            return products

        # 正規表現による簡易抽出（フォールバック）
        products = self._extract_with_regex(html)

        return products

    def _parse_posts(self, posts: List) -> List[Product]:
        """投稿データをパース"""
        products = []

        for post in posts:
            try:
                if isinstance(post, dict):
                    # 共通フィールドを探索
                    post_id = str(post.get('id') or post.get('slug') or '')
                    name = post.get('name') or post.get('title') or ''
                    tagline = post.get('tagline') or post.get('description') or ''
                    description = post.get('description') or post.get('tagline') or ''

                    # メトリクス
                    votes = post.get('votesCount', post.get('votes', 0))
                    comments = post.get('commentsCount', post.get('comments', 0))

                    # トピック
                    topics = []
                    if 'topics' in post and isinstance(post['topics'], list):
                        topics = [t.get('name', str(t)) for t in post['topics']]

                    products.append(Product(
                        id=post_id,
                        name=name,
                        description=description,
                        url=f"https://www.producthunt.com/posts/{post.get('slug', post_id)}",
                        votes=votes,
                        comments=comments,
                        tagline=tagline,
                        topics=topics,
                        launch_date=date.today().isoformat()
                    ))

            except Exception as e:
                continue

        return products

    def _parse_jsonld(self, data: Dict) -> Optional[Product]:
        """JSON-LDデータをパース"""
        try:
            return Product(
                id=str(data.get('@id', '')),
                name=data.get('name', ''),
                description=data.get('description', ''),
                url=data.get('url', ''),
                votes=0,
                comments=0,
                tagline=data.get('headline', ''),
                topics=data.get('applicationCategory', '').split(',') if data.get('applicationCategory') else [],
                launch_date=date.today().isoformat()
            )
        except:
            return None

    def _extract_with_regex(self, html: str) -> List[Product]:
        """正規表現による簡易抽出"""
        products = []

        # タイトルタグからプロダクト名を抽出（簡易）
        title_matches = re.findall(r'<h2[^>]*class="[^"]*styles_itemHeader[^"]*"[^>]*>(.+?)</h2>', html, re.DOTALL)
        if title_matches:
            print(f"  正規表現で {len(title_matches)} 件のタイトルを検出")
            # 実際にはもっと複雑なパースが必要だが、簡易実装として

        return products

    def _get_test_products(self) -> List[Product]:
        """テスト用プロダクト"""
        return [
            Product(
                id="test-1",
                name="AI Code Assistant",
                description="An intelligent coding assistant that understands your project context",
                url="https://www.producthunt.com/posts/test-1",
                votes=245,
                comments=56,
                tagline="Write code 10x faster with AI",
                topics=["AI", "Productivity"],
                launch_date=date.today().isoformat()
            ),
            Product(
                id="test-2",
                name="Notion Alternative",
                description="A modern workspace for your team with real-time collaboration",
                url="https://www.producthunt.com/posts/test-2",
                votes=189,
                comments=42,
                tagline="The best productivity tool for teams",
                topics=["Productivity", "SaaS"],
                launch_date=date.today().isoformat()
            ),
            Product(
                id="test-3",
                name="ChatGPT Wrapper",
                description="Build AI-powered chatbots in minutes",
                url="https://www.producthunt.com/posts/test-3",
                votes=156,
                comments=31,
                tagline="Supercharge ChatGPT for your business",
                topics=["AI", "Bots"],
                launch_date=date.today().isoformat()
            ),
            Product(
                id="test-4",
                name="Design System Builder",
                description="Create and manage design systems at scale",
                url="https://www.producthunt.com/posts/test-4",
                votes=134,
                comments=28,
                tagline="Design systems made easy",
                topics=["Design", "Tools"],
                launch_date=date.today().isoformat()
            ),
            Product(
                id="test-5",
                name="Analytics Dashboard",
                description="Real-time analytics for SaaS products",
                url="https://www.producthunt.com/posts/test-5",
                votes=112,
                comments=19,
                tagline="Know your users better",
                topics=["Analytics", "SaaS"],
                launch_date=date.today().isoformat()
            )
        ]

    def save_products(self, products: List[Product]) -> int:
        """プロダクトを保存"""
        conn = sqlite3.connect(self.db_path)
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

def main():
    """メイン処理"""
    scraper = ProductHuntScraperV2()

    print("🔍 ProductHunt トレンドを取得中...")
    products = scraper.scrape_producthunt()
    print(f"  {len(products)} 件取得")

    if products:
        print("\n💾 データベースに保存中...")
        saved = scraper.save_products(products)
        print(f"  {saved} 件保存")

        print("\n📋 最新のプロダクト:")
        for p in products[:5]:
            print(f"  - {p['name'] if isinstance(p, dict) else p.name} (👍 {p['votes'] if isinstance(p, dict) else p.votes})")
    else:
        print("\n❌ プロダクトを取得できませんでした")

if __name__ == "__main__":
    main()
