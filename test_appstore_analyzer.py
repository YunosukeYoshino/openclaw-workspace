#!/usr/bin/env python3
"""
App Store アナライザーの簡易テスト
実際のAPI呼び出しなしで、分析機能だけをテスト
"""

import sqlite3
import json
import os
import sys
import importlib.util

# appstore-top-gainers.pyを動的インポート
spec = importlib.util.spec_from_file_location("appstore_top_gainers", os.path.join(os.path.dirname(__file__), "appstore-top-gainers.py"))
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

AppStoreAnalyzer = module.AppStoreAnalyzer

def create_dummy_data(analyzer: AppStoreAnalyzer):
    """ダミーデータを作成"""

    # アプリを追加
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
        {
            'title': '使いにくい',
            'author': 'user1',
            'text': 'UIが複雑すぎて使いにくい。ボタンが多くて何が何だかわからない。',
            'rating': 1,
            'version': '1.0',
            'date': '2026-01-15'
        },
        {
            'title': '機能不足',
            'author': 'user2',
            'text': 'フィルター機能が足りない。もっと多くのエフェクトが欲しい。',
            'rating': 2,
            'version': '1.0',
            'date': '2026-01-16'
        },
        {
            'title': '遅い',
            'author': 'user3',
            'text': '起動が遅い。写真を撮るまでに時間がかかる。',
            'rating': 1,
            'version': '1.0',
            'date': '2026-01-17'
        },
        {
            'title': '会員登録が強制',
            'author': 'user4',
            'text': '会員登録しないと使えない。無料で使わせてほしい。',
            'rating': 1,
            'version': '1.1',
            'date': '2026-01-18'
        },
        {
            'title': '広告が多い',
            'author': 'user5',
            'text': '広告が多すぎて邪魔。課金すれば消えるけど高すぎる。',
            'rating': 1,
            'version': '1.1',
            'date': '2026-01-19'
        },
        {
            'title': 'UIが複雑すぎて使いにくい',
            'author': 'user6',
            'text': 'UIが複雑すぎて使いにくい。初心者にはおすすめできない。',
            'rating': 1,
            'version': '1.0',
            'date': '2026-01-20'
        },
        {
            'title': '使いにくい',
            'author': 'user7',
            'text': '使いにくい。シンプルにしてほしい。',
            'rating': 2,
            'version': '1.0',
            'date': '2026-01-21'
        },
        {
            'title': '機能が足りない',
            'author': 'user8',
            'text': '編集機能が足りない。トリミングだけじゃ不十分。',
            'rating': 1,
            'version': '1.2',
            'date': '2026-01-22'
        },
        {
            'title': '重い',
            'author': 'user9',
            'text': '重い。動作がもっさりしている。もっと軽くしてほしい。',
            'rating': 2,
            'version': '1.2',
            'date': '2026-01-23'
        },
        {
            'title': 'バグだらけ',
            'author': 'user10',
            'text': 'よく落ちる。バグが多い。',
            'rating': 1,
            'version': '1.2',
            'date': '2026-01-24'
        },
    ]

    saved = analyzer.save_reviews(app_id, bad_reviews)
    print(f"✅ レビュー保存: {saved} 件")

    return app_id, app_data

def main():
    """メイン処理"""
    print("=" * 60)
    print("🧪 App Store アナライザー テスト")
    print("=" * 60)

    analyzer = AppStoreAnalyzer()

    # ダミーデータ作成
    app_id, app_data = create_dummy_data(analyzer)

    # 悪いレビューを取得
    print("\n🔍 悪いレビューを取得中...")
    bad_reviews = analyzer.get_bad_reviews(app_id, limit=50)
    print(f"✅ {len(bad_reviews)} 件取得")

    # 分析
    print("\n🎯 不満を分析中...")
    analysis = analyzer.analyze_issues(bad_reviews)

    print("\n📊 分析結果:")
    print(f"  要約: {analysis['summary']}")

    print("\n  テーマ別:")
    for theme in analysis['themes']:
        print(f"    {theme['theme']}: {theme['count']}回")

    print("\n  上位の不満:")
    for issue, count in analysis['top_issues'][:5]:
        print(f"    ({count}回) {issue[:60]}...")

    # レポート作成
    print("\n📝 レポートを作成中...")
    report = analyzer.create_analysis_report(app_data, bad_reviews, analysis)

    # レポートを保存
    from datetime import datetime
    report_path = os.path.join(
        os.path.dirname(__file__),
        f"appstore_test_{datetime.now().strftime('%Y%m%d_%H%M')}.md"
    )
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"✅ レポート保存: {report_path}")

    # レポートの一部を表示
    print("\n📄 レポートプレビュー:")
    print(report[:500] + "...\n")

    print("=" * 60)
    print("✅ テスト完了！")
    print("=" * 60)

if __name__ == "__main__":
    main()
