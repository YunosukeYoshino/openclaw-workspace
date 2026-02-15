#!/usr/bin/env python3
"""
Hacker News アイデアまとめ・提案ツール
3日ごとに実行して、DBをクリアしてから収集・まとめる
"""

import sys
import os
import importlib.util
from datetime import datetime, date
from collections import Counter
import json

# hackernews-scraperを動的インポート
spec = importlib.util.spec_from_file_location("hackernews_scraper", os.path.join(os.path.dirname(__file__), "hackernews-scraper.py"))
hackernews_scraper = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hackernews_scraper)
HackerNewsScraper = hackernews_scraper.HackerNewsScraper
HackerNewsProduct = hackernews_scraper.HackerNewsProduct

class IdeasSummarizer:
    """アイデアまとめツール"""

    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = os.path.join(os.path.dirname(__file__), "data", "producthunt_ideas.db")
        self.scraper = HackerNewsScraper(db_path)
        self.conn = self.scraper._connect()

    def __del__(self):
        if hasattr(self, 'conn'):
            self.conn.close()

    def analyze_topics(self, products: list) -> dict:
        """トピックを分析"""
        # タイトルからキーワードを抽出
        keywords = []

        for p in products:
            title = p['name'].lower()

            # 一般的なキーワード
            tech_keywords = ['ai', 'machine learning', 'ml', 'llm', 'gpt', 'openai',
                          'python', 'javascript', 'rust', 'go', 'zig', 'c', 'c++',
                          'web', 'browser', 'chrome', 'firefox', 'safari',
                          'database', 'sql', 'nosql', 'mongodb', 'postgresql',
                          'api', 'rest', 'graphql',
                          'security', 'privacy', 'encryption',
                          'devops', 'kubernetes', 'docker', 'aws', 'cloud',
                          'blockchain', 'crypto', 'web3', 'nft',
                          'game', 'gaming', 'vr', 'ar', 'metaverse',
                          'linux', 'open source', 'oss', 'github',
                          'startup', 'saas', 'b2b', 'b2c']

            for kw in tech_keywords:
                if kw in title:
                    keywords.append(kw)

        # カウント
        keyword_counts = Counter(keywords)

        return {
            'top_keywords': dict(keyword_counts.most_common(10)),
            'total_keywords': len(keywords)
        }

    def categorize_ideas(self, products: list) -> dict:
        """アイデアをカテゴリ分け"""
        categories = {
            'AI/ML': [],
            '開発ツール': [],
            'Web/ブラウザ': [],
            'セキュリティ/プライバシー': [],
            'DevOps/インフラ': [],
            'ブロックチェーン/Web3': [],
            'ゲーム': [],
            'データベース': [],
            'スタートアップ/SaaS': [],
            'オープンソース': [],
            'その他': []
        }

        for p in products:
            title = p['name'].lower()

            if any(kw in title for kw in ['ai', 'machine learning', 'ml', 'llm', 'gpt', 'openai', 'chatbot']):
                categories['AI/ML'].append(p)
            elif any(kw in title for kw in ['api', 'sdk', 'library', 'framework', 'tool', 'cli']):
                categories['開発ツール'].append(p)
            elif any(kw in title for kw in ['browser', 'chrome', 'firefox', 'safari', 'web', 'html']):
                categories['Web/ブラウザ'].append(p)
            elif any(kw in title for kw in ['security', 'privacy', 'encryption', 'hack', 'vulnerability']):
                categories['セキュリティ/プライバシー'].append(p)
            elif any(kw in title for kw in ['devops', 'kubernetes', 'docker', 'aws', 'cloud', 'ci/cd']):
                categories['DevOps/インフラ'].append(p)
            elif any(kw in title for kw in ['blockchain', 'crypto', 'web3', 'nft', 'bitcoin']):
                categories['ブロックチェーン/Web3'].append(p)
            elif any(kw in title for kw in ['game', 'gaming', 'vr', 'ar', 'metaverse']):
                categories['ゲーム'].append(p)
            elif any(kw in title for kw in ['database', 'sql', 'nosql', 'mongo', 'postgres']):
                categories['データベース'].append(p)
            elif any(kw in title for kw in ['startup', 'saas', 'platform', 'service']):
                categories['スタートアップ/SaaS'].append(p)
            elif any(kw in title for kw in ['open source', 'oss', 'github', 'repo']):
                categories['オープンソース'].append(p)
            else:
                categories['その他'].append(p)

        # 空のカテゴリを削除
        return {k: v for k, v in categories.items() if v}

    def generate_recommendations(self, categories: dict) -> list:
        """おすすめアイデアを生成"""
        recommendations = []

        for category, products in categories.items():
            if len(products) >= 3:
                # 各カテゴリの上位3件
                for p in products[:3]:
                    recommendations.append({
                        'title': p['name'],
                        'url': p['url'],
                        'votes': p['votes'],
                        'category': category,
                        'reason': f'{category}カテゴリで人気'
                    })

        # 全体の上位5件も追加
        cursor = self.conn.cursor()
        cursor.execute('SELECT name, url, votes FROM products ORDER BY votes DESC LIMIT 5')
        for row in cursor.fetchall():
            if not any(r['url'] == row[1] for r in recommendations):
                recommendations.append({
                    'title': row[0],
                    'url': row[1],
                    'votes': row[2],
                    'category': '全カテゴリ',
                    'reason': '総合人気'
                })

        return recommendations[:15]

    def create_summary_report(self) -> str:
        """サマリーレポートを作成"""
        # DBから全プロダクト取得
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM products ORDER BY votes DESC')
        columns = [desc[0] for desc in cursor.description]
        all_products = [dict(zip(columns, row)) for row in cursor.fetchall()]

        for p in all_products:
            if p['topics']:
                p['topics'] = json.loads(p['topics'])

        # 分析
        topic_analysis = self.analyze_topics(all_products)
        categories = self.categorize_ideas(all_products)
        recommendations = self.generate_recommendations(categories)

        # レポート作成
        report = []
        report.append("=" * 80)
        report.append("🎯 Hacker News アイデアまとめ")
        report.append(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("=" * 80)

        # 統計
        report.append("\n📊 統計情報")
        report.append("-" * 40)
        report.append(f"総アイデア数: {len(all_products)}")
        report.append(f"カテゴリ数: {len(categories)}")

        if all_products:
            avg_votes = sum(p['votes'] for p in all_products) / len(all_products)
            max_votes = max(p['votes'] for p in all_products)
            report.append(f"平均👍: {avg_votes:.1f}")
            report.append(f"最高👍: {max_votes}")

        # キーワード分析
        report.append("\n🔑 人気キーワード")
        report.append("-" * 40)
        if topic_analysis['top_keywords']:
            for kw, count in list(topic_analysis['top_keywords'].items())[:5]:
                report.append(f"  {kw}: {count}回")

        # カテゴリ別
        report.append("\n📁 カテゴリ別")
        report.append("-" * 40)
        for category, products in sorted(categories.items(), key=lambda x: len(x[1]), reverse=True):
            report.append(f"\n【{category}】({len(products)}件)")
            for p in products[:3]:
                report.append(f"  • {p['name']} (👍{p['votes']})")
            if len(products) > 3:
                report.append(f"  ... 他{len(products)-3}件")

        # おすすめ
        report.append("\n💡 おすすめアイデア")
        report.append("-" * 40)
        for i, rec in enumerate(recommendations[:10], 1):
            report.append(f"\n{i}. {rec['title']}")
            report.append(f"   👍 {rec['votes']} | {rec['category']}")
            report.append(f"   💭 {rec['reason']}")
            report.append(f"   🔗 {rec['url']}")

        return "\n".join(report)

    def clear_and_collect(self, limit: int = 30) -> dict:
        """DBをクリアしてから収集"""
        print("\n🗑️  データベースをクリア中...")
        self.scraper.clear_db()
        print("✅ クリア完了")

        print(f"\n🔍 Hacker News トレンドを取得中（上位{limit}件）...")
        stories = self.scraper.get_top_stories(limit=limit)
        print(f"  {len(stories)} 件取得")

        if stories:
            print("\n💾 データベースに保存中...")
            saved = self.scraper.save_products(stories)
            print(f"  {saved} 件保存")

            # サマリー作成
            print("\n📝 サマリーを作成中...")
            summary = self.create_summary_report()

            # ファイルに保存
            report_path = os.path.join(
                os.path.dirname(__file__),
                f"ideas_summary_{datetime.now().strftime('%Y%m%d_%H%M')}.md"
            )
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(summary)

            print(f"\n📄 サマリー保存: {report_path}")

            # JSONエクスポート
            export_path = os.path.join(
                os.path.dirname(__file__),
                f"ideas_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
            )

            # データ取得
            cursor = self.conn.cursor()
            cursor.execute('SELECT * FROM products ORDER BY votes DESC')
            columns = [desc[0] for desc in cursor.description]
            products = [dict(zip(columns, row)) for row in cursor.fetchall()]

            for p in products:
                if p['topics']:
                    p['topics'] = json.loads(p['topics'])

            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(products, f, ensure_ascii=False, indent=2)

            print(f"📄 データエクスポート: {export_path}")

            return {
                'success': True,
                'products_count': len(stories),
                'summary_path': report_path,
                'export_path': export_path
            }
        else:
            return {
                'success': False,
                'error': 'ストーリーを取得できませんでした'
            }

    def create_summary_from_existing(self, limit: int = 50) -> dict:
        """DBをクリアせずに既存データでサマリー作成"""
        print(f"\n🔍 Hacker News トレンドを追加取得（上位{limit}件）...")
        stories = self.scraper.get_top_stories(limit=limit)
        print(f"  {len(stories)} 件取得")

        if stories:
            print("\n💾 データベースに追加中...")
            saved = self.scraper.save_products(stories)
            print(f"  {saved} 件保存（重複除外済み）")

            # 現在のDB内のエントリー数を確認
            cursor = self.conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM products')
            total_count = cursor.fetchone()[0]
            print(f"\n📊 現在の総エントリー数: {total_count}")

            # サマリー作成
            print("\n📝 サマリーを作成中...")
            summary = self.create_summary_report()

            # ファイルに保存
            report_path = os.path.join(
                os.path.dirname(__file__),
                f"ideas_summary_{datetime.now().strftime('%Y%m%d_%H%M')}.md"
            )
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(summary)

            print(f"\n📄 サマリー保存: {report_path}")

            # JSONエクスポート
            export_path = os.path.join(
                os.path.dirname(__file__),
                f"ideas_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
            )

            # データ取得
            cursor.execute('SELECT * FROM products ORDER BY votes DESC')
            columns = [desc[0] for desc in cursor.description]
            products = [dict(zip(columns, row)) for row in cursor.fetchall()]

            for p in products:
                if p['topics']:
                    p['topics'] = json.loads(p['topics'])

            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(products, f, ensure_ascii=False, indent=2)

            print(f"📄 データエクスポート: {export_path}")

            return {
                'success': True,
                'products_count': saved,
                'total_count': total_count,
                'summary_path': report_path,
                'export_path': export_path
            }
        else:
            return {
                'success': False,
                'error': 'ストーリーを取得できませんでした'
            }

def main():
    """メイン処理"""
    print("=" * 60)
    print("🎯 Hacker News アイデアまとめ・提案ツール")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    summarizer = IdeasSummarizer()
    # DBをクリアせずに、既存データを維持したままサマリー作成
    result = summarizer.create_summary_from_existing(limit=50)

    if result['success']:
        print("\n" + "=" * 60)
        print("✅ 完了！")
        print("=" * 60)

        # サマリーを表示
        print("\n" + summarizer.create_summary_report())
    else:
        print(f"\n❌ エラー: {result.get('error', '不明')}")

if __name__ == "__main__":
    main()
