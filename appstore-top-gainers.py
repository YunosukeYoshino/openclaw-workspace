#!/usr/bin/env python3
"""
App Store Top Gainers アナライザー
月一回実行して、急増したアプリの悪いレビューを分析
"""

import sqlite3
import json
import urllib.request
import urllib.parse
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


def get_app_store_reviews_url(app_id: str, country: str = 'us') -> str:
    """App StoreレビューページのURLを生成"""
    return f"https://apps.apple.com/{country}/app/id{app_id}?see-all=reviews#see-all/reviews"

class AppStoreReview:
    """App Store レビュー"""
    def __init__(self, id: str, app_id: str, title: str, text: str, rating: int,
                 author: str, version: str, date: str):
        self.id = id
        self.app_id = app_id
        self.title = title
        self.text = text
        self.rating = rating
        self.author = author
        self.version = version
        self.date = date
        self.created_at = datetime.now().isoformat()

class AppStoreAnalyzer:
    """App Store アナライザー"""

    ITUNES_API_BASE = "https://itunes.apple.com"

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

        # アプリテーブル
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS apps (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                app_id TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                bundle_id TEXT,
                developer TEXT,
                category TEXT,
                rating REAL,
                rating_count INTEGER,
                price REAL,
                url TEXT,
                description TEXT,
                icon_url TEXT,
                screenshot_urls TEXT,
                discovered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_checked_at TIMESTAMP
            )
        ''')

        # レビューテーブル
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                app_id INTEGER NOT NULL,
                review_id TEXT,
                title TEXT,
                text TEXT,
                rating INTEGER,
                author TEXT,
                version TEXT,
                review_date TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (app_id) REFERENCES apps(id)
            )
        ''')

        # 分析結果テーブル
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analyses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                app_id INTEGER NOT NULL,
                report_path TEXT,
                issues_summary TEXT,
                top_issues TEXT,
                recommendations TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (app_id) REFERENCES apps(id)
            )
        ''')

        conn.commit()
        conn.close()

    def search_app(self, query: str, limit: int = 10) -> List[Dict]:
        """App Storeでアプリを検索"""
        url = f"{self.ITUNES_API_BASE}/search?term={urllib.parse.quote(query)}&media=software&limit={limit}"
        try:
            with urllib.request.urlopen(url) as response:
                data = json.loads(response.read().decode('utf-8'))
                return data.get('results', [])
        except Exception as e:
            print(f"❌ 検索エラー: {e}")
            return []

    def get_app_details(self, app_id: str) -> Optional[Dict]:
        """アプリ詳細を取得"""
        url = f"{self.ITUNES_API_BASE}/lookup?id={app_id}"
        try:
            with urllib.request.urlopen(url) as response:
                data = json.loads(response.read().decode('utf-8'))
                results = data.get('results', [])
                return results[0] if results else None
        except Exception as e:
            print(f"❌ 詳細取得エラー: {e}")
            return None

    def get_reviews(self, app_id: str, country: str = 'us', page: int = 1) -> List[Dict]:
        """レビューを取得（Rss feedを使用）"""
        url = f"https://itunes.apple.com/{country}/rss/customerreviews/id={app_id}/sortBy=mostRecent/xml"
        try:
            debug_print(f"      URL: {url[:80]}...")
            with urllib.request.urlopen(url, timeout=30) as response:
                xml_data = response.read().decode('utf-8')

            debug_print(f"      XML取得完了: {len(xml_data)} バイト")

            # XMLからレビューを抽出
            reviews = []
            pattern = r'<entry>.*?<title>(.*?)</title>.*?<author>.*?<name>(.*?)</name>.*?<content>(.*?)</content>.*?<rating>(\d+)</rating>.*?<im:version>(.*?)</im:version>.*?<updated>(.*?)</updated>.*?</entry>'
            for match in re.finditer(pattern, xml_data, re.DOTALL):
                reviews.append({
                    'title': match.group(1),
                    'author': match.group(2),
                    'text': match.group(3).replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&'),
                    'rating': int(match.group(4)),
                    'version': match.group(5),
                    'date': match.group(6)
                })

            debug_print(f"      レビュー抽出: {len(reviews)} 件")
            return reviews
        except urllib.error.URLError as e:
            debug_print(f"      URLエラー: {e}")
            return []
        except Exception as e:
            debug_print(f"      ❌ レビュー取得エラー: {e}")
            return []

    def save_app(self, app_data: Dict) -> int:
        """アプリを保存"""
        conn = self._connect()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT OR REPLACE INTO apps
            (app_id, name, bundle_id, developer, category, rating, rating_count, price, url, description, icon_url, screenshot_urls, last_checked_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            str(app_data.get('trackId', '')),
            app_data.get('trackName', ''),
            app_data.get('bundleId', ''),
            app_data.get('artistName', ''),
            app_data.get('primaryGenreName', ''),
            app_data.get('averageUserRating', 0),
            app_data.get('userRatingCount', 0),
            app_data.get('price', 0),
            app_data.get('trackViewUrl', ''),
            app_data.get('description', '')[:2000],
            app_data.get('artworkUrl100', ''),
            json.dumps(app_data.get('screenshotUrls', [])),
            datetime.now().isoformat()
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
                    INSERT OR IGNORE INTO reviews
                    (app_id, review_id, title, text, rating, author, version, review_date)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    app_id,
                    review.get('id', ''),
                    review.get('title', '')[:200],
                    review.get('text', ''),
                    review.get('rating', 0),
                    review.get('author', '')[:100],
                    review.get('version', '')[:20],
                    review.get('date', '')
                ))
                if cursor.rowcount > 0:
                    saved += 1
            except Exception as e:
                continue

        conn.commit()
        conn.close()

        return saved

    def get_bad_reviews(self, app_id: int, limit: int = 50) -> List[Dict]:
        """星1〜2の悪いレビューを取得"""
        conn = self._connect()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT id, title, text, rating, author, version, review_date
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
                'common_phrases': [],
                'summary': '悪いレビューが見つかりませんでした'
            }

        # キーワード分析
        all_texts = ' '.join([r['text'].lower() for r in bad_reviews])

        # 共通の不満パターン
        issue_patterns = {
            '機能不足': ['missing', 'feature', 'add', 'need', 'want', 'should have', 'wish', '機能', '追加'],
            'UI/UX': ['ui', 'ux', 'design', 'interface', 'navigation', 'hard to use', 'confusing', 'わかりにくい', '使いにくい'],
            'バグ/動作': ['bug', 'crash', 'freeze', 'slow', 'lag', 'error', 'doesn\'t work', '動かない', 'バグ', 'クラッシュ'],
            '会員登録/広告': ['ads', 'advertisement', 'subscription', 'pay', 'expensive', 'free', 'premium', '広告', '課金', '有料'],
            '速度/パフォーマンス': ['slow', 'loading', 'wait', 'load time', '遅い', '重い', '時間がかかる'],
            '通知': ['notification', 'alert', 'push', 'spam', '通知'],
            '同期/バックアップ': ['sync', 'backup', 'lost', 'save', 'データ', '同期', 'バックアップ', '消えた'],
            'カスタマイズ': ['custom', 'personalize', 'theme', 'dark mode', 'カスタマイズ', 'テーマ'],
            'オフライン': ['offline', 'internet', 'connection', 'wifi', 'オフライン', 'インターネット'],
        }

        themes = []
        for theme, keywords in issue_patterns.items():
            count = sum(all_texts.count(kw) for kw in keywords)
            if count > 0:
                themes.append({'theme': theme, 'count': count})

        themes = sorted(themes, key=lambda x: x['count'], reverse=True)[:5]

        # 上位の不満を抽出（繰り返されているもの）
        issue_counts = {}
        for review in bad_reviews:
            text = review['text'][:100]  # 最初の100文字をサンプル
            if len(text) > 10:
                issue_counts[text] = issue_counts.get(text, 0) + 1

        top_issues = sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)[:10]

        # サマリー作成
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
        report.append("📱 App Store Top Gainers 分析レポート")
        report.append(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("=" * 80)

        # アプリ情報
        report.append("\n📱 アプリ情報")
        report.append("-" * 40)
        report.append(f"名前: {app_data.get('trackName', 'N/A')}")
        report.append(f"開発者: {app_data.get('artistName', 'N/A')}")
        report.append(f"カテゴリ: {app_data.get('primaryGenreName', 'N/A')}")
        report.append(f"評価: ⭐{app_data.get('averageUserRating', 'N/A')} ({app_data.get('userRatingCount', 0)}件)")
        report.append(f"価格: ${app_data.get('price', 'N/A')}")
        report.append(f"URL: {app_data.get('trackViewUrl', 'N/A')}")

        # レビュー統計
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

        # テーマ分析
        report.append("\n🎯 不満テーマ分析")
        report.append("-" * 40)
        for theme in analysis['themes'][:5]:
            bar = '█' * min(theme['count'], 20)
            report.append(f"  {theme['theme']}: {theme['count']}回 {bar}")

        # 上位の不満
        report.append("\n😤 上位の不満（繰り返されている）")
        report.append("-" * 40)
        for i, (issue, count) in enumerate(analysis['top_issues'][:10], 1):
            report.append(f"\n{i}. ({count}回) {issue[:80]}...")
            report.append(f"   (完全なテキストで詳細確認)")

        # 悪いレビュー詳細（星1〜2）
        report.append("\n💬 悪いレビュー詳細（星1〜2）")
        report.append("-" * 40)
        for i, review in enumerate(bad_reviews[:20], 1):
            stars = '⭐' * review['rating']
            report.append(f"\n{i}. {stars} {review['title'] or '(タイトルなし)'}")
            report.append(f"   ユーザー: {review['author']}")
            report.append(f"   バージョン: {review['version']}")
            report.append(f"   日付: {review['review_date']}")
            report.append(f"   テキスト: {review['text'][:200]}{'...' if len(review['text']) > 200 else ''}")

        # AIプロンプト用抽出
        report.append("\n🤖 AI分析用プロンプト入力")
        report.append("-" * 40)
        report.append("以下の悪いレビューをAIに分析させる:")
        report.append("---")
        for review in bad_reviews[:30]:
            report.append(f"星{review['rating']}: {review['text']}")
        report.append("---")

        # おすすめアクション
        report.append("\n💡 おすすめアクション")
        report.append("-" * 40)
        if analysis['themes']:
            top_theme = analysis['themes'][0]['theme']
            report.append(f"1. 最優先: {top_theme}を改善")
            report.append("2. UIをシンプルにする")
            report.append("3. 強制的な会員登録を削除する（ある場合）")
            report.append("4. パフォーマンスを改善する")
            report.append("5. 欠けている機能を追加する")

        report.append("\n" + "=" * 80)

        return "\n".join(report)

    def analyze_top_gainer(self, search_query: str = None, app_id: str = None) -> Dict:
        """トップゲイナーを分析"""
        debug_print("DEBUG: analyze_top_gainer開始")

        if app_id:
            # 直接アプリIDを指定
            debug_print(f"DEBUG: app_id={app_id}")
            app_data = self.get_app_details(app_id)
        elif search_query:
            # 検索して上位を取得
            debug_print(f"DEBUG: search_query={search_query}")
            results = self.search_app(search_query, limit=5)
            if results:
                app_data = results[0]
                debug_print(f"DEBUG: 検索結果: {app_data.get('trackName')}")
            else:
                return {'success': False, 'error': 'アプリが見つかりませんでした'}
        else:
            return {'success': False, 'error': '検索クエリまたはapp_idが必要です'}

        if not app_data:
            return {'success': False, 'error': 'アプリ詳細を取得できませんでした'}

        debug_print(f"\n📱 アプリ: {app_data.get('trackName', 'N/A')}")
        debug_print(f"   開発者: {app_data.get('artistName', 'N/A')}")
        debug_print(f"   評価: ⭐{app_data.get('averageUserRating', 'N/A')}")

        # アプリを保存
        debug_print("DEBUG: アプリを保存中...")
        app_id_db = self.save_app(app_data)
        debug_print(f"DEBUG: app_id_db={app_id_db}")

        # レビューを取得（複数ページ）
        debug_print(f"\n🔍 レビューを取得中...")
        all_reviews = []
        for country in ['us', 'jp']:
            debug_print(f"   {country} のレビューを取得...")
            reviews = self.get_reviews(app_data.get('trackId', ''), country)
            if reviews:
                debug_print(f"   ✅ {len(reviews)} 件取得")
                all_reviews.extend(reviews)
            else:
                debug_print(f"   ⚠️ レビュー取得失敗、次へ...")
            time.sleep(1)  # API制限回避

        # レビューを保存
        if all_reviews:
            debug_print("DEBUG: レビューを保存中...")
            saved = self.save_reviews(app_id_db, all_reviews)
            debug_print(f"✅ {saved} 件保存")

        # 悪いレビューを取得
        debug_print(f"\n😤 悪いレビューを分析中...")
        bad_reviews = self.get_bad_reviews(app_id_db, limit=50)
        debug_print(f"   星1〜2: {len(bad_reviews)} 件")

        # 分析
        debug_print("DEBUG: 不満を分析中...")
        analysis = self.analyze_issues(bad_reviews)

        # レポート作成
        debug_print("DEBUG: レポートを作成中...")
        report = self.create_analysis_report(app_data, bad_reviews, analysis)

        # レポートを保存
        report_path = os.path.join(
            os.path.dirname(__file__),
            f"appstore_analysis_{datetime.now().strftime('%Y%m%d_%H%M')}.md"
        )
        debug_print(f"DEBUG: レポート保存先: {report_path}")
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)

        debug_print(f"\n📄 レポート保存: {report_path}")

        # 分析結果をDBに保存
        debug_print("DEBUG: 分析結果をDBに保存中...")
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO analyses (app_id, report_path, issues_summary, top_issues, recommendations)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            app_id_db,
            report_path,
            analysis['summary'],
            json.dumps(analysis['top_issues'][:10]),
            json.dumps(analysis['themes'][:5])
        ))
        conn.commit()
        conn.close()

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

    parser = argparse.ArgumentParser(description='App Store Top Gainers アナライザー')
    parser.add_argument('--search', '-s', help='検索クエリ（iTunes API経由）')
    parser.add_argument('--app-id', '-a', help='App Store ID（iTunes API経由）')
    parser.add_argument('--manual', '-m', action='store_true', help='手動入力モード（レビューを直接入力）')
    parser.add_argument('--test', '-t', action='store_true', help='テストモード（ダミーデータ使用）')
    parser.add_argument('--list', '-l', action='store_true', help='最近分析したアプリを一覧表示')

    args = parser.parse_args()

    print("DEBUG: アナライザー初期化中...")
    analyzer = AppStoreAnalyzer()
    print("DEBUG: 初期化完了")

    if args.test:
        # テストモード（ダミーデータ）
        print("\n🧪 テストモード: ダミーデータで分析します")
        return run_test_mode(analyzer)

    if args.manual:
        # 手動入力モード
        print("\n📝 手動入力モード")
        return run_manual_mode(analyzer)

    if args.list:
        # 一覧表示
        conn = analyzer._connect()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT id, name, developer, rating, rating_count, discovered_at
            FROM apps
            ORDER BY discovered_at DESC
            LIMIT 10
        ''')

        print("\n📱 最近分析したアプリ")
        print("-" * 80)
        for row in cursor.fetchall():
            print(f"ID:{row[0]} | {row[1]} | {row[2]} | ⭐{row[3]} ({row[4]}件) | {row[5][:10]}")

        conn.close()

    elif args.search or args.app_id:
        print("\n⚠️  iTunes APIは現在不安定です。")
        print("   --test モードでテストするか、--manual モードでレビューを手動入力してください。\n")

        result = analyzer.analyze_top_gainer(search_query=args.search, app_id=args.app_id)

        if result['success']:
            print("\n" + "=" * 60)
            print("✅ 完了！")
            print("=" * 60)
        else:
            print(f"\n❌ エラー: {result.get('error', '不明')}")

    else:
        # デフォルトはテストモード
        print("\n🧪 テストモード: ダミーデータで分析します")
        print("   （iTunes APIが不安定なため、--test フラグなしでテストモードが実行されます）\n")
        return run_test_mode(analyzer)


def run_test_mode(analyzer: AppStoreAnalyzer):
    """テストモード（ダミーデータ使用）"""
    # ダミーデータ作成
    app_data = {
        'trackId': '123456',
        'trackName': 'Test Camera App',
        'artistName': 'Test Developer',
        'primaryGenreName': 'Photo & Video',
        'averageUserRating': 3.5,
        'userRatingCount': 1000,
        'price': 0.99,
        'trackViewUrl': 'https://example.com/app',
        'description': 'Test camera app',
        'artworkUrl100': 'https://example.com/icon.png',
        'screenshotUrls': []
    }

    app_id = analyzer.save_app(app_data)
    print(f"✅ アプリ保存: app_id={app_id}")

    # ダミーレビュー（星1〜2）
    bad_reviews = [
        {'title': '使いにくい', 'author': 'user1', 'text': 'UIが複雑すぎて使いにくい。ボタンが多くて何が何だかわからない。', 'rating': 1, 'version': '1.0', 'date': '2026-01-15'},
        {'title': '機能不足', 'author': 'user2', 'text': 'フィルター機能が足りない。もっと多くのエフェクトが欲しい。', 'rating': 2, 'version': '1.0', 'date': '2026-01-16'},
        {'title': '遅い', 'author': 'user3', 'text': '起動が遅い。写真を撮るまでに時間がかかる。', 'rating': 1, 'version': '1.0', 'date': '2026-01-17'},
        {'title': '会員登録が強制', 'author': 'user4', 'text': '会員登録しないと使えない。無料で使わせてほしい。', 'rating': 1, 'version': '1.1', 'date': '2026-01-18'},
        {'title': '広告が多い', 'author': 'user5', 'text': '広告が多すぎて邪魔。課金すれば消えるけど高すぎる。', 'rating': 1, 'version': '1.1', 'date': '2026-01-19'},
        {'title': 'UIが複雑すぎて使いにくい', 'author': 'user6', 'text': 'UIが複雑すぎて使いにくい。初心者にはおすすめできない。', 'rating': 1, 'version': '1.0', 'date': '2026-01-20'},
        {'title': '使いにくい', 'author': 'user7', 'text': '使いにくい。シンプルにしてほしい。', 'rating': 2, 'version': '1.0', 'date': '2026-01-21'},
        {'title': '機能が足りない', 'author': 'user8', 'text': '編集機能が足りない。トリミングだけじゃ不十分。', 'rating': 1, 'version': '1.2', 'date': '2026-01-22'},
        {'title': '重い', 'author': 'user9', 'text': '重い。動作がもっさりしている。もっと軽くしてほしい。', 'rating': 2, 'version': '1.2', 'date': '2026-01-23'},
        {'title': 'バグだらけ', 'author': 'user10', 'text': 'よく落ちる。バグが多い。', 'rating': 1, 'version': '1.2', 'date': '2026-01-24'},
        {'title': 'クラッシュ頻発', 'author': 'user11', 'text': '撮影直後にクラッシュする。何度やってもダメ。', 'rating': 1, 'version': '1.3', 'date': '2026-01-25'},
        {'title': '保存できない', 'author': 'user12', 'text': '写真を保存できない。カメラロールに保存されない。', 'rating': 1, 'version': '1.3', 'date': '2026-01-26'},
        {'title': '使いにくいUI', 'author': 'user13', 'text': 'メニューが深すぎる。目的の機能にたどり着けない。', 'rating': 2, 'version': '1.0', 'date': '2026-01-27'},
        {'title': 'フィルターが足りない', 'author': 'user14', 'text': 'フィルターが少ない。もっとバリエーションが欲しい。', 'rating': 1, 'version': '1.2', 'date': '2026-01-28'},
        {'title': '高すぎる', 'author': 'user15', 'text': '有料版が高すぎる。サブスクリプションじゃなくて買い切りにしてほしい。', 'rating': 1, 'version': '1.1', 'date': '2026-01-29'},
    ]

    saved = analyzer.save_reviews(app_id, bad_reviews)
    print(f"✅ レビュー保存: {saved} 件")

    # 分析
    bad_reviews = analyzer.get_bad_reviews(app_id, limit=50)
    analysis = analyzer.analyze_issues(bad_reviews)

    # レポート作成
    report = analyzer.create_analysis_report(app_data, bad_reviews, analysis)

    # レポートを保存
    from datetime import datetime
    report_path = os.path.join(
        os.path.dirname(__file__),
        f"appstore_analysis_{datetime.now().strftime('%Y%m%d_%H%M')}.md"
    )
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"\n📄 レポート保存: {report_path}")

    print("\n" + "=" * 60)
    print("✅ テスト完了！")
    print("=" * 60)


def run_manual_mode(analyzer: AppStoreAnalyzer):
    """手動入力モード"""
    print("\n📱 アプリ情報を入力してください")
    print("=" * 60)

    app_name = input("アプリ名: ")
    developer = input("開発者名: ")
    category = input("カテゴリ: ")
    rating = input("評価 (例: 3.5): ")

    app_data = {
        'trackId': str(int(datetime.now().timestamp())),
        'trackName': app_name,
        'artistName': developer,
        'primaryGenreName': category,
        'averageUserRating': float(rating) if rating else 0,
        'userRatingCount': 0,
        'price': 0,
        'trackViewUrl': '',
        'description': '',
        'artworkUrl100': '',
        'screenshotUrls': []
    }

    app_id = analyzer.save_app(app_data)
    print(f"\n✅ アプリ保存: app_id={app_id}")

    print("\n📝 レビューを入力してください（空行で終了）")
    print("フォーマット: 星数|タイトル|テキスト")
    print("例: 1|使いにくい|UIが複雑すぎて使いにくい")
    print("=" * 60)

    bad_reviews = []
    review_count = 0

    while review_count < 30:
        line = input(f"\nレビュー {review_count + 1}/30: ")
        if not line.strip():
            break

        try:
            parts = line.split('|', 2)
            if len(parts) == 3:
                rating = int(parts[0].strip())
                title = parts[1].strip()
                text = parts[2].strip()

                if rating <= 2:  # 星1〜2のみ
                    bad_reviews.append({
                        'title': title,
                        'author': f'user{review_count + 1}',
                        'text': text,
                        'rating': rating,
                        'version': '1.0',
                        'date': '2026-01-15'
                    })
                    review_count += 1
                    print(f"✅ 追加 (星{rating}): {title}")
                else:
                    print("⚠️ 星1〜2のレビューのみ追加できます")
            else:
                print("⚠️ フォーマットエラー: 星数|タイトル|テキスト")
        except Exception as e:
            print(f"⚠️ 入力エラー: {e}")

    if bad_reviews:
        saved = analyzer.save_reviews(app_id, bad_reviews)
        print(f"\n✅ レビュー保存: {saved} 件")

        # 分析
        db_bad_reviews = analyzer.get_bad_reviews(app_id, limit=50)
        analysis = analyzer.analyze_issues(db_bad_reviews)

        # レポート作成
        report = analyzer.create_analysis_report(app_data, db_bad_reviews, analysis)

        # レポートを保存
        report_path = os.path.join(
            os.path.dirname(__file__),
            f"appstore_analysis_{datetime.now().strftime('%Y%m%d_%H%M')}.md"
        )
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)

        print(f"\n📄 レポート保存: {report_path}")

        print("\n" + "=" * 60)
        print("✅ 完了！")
        print("=" * 60)
    else:
        print("\n⚠️ レビューが入力されませんでした")


if __name__ == "__main__":
    main()
