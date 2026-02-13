#!/usr/bin/env python3
"""
えっちコンテンツブックマークエージェント - メインモジュール
Erotic Content Bookmark Agent - Main Module

えっちなコンテンツのブックマーク管理を行うエージェント
"""

import re
from db import EroticBookmarkAgentDB


class EroticBookmarkAgent:
    """えっちコンテンツブックマークエージェント"""

    def __init__(self):
        """初期化"""
        self.db = EroticBookmarkAgentDB()
        self.db.initialize()

    def parse_message(self, message: str) -> dict:
        """メッセージを解析 / Parse message"""
        message = message.strip()

        # ブックマーク追加 / Add bookmark
        add_match = re.match(r'(?:ブックマーク|bookmark|ブクマ|bm)[:：]\s*(.+)', message, re.IGNORECASE)
        if add_match:
            return self._parse_add(add_match.group(1))

        # 更新 / Update
        update_match = re.match(r'(?:更新|update)[:：]\s*(\d+)\s*,\s*(.+)', message, re.IGNORECASE)
        if update_match:
            return self._parse_update(int(update_match.group(1)), update_match.group(2))

        # 削除 / Delete
        delete_match = re.match(r'(?:削除|delete|del)[:：]\s*(\d+)', message, re.IGNORECASE)
        if delete_match:
            return {'action': 'delete', 'bookmark_id': int(delete_match.group(1))}

        # 検索 / Search
        search_match = re.match(r'(?:検索|search)[:：]\s*(.+)', message, re.IGNORECASE)
        if search_match:
            return {'action': 'search', 'keyword': search_match.group(1)}

        # 一覧 / List
        list_match = re.match(r'(?:ブックマーク|bookmark|ブクマ)(?:一覧|list)?', message, re.IGNORECASE)
        if list_match:
            return {'action': 'list'}

        # カテゴリ一覧 / Category list
        if message.strip() in ['カテゴリ一覧', 'categories', 'cats']:
            return {'action': 'categories'}

        # タグ一覧 / Tag list
        if message.strip() in ['タグ一覧', 'tags']:
            return {'action': 'tags'}

        # 最近アクセス / Recently accessed
        if message.strip() in ['最近', 'recent', '履歴', 'history']:
            return {'action': 'recent'}

        # 統計 / Stats
        if message.strip() in ['統計', 'stats', 'ブックマーク統計']:
            return {'action': 'stats'}

        return None

    def _parse_add(self, content: str) -> dict:
        """追加コマンド解析"""
        result = {'action': 'add', 'url': None, 'title': None,
                  'description': None, 'tags': None, 'category': None}

        # URL
        url_match = re.search(r'https?://[^\s,、]+', content)
        if url_match:
            result['url'] = url_match.group(0).strip()
            content = content.replace(url_match.group(0), '', 1).strip()
        else:
            return None  # URLは必須

        # タイトル
        title_match = re.search(r'(?:タイトル|title)[:：]\s*([^,、]+)', content, re.IGNORECASE)
        if title_match:
            result['title'] = title_match.group(1).strip()

        # 説明
        desc_match = re.search(r'(?:説明|description|desc)[:：]\s*(.+)', content, re.IGNORECASE)
        if desc_match:
            result['description'] = desc_match.group(1).strip()

        # カテゴリ
        cat_match = re.search(r'(?:カテゴリ|category|cat)[:：]\s*([^,、]+)', content, re.IGNORECASE)
        if cat_match:
            result['category'] = cat_match.group(1).strip()

        # タグ
        tag_match = re.search(r'(?:タグ|tag)[:：]\s*(.+)', content, re.IGNORECASE)
        if tag_match:
            tags_str = tag_match.group(1).strip()
            result['tags'] = ', '.join([t.strip() for t in re.split(r'[,、\s]+', tags_str) if t.strip()])

        return result

    def _parse_update(self, bookmark_id: int, content: str) -> dict:
        """更新コマンド解析"""
        result = {'action': 'update', 'bookmark_id': bookmark_id, 'url': None,
                  'title': None, 'description': None, 'tags': None, 'category': None}

        # URL
        url_match = re.search(r'url[:：]\s*(https?://[^\s,、]+)', content, re.IGNORECASE)
        if url_match:
            result['url'] = url_match.group(1).strip()

        # タイトル
        title_match = re.search(r'(?:タイトル|title)[:：]\s*([^,、]+)', content, re.IGNORECASE)
        if title_match:
            result['title'] = title_match.group(1).strip()

        # 説明
        desc_match = re.search(r'(?:説明|description|desc)[:：]\s*(.+)', content, re.IGNORECASE)
        if desc_match:
            result['description'] = desc_match.group(1).strip()

        # カテゴリ
        cat_match = re.search(r'(?:カテゴリ|category|cat)[:：]\s*([^,、]+)', content, re.IGNORECASE)
        if cat_match:
            result['category'] = cat_match.group(1).strip()

        # タグ
        tag_match = re.search(r'(?:タグ|tag)[:：]\s*(.+)', content, re.IGNORECASE)
        if tag_match:
            tags_str = tag_match.group(1).strip()
            result['tags'] = ', '.join([t.strip() for t in re.split(r'[,、\s]+', tags_str) if t.strip()])

        return result

    def handle_message(self, message: str) -> str:
        """メッセージを処理 / Handle message"""
        parsed = self.parse_message(message)

        if not parsed:
            return None

        action = parsed['action']

        if action == 'add':
            if not parsed['url']:
                return "❌ URLを入力してください / Please enter a URL"

            bookmark_id = self.db.add_bookmark(
                url=parsed['url'],
                title=parsed['title'] or "",
                description=parsed['description'] or "",
                tags=parsed['tags'] or "",
                category=parsed['category'] or ""
            )

            response = f"✅ ブックマーク #{bookmark_id} 追加完了 / Bookmark added\n"
            response += f"URL: {parsed['url']}\n"
            if parsed['title']:
                response += f"タイトル / Title: {parsed['title']}\n"
            if parsed['category']:
                response += f"カテゴリ / Category: {parsed['category']}\n"
            if parsed['tags']:
                response += f"タグ / Tags: {parsed['tags']}"

            return response

        elif action == 'update':
            success = self.db.update_bookmark(
                parsed['bookmark_id'],
                url=parsed['url'],
                title=parsed['title'],
                description=parsed['description'],
                tags=parsed['tags'],
                category=parsed['category']
            )

            if not success:
                return f"❌ ブックマーク #{parsed['bookmark_id']} が見つかりません / Bookmark not found"

            response = f"✏️ ブックマーク #{parsed['bookmark_id']} 更新完了 / Bookmark updated\n"
            if parsed['title']:
                response += f"タイトル / Title: {parsed['title']}\n"
            if parsed['category']:
                response += f"カテゴリ / Category: {parsed['category']}"
            return response

        elif action == 'delete':
            success = self.db.delete_bookmark(parsed['bookmark_id'])
            if success:
                return f"🗑️ ブックマーク #{parsed['bookmark_id']} 削除完了 / Bookmark deleted"
            return f"❌ ブックマーク #{parsed['bookmark_id']} が見つかりません / Bookmark not found"

        elif action == 'search':
            keyword = parsed['keyword']
            bookmarks = self.db.search_bookmarks(keyword)

            if not bookmarks:
                return f"🔍 「{keyword}」の検索結果: 見つかりませんでした / No results found for \"{keyword}\""

            response = f"🔍 「{keyword}」の検索結果 ({len(bookmarks)}件 / results):\n"
            for bookmark in bookmarks:
                response += self._format_bookmark(bookmark)
            return response

        elif action == 'list':
            bookmarks = self.db.list_bookmarks()

            if not bookmarks:
                return "📋 ブックマークがありません / No bookmarks found"

            response = f"📋 ブックマーク一覧 ({len(bookmarks)}件 / bookmarks):\n"
            for bookmark in bookmarks:
                response += self._format_bookmark(bookmark)
            return response

        elif action == 'categories':
            categories = self.db.get_categories()

            if not categories:
                return "📁 カテゴリがありません / No categories found"

            response = "📁 カテゴリ一覧 / Categories:\n"
            for cat in categories:
                response += f"  • {cat}\n"
            return response

        elif action == 'tags':
            tags = self.db.get_tags()

            if not tags:
                return "🏷️ タグがありません / No tags found"

            response = "🏷️ タグ一覧 / Tags:\n"
            for tag in tags:
                response += f"  • {tag}\n"
            return response

        elif action == 'recent':
            bookmarks = self.db.get_recently_accessed()

            if not bookmarks:
                return "🕐 最近アクセスしたブックマークがありません / No recently accessed bookmarks"

            response = f"🕐 最近アクセスしたブックマーク ({len(bookmarks)}件 / bookmarks):\n"
            for bookmark in bookmarks:
                response += self._format_bookmark(bookmark, show_accessed=True)
            return response

        elif action == 'stats':
            stats = self.db.get_stats()

            response = "📊 ブックマーク統計 / Bookmark Stats:\n"
            response += f"全ブックマーク数 / Total: {stats['total_bookmarks']}件\n"
            response += f"最近7日間の追加 / Added last 7 days: {stats['recent_added']}件\n"
            response += f"最近7日間のアクセス / Accessed last 7 days: {stats['recent_accessed']}件"

            if stats['top_categories']:
                response += f"\n\nトップカテゴリ / Top categories:\n"
                for cat, count in list(stats['top_categories'].items())[:5]:
                    response += f"  • {cat}: {count}件"

            return response

        return None

    def _format_bookmark(self, bookmark: dict, show_accessed: bool = False) -> str:
        """ブックマークをフォーマット"""
        id, url, title, description, tags, category, created_at, last_accessed = \
            bookmark['id'], bookmark['url'], bookmark['title'], \
            bookmark['description'], bookmark['tags'], bookmark['category'], \
            bookmark['created_at'], bookmark['last_accessed']

        response = f"\n🔗 [{id}] "
        response += f"{title if title else url[:50]}...\n"
        if description:
            response += f"    💬 {description[:100]}...\n"
        response += f"    🔗 {url}\n"
        if category:
            response += f"    📁 {category}\n"
        if tags:
            response += f"    🏷️ {tags}\n"
        if show_accessed and last_accessed:
            response += f"    🕐 最終アクセス: {last_accessed[:10]}"
        else:
            response += f"    📅 追加日: {created_at[:10]}"

        return response


if __name__ == '__main__':
    agent = EroticBookmarkAgent()

    test_messages = [
        "ブックマーク: https://example.com, タイトル:Example Site, カテゴリ:Work",
        "ブックマーク: https://github.com, タグ:code, git, dev",
        "タグ: code",
        "検索: github",
        "ブックマーク一覧",
        "stats",
    ]

    for msg in test_messages:
        print(f"\n入力 / Input: {msg}")
        result = agent.handle_message(msg)
        if result:
            print(result)
