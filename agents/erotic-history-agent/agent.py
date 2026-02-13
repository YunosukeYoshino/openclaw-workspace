#!/usr/bin/env python3
"""
えっちコンテンツ閲覧履歴エージェント - メインモジュール
Erotic Content History Agent - Main Module

えっちなコンテンツの閲覧履歴を記録・管理するエージェント
"""

import re
from datetime import datetime, timedelta
from db import EroticHistoryAgentDB


class EroticHistoryAgent:
    """えっちコンテンツ閲覧履歴エージェント"""

    def __init__(self):
        """初期化"""
        self.db = EroticHistoryAgentDB()
        self.db.initialize()

    def parse_message(self, message: str) -> dict:
        """メッセージを解析 / Parse message"""
        message = message.strip()

        # 履歴追加 / Add history
        add_match = re.match(r'(?:履歴|history|閲覧|view)[:：]\s*(.+)', message, re.IGNORECASE)
        if add_match:
            return self._parse_add(add_match.group(1))

        # 削除 / Delete
        delete_match = re.match(r'(?:削除|delete|del)[:：]\s*(\d+)', message, re.IGNORECASE)
        if delete_match:
            return {'action': 'delete', 'history_id': int(delete_match.group(1))}

        # 検索 / Search
        search_match = re.match(r'(?:検索|search)[:：]\s*(.+)', message, re.IGNORECASE)
        if search_match:
            return {'action': 'search', 'keyword': search_match.group(1)}

        # 一覧 / List
        list_match = re.match(r'(?:履歴|history)(?:一覧|list)?', message, re.IGNORECASE)
        if list_match:
            return {'action': 'list'}

        # 最近の履歴 / Recent history
        if message.strip() in ['最近', 'recent', '最新']:
            return {'action': 'recent'}

        # アーティスト別 / By artist
        artist_match = re.match(r'(?:アーティスト|artist)[:：]\s*(.+)', message, re.IGNORECASE)
        if artist_match:
            return {'action': 'list_artist', 'artist': artist_match.group(1)}

        # ソース別 / By source
        source_match = re.match(r'(?:ソース|source|サイト|site)[:：]\s*(.+)', message, re.IGNORECASE)
        if source_match:
            return {'action': 'list_source', 'source': source_match.group(1)}

        # 最多閲覧 / Most viewed
        if message.strip() in ['top', '最多', '人気']:
            return {'action': 'most_viewed'}

        # 統計 / Stats
        if message.strip() in ['統計', 'stats', '履歴統計']:
            return {'action': 'stats'}

        # クリア / Clear
        clear_old_match = re.match(r'(?:クリア|clear|削除|delete)[:：]\s*(?:古い|old|全|all)?\s*(\d+)?', message, re.IGNORECASE)
        if clear_old_match:
            days = int(clear_old_match.group(1)) if clear_old_match.group(1) else None
            return {'action': 'clear', 'days': days}

        return None

    def _parse_add(self, content: str) -> dict:
        """追加コマンド解析"""
        result = {'action': 'add', 'content_id': None, 'content_title': None,
                  'artist': None, 'tags': None, 'source': None}

        # コンテンツID
        id_match = re.search(r'(?:id|コンテンツID|content_id)[:：]\s*(\S+)', content, re.IGNORECASE)
        if id_match:
            result['content_id'] = id_match.group(1).strip()
            content = content.replace(id_match.group(0), '', 1).strip()

        # タイトル
        title_match = re.search(r'(?:タイトル|title)[:：]\s*([^,、]+)', content, re.IGNORECASE)
        if title_match:
            result['content_title'] = title_match.group(1).strip()
            content = content.replace(title_match.group(0), '', 1).strip()

        # アーティスト
        artist_match = re.search(r'(?:アーティスト|artist)[:：]\s*([^,、]+)', content, re.IGNORECASE)
        if artist_match:
            result['artist'] = artist_match.group(1).strip()
            content = content.replace(artist_match.group(0), '', 1).strip()

        # ソース
        source_match = re.search(r'(?:ソース|source|サイト|site)[:：]\s*([^,、]+)', content, re.IGNORECASE)
        if source_match:
            result['source'] = source_match.group(1).strip()

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
            if not parsed['content_id']:
                return "❌ コンテンツIDを入力してください / Please enter a content ID"

            history_id = self.db.add_history(
                content_id=parsed['content_id'],
                content_title=parsed['content_title'] or "タイトルなし",
                artist=parsed['artist'] or "",
                tags=parsed['tags'] or "",
                source=parsed['source'] or ""
            )

            response = f"✅ 履歴 #{history_id} 追加完了 / History added\n"
            response += f"タイトル / Title: {parsed['content_title'] or 'タイトルなし'}\n"
            if parsed['artist']:
                response += f"アーティスト / Artist: {parsed['artist']}\n"
            if parsed['source']:
                response += f"ソース / Source: {parsed['source']}"
            return response

        elif action == 'delete':
            success = self.db.delete_history(parsed['history_id'])
            if success:
                return f"🗑️ 履歴 #{parsed['history_id']} 削除完了 / History deleted"
            return f"❌ 履歴 #{parsed['history_id']} が見つかりません / History not found"

        elif action == 'clear':
            if parsed['days']:
                deleted = self.db.clear_old_history(parsed['days'])
                return f"🧹 過去{parsed['days']}日間の履歴 {deleted}件を削除 / Deleted {deleted} records from last {parsed['days']} days"
            else:
                count = self.db.clear_all_history()
                return f"🧹 全履歴 {count}件を削除 / Deleted all {count} history records"

        elif action == 'search':
            keyword = parsed['keyword']
            history = self.db.search_history(keyword)

            if not history:
                return f"🔍 「{keyword}」の検索結果: 見つかりませんでした / No results found for \"{keyword}\""

            response = f"🔍 「{keyword}」の検索結果 ({len(history)}件 / results):\n"
            for item in history:
                response += self._format_history(item)
            return response

        elif action == 'list':
            history = self.db.list_history()

            if not history:
                return "📋 履歴がありません / No history found"

            response = f"📋 履歴一覧 ({len(history)}件 / records):\n"
            for item in history:
                response += self._format_history(item)
            return response

        elif action == 'recent':
            history = self.db.get_recent_history()

            if not history:
                return "🕐 最近の履歴がありません / No recent history"

            response = f"🕐 最近の履歴 ({len(history)}件 / records):\n"
            for item in history:
                response += self._format_history(item, compact=True)
            return response

        elif action == 'list_artist':
            artist = parsed['artist']
            history = self.db.get_history_by_artist(artist)

            if not history:
                return f"🎨 アーティスト「{artist}」の履歴: 見つかりませんでした / No history found for artist \"{artist}\""

            response = f"🎨 アーティスト「{artist}」の履歴 ({len(history)}件 / records):\n"
            for item in history:
                response += self._format_history(item)
            return response

        elif action == 'list_source':
            source = parsed['source']
            history = self.db.get_history_by_source(source)

            if not history:
                return f"🌐 ソース「{source}」の履歴: 見つかりませんでした / No history found for source \"{source}\""

            response = f"🌐 ソース「{source}」の履歴 ({len(history)}件 / records):\n"
            for item in history:
                response += self._format_history(item)
            return response

        elif action == 'most_viewed':
            content = self.db.get_most_viewed(10)

            if not content:
                return "🔥 最多閲覧コンテンツがありません / No most viewed content found"

            response = "🔥 最多閲覧コンテンツ Top 10:\n"
            for i, item in enumerate(content, 1):
                response += f"\n#{i} "
                response += f"{item['content_title']} ({item['view_count']}回)\n"
                if item['artist']:
                    response += f"    🎨 {item['artist']}\n"
                response += f"    🕐 最終閲覧: {item['last_viewed'][:10]}"
            return response

        elif action == 'stats':
            stats = self.db.get_stats()

            response = "📊 履歴統計 / History Stats:\n"
            response += f"総閲覧数 / Total views: {stats['total_views']}件\n"
            response += f"一意なコンテンツ / Unique content: {stats['unique_content']}件\n"
            response += f"トップアーティスト / Top artist: {stats['top_artist']}\n"
            response += f"今日の閲覧 / Today's views: {stats['views_today']}件\n"
            response += f"過去7日間の閲覧 / Last 7 days: {stats['views_last_7days']}件"

            if stats['sources']:
                response += "\n\nソース別 / By source:\n"
                for source, count in list(stats['sources'].items())[:5]:
                    response += f"  • {source}: {count}件"

            return response

        return None

    def _format_history(self, item: dict, compact: bool = False) -> str:
        """履歴をフォーマット"""
        if compact:
            return f"📝 {item['content_title']} - {item['viewed_at'][:10]}\n"

        id, content_id, content_title, artist, viewed_at, tags, source = \
            item['id'], item['content_id'], item['content_title'], \
            item['artist'], item['viewed_at'], item['tags'], item['source']

        response = f"\n📝 [{id}] {content_title}\n"
        if artist:
            response += f"    🎨 {artist}\n"
        if source:
            response += f"    🌐 {source}\n"
        if tags:
            response += f"    🏷️ {tags}\n"
        response += f"    🕐 {viewed_at}"

        return response


if __name__ == '__main__':
    agent = EroticHistoryAgent()

    test_messages = [
        "履歴: id:001, タイトル:素晴らしい作品, アーティスト:Name",
        "アーティスト: テスト",
        "最近",
        "top",
        "stats",
    ]

    for msg in test_messages:
        print(f"\n入力 / Input: {msg}")
        result = agent.handle_message(msg)
        if result:
            print(result)
