#!/usr/bin/env python3
"""
App Store Top Gainers アナライザー v2
RSS APIを改良し、リトライ機構を強化
"""

import sqlite3
import json
import urllib.request
import urllib.parse
import urllib.error
import re
import time
import sys
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import os
import random

def debug_print(msg):
    print(msg)
    sys.stdout.flush()


class AppStoreAnalyzerV2:
    """App Store アナライザー v2"""

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
        """データベース接続"""
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        """データベース初期化"""
        conn = self._connect()
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS apps (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                app_id TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                developer TEXT,
                category TEXT,
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
                review_date TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (app_id) REFERENCES apps(id)
            )
        ''')

        conn.commit()
        conn.close()

    def get_reviews_with_retry(self, app_id: str, country: str = 'us',
                                 max_retries: int = 3, base_timeout: int = 30) -> List[Dict]:
        """レビューを取得（リトライ機構付き）"""
        url = f"https://itunes.apple.com/{country}/rss/customerreviews/id={app_id}/sortBy=mostRecent/xml"

        for attempt in range(1, max_retries + 1):
            timeout = base_timeout * attempt  # リトライごとにタイムアウトを増やす

            try:
                debug_print(f"      リトライ {attempt}/{max_retries}: timeout={timeout}秒")
                debug_print(f"      URL: {url[:80]}...")

                with urllib.request.urlopen(url, timeout=timeout) as response:
                    xml_data = response.read().decode('utf-8')

                debug_print(f"      ✅ XML取得完了: {len(xml_data)} バイト")

                # XMLからレビューを抽出
                reviews = self._parse_xml_reviews(xml_data)
                debug_print(f"      ✅ レビュー抽出: {len(reviews)} 件")

                return reviews

            except urllib.error.HTTPError as e:
                debug_print(f"      ⚠️ HTTPエラー: {e.code} {e.reason}")
                if attempt < max_retries:
                    debug_print(f"      {attempt * 2}秒待機してリトライ...")
                    time.sleep(attempt * 2)

            except urllib.error.URLError as e:
                debug_print(f"      ⚠️ URLエラー: {e.reason}")
                if attempt < max_retries:
                    debug_print(f"      {attempt * 2}秒待機してリトライ...")
                    time.sleep(attempt * 2)

            except Exception as e:
                debug_print(f"      ⚠️ エラー: {e}")
                if attempt < max_retries:
                    debug_print(f"      {attempt * 2}秒待機してリトライ...")
                    time.sleep(attempt * 2)

        debug_print(f"      ❌ {max_retries}回失敗")
        return []

    def _parse_xml_reviews(self, xml_data: str) -> List[Dict]:
        """XMLからレビューを抽出"""
        reviews = []

        # より詳細なパターン
        pattern = r'<entry>.*?<(?:title|im:name)>(.*?)</\w+>.*?<author>.*?<(?:name)>(.*?)</\w+>.*?<content>(.*?)</content>.*?<(?:im:rating|rating)>(\d+)</\w+>.*?(?:<(?:im:version)>(.*?)</\w+>|version>(.*?)</version>).*?(?:<updated>)(.*?)</updated>.*?</entry>'

        for match in re.finditer(pattern, xml_data, re.DOTALL):
            title = match.group(1).replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&')
            author = match.group(2).replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&')
            text = match.group(3).replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&')
            rating = int(match.group(4))
            version = match.group(5) or match.group(6) or 'N/A'
            date = match.group(7)

            # タイトルが空の場合、最初の30文字を使う
            if not title.strip() or title.startswith('⭐'):
                title = text[:50] + '...' if len(text) > 50 else text

            reviews.append({
                'title': title,
                'author': author,
                'text': text,
                'rating': rating,
                'version': version,
                'date': date
            })

        return reviews

    def search_app(self, query: str, limit: int = 5) -> List[Dict]:
        """App Storeでアプリを検索"""
        url = f"https://itunes.apple.com/search?term={urllib.parse.quote(query)}&media=software&limit={limit}"

        try:
            with urllib.request.urlopen(url, timeout=30) as response:
                data = json.loads(response.read().decode('utf-8'))
                return data.get('results', [])
        except Exception as e:
            debug_print(f"❌ 検索エラー: {e}")
            return []

    def save_app(self, app_data: Dict) -> int:
        """アプリを保存"""
        conn = self._connect()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT OR REPLACE INTO apps (app_id, name, developer, category, rating, url)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            str(app_data.get('trackId', '')),
            app_data.get('trackName', ''),
            app_data.get('artistName', ''),
            app_data.get('primaryGenreName', ''),
            app_data.get('averageUserRating', 0),
            app_data.get('trackViewUrl', '')
        ))

        app_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return app_id

    def save_reviews(self, app_id: int, reviews: List[Dict]) -> int:
        """レビューを保存"""
        if not reviews:
            return 0

        conn = self._connect()
        cursor = conn.cursor()

        saved = 0
        for review in reviews:
            try:
                cursor.execute('''
                    INSERT OR IGNORE INTO reviews (app_id, title, text, rating, author, review_date)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    app_id,
                    review.get('title', '')[:200],
                    review.get('text', ''),
                    review.get('rating', 0),
                    review.get('author', '')[:100],
                    review.get('date', '')
                ))

                if cursor.rowcount > 0:
                    saved += 1
            except Exception as e:
                debug_print(f"      ⚠️ レビュー保存エラー: {e}")
                continue

        conn.commit()
        conn.close()

        return saved

    def get_bad_reviews(self, app_id: int, limit: int = 50) -> List[Dict]:
        """星1〜2の悪いレビューを取得"""
        conn = self._connect()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT id, title, text, rating, author, review_date
            FROM reviews
            WHERE app_id = ? AND rating <= 2
            ORDER BY rating ASC, id DESC
            LIMIT ?
        ''', (app_id, limit))

        columns = [desc[0] for desc in cursor.description]
        reviews = [dict(zip(columns, row)) for row in cursor.fetchall()]

        conn.close()

        return reviews

    def analyze_issues(self, bad_reviews: List[Dict]) -> Dict:
        """悪いレビューを分析"""
        if not bad_reviews:
            return {
                'themes': [],
                'top_issues': [],
                'summary': '悪いレビューが見つかりませんでした'
            }

        all_texts = ' '.join([r['text'].lower() for r in bad_reviews])

        issue_patterns = {
            '機能不足': ['missing', 'feature', 'add', 'need', 'want', 'should have', 'wish', '機能', '追加'],
            'UI/UX': ['ui', 'ux', 'design', 'interface', 'navigation', 'hard to use', 'confusing', 'わかりにくい', '使いにくい'],
            'バグ/動作': ['bug', 'crash', 'freeze', 'slow', 'lag', 'error', 'doesn\'t work', '動かない', 'バグ', 'クラッシュ'],
            '会員登録/広告': ['ads', 'advertisement', 'subscription', 'pay', 'expensive', 'free', 'premium', '広告', '課金', '有料'],
            '速度/パフォーマンス': ['slow', 'loading', 'wait', 'load time', '遅い', '重い', '時間がかかる'],
            '通知': ['notification', 'alert', 'push', 'spam', '通知'],
        }

        themes = []
        for theme, keywords in issue_patterns.items():
            count = sum(all_texts.count(kw) for kw in keywords)
            if count > 0:
                themes.append({'theme': theme, 'count': count})

        themes = sorted(themes, key=lambda x: x['count'], reverse=True)[:5]

        issue_counts = {}
        for review in bad_reviews:
            text = review['text'][:80]
            if len(text) > 10:
                issue_counts[text] = issue_counts.get(text, 0) + 1

        top_issues = sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)[:10]

        if themes:
            theme_str = '、'.join([t['theme'] for t in themes[:3]])
            summary = f"主な不満テーマ: {theme_str}"
        else:
            summary = "特定のテーマは見つかりませんでした"

        return {
            'themes': themes,
            'top_issues': top_issues,
            'summary': summary
        }

    def create_analysis_report(self, app_data: Dict, bad_reviews: List[Dict], analysis: Dict) -> str:
        """分析レポートを作成"""
        report = []
        report.append("=" * 80)
        report.append("📱 App Store レビュー分析レポート")
        report.append(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("=" * 80)

        report.append("\n📱 アプリ情報")
        report.append("-" * 40)
        report.append(f"名前: {app_data.get('trackName', 'N/A')}")
        report.append(f"開発者: {app_data.get('artistName', 'N/A')}")
        report.append(f"カテゴリ: {app_data.get('primaryGenreName', 'N/A')}")
        report.append(f"評価: ⭐{app_data.get('averageUserRating', 'N/A')}")

        report.append("\n📊 悪いレビュー統計")
        report.append("-" * 40)
        report.append(f"星1〜2のレビュー数: {len(bad_reviews)}")

        rating_dist = {}
        for r in bad_reviews:
            rating_dist[r['rating']] = rating_dist.get(r['rating'], 0) + 1

        for rating in [1, 2]:
            count = rating_dist.get(rating, 0)
            bar = '█' * (count // 2 + 1)
            report.append(f"  星{rating}: {count}件 {bar}")

        report.append("\n🎯 不満テーマ分析")
        report.append("-" * 40)
        for theme in analysis['themes'][:5]:
            bar = '█' * min(theme['count'], 20)
            report.append(f"  {theme['theme']}: {theme['count']}回 {bar}")

        report.append("\n😤 上位の不満（繰り返されている）")
        report.append("-" * 40)
        for i, (issue, count) in enumerate(analysis['top_issues'][:10], 1):
            report.append(f"\n{i}. ({count}回) {issue}")

        report.append("\n💬 悪いレビュー詳細（星1〜2）")
        report.append("-" * 40)
        for i, review in enumerate(bad_reviews[:20], 1):
            stars = '⭐' * review['rating']
            report.append(f"\n{i}. {stars} {review['title'] or '(タイトルなし)'}")
            report.append(f"   ユーザー: {review['author']}")
            report.append(f"   日付: {review['review_date']}")
            report.append(f"   テキスト: {review['text'][:150]}{'...' if len(review['text']) > 150 else ''}")

        report.append("\n🤖 AI分析用プロンプト")
        report.append("-" * 40)
        report.append("以下の悪いレビューをAIに分析させる:")
        report.append("---")
        for review in bad_reviews[:30]:
            report.append(f"星{review['rating']}: {review['text']}")
        report.append("---")

        report.append("\n💡 おすすめアクション")
        report.append("-" * 40)
        if analysis['themes']:
            top_theme = analysis['themes'][0]['theme']
            report.append(f"1. 最優先: {top_theme}を改善")
            report.append("2. UIをシンプルにする")
            report.append("3. 強制的な会員登録を削除する（ある場合）")
            report.append("4. パフォーマンスを改善する")

        report.append("\n" + "=" * 80)

        return "\n".join(report)

    def analyze_app(self, search_query: str, max_reviews: int = 100) -> Dict:
        """アプリを分析"""
        debug_print(f"\n🔍 検索: {search_query}")

        # 検索
        results = self.search_app(search_query, limit=5)
        if not results:
            return {'success': False, 'error': 'アプリが見つかりませんでした'}

        app_data = results[0]
        debug_print(f"📱 アプリ: {app_data.get('trackName')}")
        debug_print(f"   開発者: {app_data.get('artistName')}")
        debug_print(f"   評価: ⭐{app_data.get('averageUserRating')}")

        # アプリを保存
        app_id_db = self.save_app(app_data)
        debug_print(f"✅ アプリ保存: app_id={app_id_db}")

        # レビューを取得（複数カテゴリ）
        debug_print(f"\n🔍 レビューを取得中...")
        all_reviews = []

        countries = ['us', 'gb', 'ca', 'au']
        for country in countries:
            debug_print(f"   {country.upper()} のレビューを取得...")
            reviews = self.get_reviews_with_retry(app_data.get('trackId', ''), country)
            if reviews:
                debug_print(f"   ✅ {len(reviews)} 件取得")
                all_reviews.extend(reviews)
            else:
                debug_print(f"   ⚠️ 取得失敗")
            time.sleep(1)

        # 重複を除去
        unique_reviews = []
        seen = set()
        for review in all_reviews:
            key = (review['author'], review['text'][:50])
            if key not in seen:
                seen.add(key)
                unique_reviews.append(review)

        debug_print(f"   📊 総レビュー: {len(all_reviews)} 件 -> 重複除去: {len(unique_reviews)} 件")

        # レビューを保存
        if unique_reviews:
            saved = self.save_reviews(app_id_db, unique_reviews)
            debug_print(f"✅ {saved} 件保存")

        # 悪いレビューを取得
        debug_print(f"\n😤 悪いレビューを分析中...")
        bad_reviews = self.get_bad_reviews(app_id_db, limit=max_reviews)
        debug_print(f"   星1〜2: {len(bad_reviews)} 件")

        # 分析
        debug_print(f"🎯 不満を分析中...")
        analysis = self.analyze_issues(bad_reviews)

        # レポート作成
        debug_print(f"📝 レポートを作成中...")
        report = self.create_analysis_report(app_data, bad_reviews, analysis)

        # レポートを保存
        report_path = os.path.join(
            os.path.dirname(__file__),
            f"appstore_analysis_{datetime.now().strftime('%Y%m%d_%H%M')}.md"
        )
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)

        debug_print(f"✅ レポート保存: {report_path}")

        return {
            'success': True,
            'app_name': app_data.get('trackName'),
            'bad_reviews_count': len(bad_reviews),
            'report_path': report_path,
            'analysis': analysis
        }


def main():
    """メイン処理"""
    import argparse

    parser = argparse.ArgumentParser(description='App Store Top Gainers アナライザー v2')
    parser.add_argument('--search', '-s', help='検索クエリ', required=True)

    args = parser.parse_args()

    print("=" * 60)
    print("🧪 App Store アナライザー v2")
    print("=" * 60)

    analyzer = AppStoreAnalyzerV2()
    result = analyzer.analyze_app(args.search, max_reviews=100)

    if result['success']:
        print("\n" + "=" * 60)
        print("✅ 完了！")
        print("=" * 60)
        print(f"\n📄 レポート: {result['report_path']}")
    else:
        print(f"\n❌ エラー: {result.get('error', '不明')}")


if __name__ == "__main__":
    main()
