#!/usr/bin/env python3
"""
ProductHunt アイディア倉庫管理ツール
コマンドラインでアイディアを管理
"""

import sqlite3
import json
import sys
import os
from datetime import datetime
from typing import List, Dict

class IdeaManager:
    """アイディア管理マネージャー"""

    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = os.path.join(
                os.path.dirname(__file__),
                "producthunt_ideas.db"
            )
        self.db_path = db_path

    def list(self, status: str = None, min_votes: int = 0, limit: int = 50):
        """プロダクト一覧を表示"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query = '''
            SELECT p.*, n.note, n.priority, n.status
            FROM products p
            LEFT JOIN idea_notes n ON p.id = n.product_id
            WHERE p.votes >= ?
        '''
        params = [min_votes]

        if status:
            query += ' AND n.status = ?'
            params.append(status)

        query += ' ORDER BY p.votes DESC LIMIT ?'
        params.append(limit)

        cursor.execute(query, params)
        rows = cursor.fetchall()

        columns = [desc[0] for desc in cursor.description]

        print(f"\n📋 アイディア一覧 ({len(rows)}件)")
        print("=" * 100)

        for row in rows:
            p = dict(zip(columns, row))

            # ステータスアイコン
            status_icons = {
                'new': '🆕',
                'researching': '🔍',
                'planning': '📝',
                'developing': '🔨',
                'completed': '✅',
                'skipped': '⏭️'
            }

            status_icon = status_icons.get(p['status'], '❓')

            print(f"\n{status_icon} {p['name']} (👍 {p['votes']})")
            print(f"   {p['tagline']}")
            print(f"   {p['description'][:70]}...")
            print(f"   🔗 {p['url']}")

            if p['note']:
                print(f"   💬 メモ: {p['note']}")

            if p['topics']:
                topics = json.loads(p['topics'])
                print(f"   🏷️  {', '.join(topics)}")

        conn.close()

    def add_note(self, product_id: str, note: str, priority: int = 0, status: str = 'researching'):
        """ノートを追加"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        now = datetime.now().isoformat()

        cursor.execute('''
            INSERT OR REPLACE INTO idea_notes
            (product_id, note, priority, status, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (product_id, note, priority, status, now, now))

        conn.commit()
        conn.close()

        print(f"✅ ノートを追加しました: {product_id}")

    def update_status(self, product_id: str, status: str):
        """ステータスを更新"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            UPDATE idea_notes
            SET status = ?, updated_at = ?
            WHERE product_id = ?
        ''', (status, datetime.now().isoformat(), product_id))

        if cursor.rowcount > 0:
            print(f"✅ ステータスを更新しました: {product_id} -> {status}")
        else:
            print(f"❌ 見つかりません: {product_id}")

        conn.commit()
        conn.close()

    def search(self, keyword: str):
        """キーワード検索"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query = '''
            SELECT p.*, n.note, n.status
            FROM products p
            LEFT JOIN idea_notes n ON p.id = n.product_id
            WHERE p.name LIKE ? OR p.description LIKE ? OR p.tagline LIKE ? OR n.note LIKE ?
            ORDER BY p.votes DESC
        '''

        search_pattern = f"%{keyword}%"
        cursor.execute(query, [search_pattern] * 4)
        rows = cursor.fetchall()

        columns = [desc[0] for desc in cursor.description]

        print(f"\n🔍 検索結果: '{keyword}' ({len(rows)}件)")
        print("=" * 100)

        for row in rows:
            p = dict(zip(columns, row))

            print(f"\n🔹 {p['name']} (👍 {p['votes']})")
            print(f"   {p['tagline']}")
            print(f"   🔗 {p['url']}")

            if p['status']:
                print(f"   ステータス: {p['status']}")
            if p['note']:
                print(f"   💬 {p['note']}")

        conn.close()

    def stats(self):
        """統計情報表示"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        print("\n📊 統計情報")
        print("=" * 40)

        # 全体
        cursor.execute('SELECT COUNT(*) FROM products')
        total = cursor.fetchone()[0]
        print(f"総プロダクト数: {total}")

        cursor.execute('SELECT COUNT(*) FROM idea_notes')
        notes = cursor.fetchone()[0]
        print(f"ノート付き: {notes}")

        cursor.execute('SELECT AVG(votes), MAX(votes), MIN(votes) FROM products')
        avg, max_v, min_v = cursor.fetchone()
        print(f"平均👍: {avg:.1f}  |  最大: {max_v}  |  最小: {min_v}")

        # ステータス別
        cursor.execute('SELECT status, COUNT(*) FROM idea_notes GROUP BY status')
        status_counts = cursor.fetchall()

        if status_counts:
            print("\nステータス別:")
            for status, count in status_counts:
                print(f"  {status}: {count}")

        # トピック別
        cursor.execute('SELECT topics FROM products WHERE topics IS NOT NULL')
        all_topics = []
        for row in cursor.fetchall():
            topics = json.loads(row[0])
            all_topics.extend(topics)

        if all_topics:
            from collections import Counter
            topic_counts = Counter(all_topics)
            print("\n人気のトピック:")
            for topic, count in topic_counts.most_common(5):
                print(f"  {topic}: {count}")

        conn.close()

    def show_product(self, product_id: str):
        """プロダクト詳細を表示"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        query = '''
            SELECT p.*, n.note, n.priority, n.status, n.created_at, n.updated_at
            FROM products p
            LEFT JOIN idea_notes n ON p.id = n.product_id
            WHERE p.id = ?
        '''

        cursor.execute(query, [product_id])
        row = cursor.fetchone()

        if row:
            columns = [desc[0] for desc in cursor.description]
            p = dict(zip(columns, row))

            print(f"\n📦 {p['name']}")
            print("=" * 100)
            print(f"\n📝 説明:")
            print(f"   {p['description']}")
            print(f"\n🎯 キャッチコピー:")
            print(f"   {p['tagline']}")
            print(f"\n📊 メトリクス:")
            print(f"   👍 投票: {p['votes']}")
            print(f"   💬 コメント: {p['comments']}")
            print(f"\n🔗 URL:")
            print(f"   {p['url']}")
            print(f"\n📅 登録日:")
            print(f"   {p['launch_date']}")
            print(f"\n🕐 スクレイプ日時:")
            print(f"   {p['scraped_at']}")

            if p['topics']:
                topics = json.loads(p['topics'])
                print(f"\n🏷️  トピック:")
                print(f"   {', '.join(topics)}")

            if p['note'] or p['status']:
                print(f"\n💼 私のノート:")
                if p['status']:
                    print(f"   ステータス: {p['status']}")
                if p['priority']:
                    priorities = ['未分類', '低', '中', '高']
                    print(f"   優先度: {priorities[p['priority']]}")
                if p['note']:
                    print(f"   メモ: {p['note']}")
                if p['created_at']:
                    print(f"   作成日: {p['created_at']}")
                if p['updated_at']:
                    print(f"   更新日: {p['updated_at']}")
        else:
            print(f"❌ 見つかりません: {product_id}")

        conn.close()

def print_help():
    """ヘルプ表示"""
    print("""
🚀 ProductHunt アイディア倉庫管理ツール

使い方:
  python3 producthunt-ideas.py <コマンド> [オプション]

コマンド:
  list                    アイディア一覧を表示
    --status STATUS       ステータスでフィルタ (new/researching/planning/developing/completed/skipped)
    --min-votes N        最低投票数
    --limit N            表示件数 (デフォルト: 50)

  note <ID> <NOTE>      ノートを追加
    --priority N         優先度 (0=未分類, 1=低, 2=中, 3=高)
    --status STATUS      ステータス (デフォルト: researching)

  status <ID> <STATUS>  ステータスを更新

  search <KEYWORD>      キーワード検索

  show <ID>             プロダクト詳細を表示

  stats                 統計情報を表示

  help                  このヘルプを表示

例:
  python3 producthunt-ideas.py list
  python3 producthunt-ideas.py list --status planning --limit 20
  python3 producthunt-ideas.py note test-1 "面白いアイディア！似たものを作ってみたい" --priority 3
  python3 producthunt-ideas.py status test-1 planning
  python3 producthunt-ideas.py search "AI"
  python3 producthunt-ideas.py stats
""")

def main():
    """メイン処理"""
    if len(sys.argv) < 2:
        print_help()
        return

    manager = IdeaManager()
    command = sys.argv[1].lower()

    if command == 'list':
        status = None
        min_votes = 0
        limit = 50

        i = 2
        while i < len(sys.argv):
            if sys.argv[i] == '--status' and i + 1 < len(sys.argv):
                status = sys.argv[i + 1]
                i += 2
            elif sys.argv[i] == '--min-votes' and i + 1 < len(sys.argv):
                min_votes = int(sys.argv[i + 1])
                i += 2
            elif sys.argv[i] == '--limit' and i + 1 < len(sys.argv):
                limit = int(sys.argv[i + 1])
                i += 2
            else:
                i += 1

        manager.list(status=status, min_votes=min_votes, limit=limit)

    elif command == 'note' and len(sys.argv) >= 3:
        product_id = sys.argv[2]
        note = sys.argv[3] if len(sys.argv) > 3 else ""

        priority = 0
        status = 'researching'

        i = 4
        while i < len(sys.argv):
            if sys.argv[i] == '--priority' and i + 1 < len(sys.argv):
                priority = int(sys.argv[i + 1])
                i += 2
            elif sys.argv[i] == '--status' and i + 1 < len(sys.argv):
                status = sys.argv[i + 1]
                i += 2
            else:
                i += 1

        manager.add_note(product_id, note, priority, status)

    elif command == 'status' and len(sys.argv) >= 3:
        product_id = sys.argv[2]
        status = sys.argv[3] if len(sys.argv) > 3 else 'new'
        manager.update_status(product_id, status)

    elif command == 'search' and len(sys.argv) >= 3:
        keyword = sys.argv[2]
        manager.search(keyword)

    elif command == 'show' and len(sys.argv) >= 3:
        product_id = sys.argv[2]
        manager.show_product(product_id)

    elif command == 'stats':
        manager.stats()

    elif command == 'help':
        print_help()

    else:
        print(f"❌ 不明なコマンド: {command}")
        print_help()

if __name__ == "__main__":
    main()
