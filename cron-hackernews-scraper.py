#!/usr/bin/env python3
"""
Hacker News トレンド収集（cron用）
毎日15時に実行
"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

import importlib.util
spec = importlib.util.spec_from_file_location("hackernews_scraper", os.path.join(os.path.dirname(__file__), "hackernews-scraper.py"))
hackernews_scraper = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hackernews_scraper)
HackerNewsScraper = hackernews_scraper.HackerNewsScraper
from datetime import datetime

def main():
    """メイン処理"""
    scraper = HackerNewsScraper()

    print(f"{'='*60}")
    print(f"🕒 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Hacker News トレンド収集開始")
    print(f"{'='*60}")

    stories = scraper.get_top_stories(limit=30)

    if stories:
        print(f"\n✅ {len(stories)} 件のストーリーを取得")

        saved = scraper.save_products(stories)
        print(f"✅ {saved} 件を保存")

        # 統計を表示
        conn = scraper._connect()
        cursor = conn.cursor()

        cursor.execute('SELECT COUNT(*) FROM products')
        total = cursor.fetchone()[0]

        cursor.execute('SELECT COUNT(DISTINCT id) FROM products WHERE scraped_at >= date("now", "-3 days")')
        recent = cursor.fetchone()[0]

        print(f"\n📊 データベース状態:")
        print(f"   総プロダクト数: {total}")
        print(f"   過去3日間: {recent}")

        conn.close()
    else:
        print("❌ ストーリーを取得できませんでした")

    print(f"\n{'='*60}")
    print(f"✅ 収集完了")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
