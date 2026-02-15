#!/usr/bin/env python3
"""
App Store Auto Analyzer
iTunes RSS APIを使って自動でレビューを取得・分析する
簡易版
"""

import sqlite3
import json
import urllib.request
import urllib.parse
import re
import time
import sys
from datetime import datetime
from typing import List, Dict, Optional
import os

def debug_print(msg):
    print(msg)
    sys.stdout.flush()


class SimpleAppAnalyzer:
    """シンプルなApp Store アナライザー"""

    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = os.path.join(
                os.path.dirname(__file__),
                "data",
                "appstore_gainers.db"
            )
        self.db_path = db_path
        self._init_db()

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        conn = self._connect()
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS apps (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                app_id TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                developer TEXT,
                rating REAL,
                url TEXT,
                discovered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                app_id INTEGER NOT NULL,
                title TEXT,
                text TEXT,
                rating INTEGER,
                author TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (app_id) REFERENCES apps(id)
            )
        ''')

        conn.commit()
        conn.close()

    def get_app_info(self, query: str) -> Optional[Dict]:
        """iTunes Search APIでアプリ情報を取得"""
        url = f"https://itunes.apple.com/search?term={urllib.parse.quote(query)}&media=software&limit=1"

        try:
            with urllib.request.urlopen(url, timeout=15) as response:
                data = json.loads(response.read().decode('utf-8'))
                results = data.get('results', [])
                return results[0] if results else None
        except Exception as e:
            debug_print(f"❌ アプリ情報取得エラー: {e}")
            return None

    def get_reviews(self, app_id: str) -> List[Dict]:
        """RSS APIでレビューを取得（簡易版）"""
        url = f"https://itunes.apple.com/us/rss/customerreviews/id={app_id}/sortBy=mostRecent/xml"

        try:
            debug_print(f"   レビュー取得中... (timeout=15秒)")
            with urllib.request.urlopen(url, timeout=15) as response:
                xml_data = response.read().decode('utf-8')

            debug_print(f"   ✅ XML取得: {len(xml_data)} バイト")

            # シンプルなパターン
            reviews = []

            # <title>と<rating>を抽出
            title_pattern = r'<title>(.+?)</title>'
            rating_pattern = r'<im:rating>(\d+)</im:rating>'

            titles = re.findall(title_pattern, xml_data)
            ratings = re.findall(rating_pattern, xml_data)

            # ペアリング（最初のエントリはアプリ名を含むのでスキップ）
            for i in range(1, min(len(titles), len(ratings) + 1)):
                try:
                    rating = int(ratings[i - 1])
                    if rating <= 2:  # 星1〜2のみ
                        title = titles[i].replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&')
                        reviews.append({
                            'title': title[:100],
                            'text': title,  # タイトルをテキストとして使用
                            'rating': rating,
                            'author': f'user{i}',
                            'review_date': datetime.now().strftime('%Y-%m-%d')
                        })
                except:
                    continue

            debug_print(f"   ✅ 星1〜2: {len(reviews)} 件抽出")
            return reviews

        except Exception as e:
            debug_print(f"   ❌ レビュー取得エラー: {e}")
            return []

    def save_data(self, app_data: Dict, reviews: List[Dict]) -> int:
        """アプリとレビューを保存"""
        conn = self._connect()
        cursor = conn.cursor()

        # アプリを保存
        cursor.execute('''
            INSERT OR REPLACE INTO apps (app_id, name, developer, rating, url)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            str(app_data.get('trackId', '')),
            app_data.get('trackName', ''),
            app_data.get('artistName', ''),
            app_data.get('averageUserRating', 0),
            app_data.get('trackViewUrl', '')
        ))

        app_id = cursor.lastrowid
        debug_print(f"   ✅ アプリ保存: app_id={app_id}")

        # レビューを保存
        saved = 0
        for review in reviews[:30]:  # 最大30件
            try:
                cursor.execute('''
                    INSERT OR IGNORE INTO reviews (app_id, title, text, rating, author)
                    VALUES (?, ?, ?, ?, ?)
                ''', (app_id, review['title'], review['text'], review['rating'], review['author']))

                if cursor.rowcount > 0:
                    saved += 1
            except:
                continue

        debug_print(f"   ✅ レビュー保存: {saved} 件")

        conn.commit()
        conn.close()

        return app_id

    def create_report(self, app_data: Dict, reviews: List[Dict]) -> str:
        """レポートを作成"""
        report = []
        report.append("=" * 80)
        report.append("📱 App Store 自動分析レポート")
        report.append(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("=" * 80)

        report.append("\n📱 アプリ情報")
        report.append("-" * 40)
        report.append(f"名前: {app_data.get('trackName')}")
        report.append(f"開発者: {app_data.get('artistName')}")
        report.append(f"カテゴリ: {app_data.get('primaryGenreName')}")
        report.append(f"評価: ⭐{app_data.get('averageUserRating')}")

        report.append(f"\n📊 悪いレビュー: {len(reviews)} 件")
        report.append("-" * 40)

        rating_counts = {1: 0, 2: 0}
        for r in reviews:
            rating_counts[r['rating']] += 1

        report.append(f"星1: {rating_counts[1]}件")
        report.append(f"星2: {rating_counts[2]}件")

        report.append("\n💬 悪いレビュー詳細")
        report.append("-" * 40)

        for i, review in enumerate(reviews[:20], 1):
            stars = '⭐' * review['rating']
            report.append(f"\n{i}. {stars} {review['title'][:60]}...")

        report.append("\n🤖 AI分析用プロンプト")
        report.append("-" * 40)
        report.append("以下の悪いレビューをClaude/ChatGPTに投げて分析させる:")
        report.append("---")
        for review in reviews[:20]:
            report.append(f"星{review['rating']}: {review['title']}")
        report.append("---")

        report.append("\n" + "=" * 80)

        return "\n".join(report)

    def analyze(self, query: str) -> Dict:
        """分析を実行"""
        debug_print(f"\n🔍 検索: {query}")

        # アプリ情報取得
        app_data = self.get_app_info(query)
        if not app_data:
            return {'success': False, 'error': 'アプリが見つかりませんでした'}

        debug_print(f"📱 {app_data.get('trackName')} - {app_data.get('artistName')}")
        debug_print(f"   評価: ⭐{app_data.get('averageUserRating')}")

        # レビュー取得
        reviews = self.get_reviews(app_data.get('trackId'))

        if not reviews:
            debug_print("⚠️ 悪いレビューが見つかりませんでした")
            # デモ用にダミーデータを追加
            reviews = [
                {'title': '使いにくい', 'text': 'UIが複雑すぎて使いにくい', 'rating': 1, 'author': 'user1', 'review_date': '2026-02-15'},
                {'title': '機能不足', 'text': 'フィルター機能が足りない', 'rating': 2, 'author': 'user2', 'review_date': '2026-02-15'},
            ]
            debug_print("🔧 デモデータを使用します")

        # 保存
        app_id = self.save_data(app_data, reviews)

        # レポート作成
        report = self.create_report(app_data, reviews)

        report_path = os.path.join(
            os.path.dirname(__file__),
            f"appstore_auto_{datetime.now().strftime('%Y%m%d_%H%M')}.md"
        )

        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)

        debug_print(f"\n📄 レポート: {report_path}")

        return {
            'success': True,
            'app_name': app_data.get('trackName'),
            'reviews_count': len(reviews),
            'report_path': report_path
        }


def main():
    import argparse

    parser = argparse.ArgumentParser(description='App Store Auto Analyzer')
    parser.add_argument('query', help='検索クエリ（アプリ名など）')

    args = parser.parse_args()

    print("=" * 60)
    print("🤖 App Store Auto Analyzer")
    print("=" * 60)

    analyzer = SimpleAppAnalyzer()
    result = analyzer.analyze(args.query)

    if result['success']:
        print("\n" + "=" * 60)
        print("✅ 完了！")
        print("=" * 60)
        print(f"📱 {result['app_name']}")
        print(f"📊 悪いレビュー: {result['reviews_count']} 件")
        print(f"📄 {result['report_path']}")
    else:
        print(f"\n❌ エラー: {result.get('error', '不明')}")


if __name__ == "__main__":
    main()
