#!/usr/bin/env python3
"""
えっちコンテンツ高度検索エージェント - メインモジュール
Erotic Content Advanced Search Agent - Main Module

えっちなコンテンツの高度な検索機能を提供するエージェント
"""

import re
from db import EroticSearchAgentDB


class EroticSearchAgent:
    """えっちコンテンツ高度検索エージェント"""

    def __init__(self):
        """初期化"""
        self.db = EroticSearchAgentDB()
        self.db.initialize()

    def parse_message(self, message: str) -> dict:
        """メッセージを解析 / Parse message"""
        message = message.strip()

        # 検索 / Search
        search_match = re.match(r'(?:検索|search)[:：]\s*(.+)', message, re.IGNORECASE)
        if search_match:
            return self._parse_search(search_match.group(1))

        # インデックス追加 / Add to index
        add_match = re.match(r'(?:追加|add|index)[:：]\s*(.+)', message, re.IGNORECASE)
        if add_match:
            return self._parse_add(add_match.group(1))

        # インデックス削除 / Delete from index
        delete_match = re.match(r'(?:削除|delete|del)[:：]\s*(\d+)', message, re.IGNORECASE)
        if delete_match:
            return {'action': 'delete', 'index_id': int(delete_match.group(1))}

        # インデックス更新 / Update index
        update_match = re.match(r'(?:更新|update)[:：]\s*(\d+)\s*,\s*(.+)', message, re.IGNORECASE)
        if update_match:
            return self._parse_update(int(update_match.group(1)), update_match.group(2))

        # 検索履歴 / Search history
        if message.strip() in ['履歴', 'history', '検索履歴']:
            return {'action': 'history'}

        # タグ検索 / Tag search
        tag_match = re.match(r'(?:タグ|tag)[:：]\s*(.+)', message, re.IGNORECASE)
        if tag_match:
            return {'action': 'tag_search', 'tag': tag_match.group(1)}

        # アーティスト検索 / Artist search
        artist_match = re.match(r'(?:アーティスト|artist)[:：]\s*(.+)', message, re.IGNORECASE)
        if artist_match:
            return {'action': 'artist_search', 'artist': artist_match.group(1)}

        # 統計 / Stats
        if message.strip() in ['統計', 'stats', 'インデックス統計']:
            return {'action': 'stats'}

        # 再構築 / Rebuild
        if message.strip() in ['再構築', 'rebuild', 'reindex']:
            return {'action': 'rebuild'}

        return None

    def _parse_search(self, content: str) -> dict:
        """検索コマンド解析"""
        result = {'action': 'search', 'keyword': None, 'tag': None,
                  'artist': None, 'source': None}
        content = content.strip()

        # キーワード
        keyword_match = re.search(r'(?:キーワード|keyword|kw)[:：]\s*(.+)', content, re.IGNORECASE)
        if keyword_match:
            result['keyword'] = keyword_match.group(1).strip()
            content = content.replace(keyword_match.group(0), '', 1).strip()

        # タグ
        tag_match = re.search(r'(?:タグ|tag)[:：]\s*(.+)', content, re.IGNORECASE)
        if tag_match:
            tags_str = tag_match.group(1).strip()
            result['tag'] = ', '.join([t.strip() for t in re.split(r'[,、\s]+', tags_str) if t.strip()])
            content = content.replace(tag_match.group(0), '', 1).strip()

        # アーティスト
        artist_match = re.search(r'(?:アーティスト|artist)[:：]\s*([^,、]+)', content, re.IGNORECASE)
        if artist_match:
            result['artist'] = artist_match.group(1).strip()

        # ソース
        source_match = re.search(r'(?:ソース|source)[:：]\s*(.+)', content, re.IGNORECASE)
        if source_match:
            result['source'] = source_match.group(1).strip()

        return result

    def _parse_add(self, content: str) -> dict:
        """追加コマンド解析"""
        result = {'action': 'add', 'content_id': None, 'title': None,
                  'artist': None, 'tags': None, 'description': None, 'source': None}
        content = content.strip()

        # コンテンツID
        id_match = re.search(r'(?:id|コンテンツID|content_id)[:：]\s*(\S+)', content, re.IGNORECASE)
        if id_match:
            result['content_id'] = id_match.group(1).strip()

        # タイトル
        title_match = re.search(r'(?:タイトル|title)[:：]\s*([^,、]+)', content, re.IGNORECASE)
        if title_match:
            result['title'] = title_match.group(1).strip()

        # アーティスト
        artist_match = re.search(r'(?:アーティスト|artist)[:：]\s*([^,、]+)', content, re.IGNORECASE)
        if artist_match:
            result['artist'] = artist_match.group(1).strip()

        # タグ
        tag_match = re.search(r'(?:タグ|tag)[:：]\s*(.+)', content, re.IGNORECASE)
        if tag_match:
            tags_str = tag_match.group(1).strip()
            result['tags'] = ', '.join([t.strip() for t in re.split(r'[,、\s]+', tags_str) if t.strip()])

        # 説明
        desc_match = re.search(r'(?:説明|desc|description)[:：]\s*(.+)', content, re.IGNORECASE)
        if desc_match:
            result['description'] = desc_match.group(1).strip()

        # ソース
        source_match = re.search(r'(?:ソース|source)[:：]\s*(.+)', content, re.IGNORECASE)
        if source_match:
            result['source'] = source_match.group(1).strip()

        return result

    def _parse_update(self, index_id: int, content: str) -> dict:
        """更新コマンド解析"""
        result = {'action': 'update', 'index_id': index_id, 'title': None,
                  'artist': None, 'tags': None, 'description': None, 'source': None}
        content = content.strip()

        # タイトル
        title_match = re.search(r'(?:タイトル|title)[:：]\s*([^,、]+)', content, re.IGNORECASE)
        if title_match:
            result['title'] = title_match.group(1).strip()

        # アーティスト
        artist_match = re.search(r'(?:アーティスト|artist)[:：]\s*([^,、]+)', content, re.IGNORECASE)
        if artist_match:
            result['artist'] = artist_match.group(1).strip()

        # タグ
        tag_match = re.search(r'(?:タグ|tag)[:：]\s*(.+)', content, re.IGNORECASE)
        if tag_match:
            tags_str = tag_match.group(1).strip()
            result['tags'] = ', '.join([t.strip() for t in re.split(r'[,、\s]+', tags_str) if t.strip()])

        # 説明
        desc_match = re.search(r'(?:説明|desc|description)[:：]\s*(.+)', content, re.IGNORECASE)
        if desc_match:
            result['description'] = desc_match.group(1).strip()

        # ソース
        source_match = re.search(r'(?:ソース|source)[:：]\s*(.+)', content, re.IGNORECASE)
        if source_match:
            result['source'] = source_match.group(1).strip()

        return result

    def handle_message(self, message: str) -> str:
        """メッセージを処理 / Handle message"""
        parsed = self.parse_message(message)

        if not parsed:
            return None

        action = parsed['action']

        if action == 'search':
            keyword = parsed.get('keyword')
            tag = parsed.get('tag')
            artist = parsed.get('artist')
            source = parsed.get('source')

            results = self.db.search(keyword=keyword, tag=tag, artist=artist, source=source)

            if not results:
                response = "🔍 検索結果: 0件 / No results found\n"
                if keyword:
                    response += f"キーワード / Keyword: {keyword}\n"
                if tag:
                    response += f"タグ / Tag: {tag}\n"
                if artist:
                    response += f"アーティスト / Artist: {artist}\n"
                return response

            response = f"🔍 検索結果: {len(results)}件 / {len(results)} results found\n"
            for i, result in enumerate(results, 1):
                response += self._format_result(result, i)
            return response

        elif action == 'add':
            if not parsed.get('content_id'):
                return "❌ コンテンツIDを入力してください / Please enter a content ID"

            try:
                index_id = self.db.add_to_index(
                    content_id=parsed['content_id'],
                    title=parsed.get('title') or "",
                    artist=parsed.get('artist') or "",
                    tags=parsed.get('tags') or "",
                    description=parsed.get('description') or "",
                    source=parsed.get('source') or ""
                )

                response = f"✅ インデックス #{index_id} 追加完了 / Added to index\n"
                if parsed['title']:
                    response += f"タイトル / Title: {parsed['title']}\n"
                if parsed['artist']:
                    response += f"アーティスト / Artist: {parsed['artist']}\n"
                if parsed['tags']:
                    response += f"タグ / Tags: {parsed['tags']}\n"
                return response
            except Exception as e:
                return f"❌ {str(e)}"

        elif action == 'update':
            try:
                success = self.db.update_index(
                    parsed['index_id'],
                    title=parsed.get('title'),
                    artist=parsed.get('artist'),
                    tags=parsed.get('tags'),
                    description=parsed.get('description'),
                    source=parsed.get('source')
                )

                if not success:
                    return f"❌ インデックス #{parsed['index_id']} が見つかりません / Index not found"

                response = f"✏️ インデックス #{parsed['index_id']} 更新完了 / Updated\n"
                return response
            except Exception as e:
                return f"❌ {str(e)}"

        elif action == 'delete':
            success = self.db.delete_from_index(parsed['index_id'])

            if success:
                return f"🗑️ インデックス #{parsed['index_id']} 削除完了 / Deleted from index"

            return f"❌ インデックス #{parsed['index_id']} が見つかりません / Index not found"

        elif action == 'history':
            history = self.db.get_search_history(limit=20)

            if not history:
                return "📋 検索履歴: なし / No search history"

            response = f"📋 検索履歴 (最近20件 / Recent 20 searches):\n"
            for h in history:
                response += f"  🔍 {h['query']} ({h['results_count']}件) - {h['executed_at'][:16]}\n"
            return response

        elif action == 'stats':
            stats = self.db.get_stats()
            response = "📊 インデックス統計 / Index Stats:\n"
            response += f"総インデックス数 / Total indexed: {stats['total_indexed']}\n"
            response += f"検索クエリ数 / Total queries: {stats['total_queries']}\n"
            if stats['avg_results']:
                response += f"平均結果数 / Avg results: {stats['avg_results']:.1f}\n"
            if stats['top_query']:
                response += f"トップ検索 / Top query: {stats['top_query']}\n"
            return response

        elif action == 'rebuild':
            count = self.db.rebuild_index()
            response = f"🔄 インデックスを再構築しました / Index rebuilt\n"
            response += f"処理件数: {count}件 / Processed: {count} items\n"
            return response

        return None

    def _format_result(self, result: dict, index: int = 0) -> str:
        """結果をフォーマット"""
        parts = []
        parts.append(f"[{index}] {result['title']}")
        if result.get('artist'):
            parts.append(f"  🎨 {result['artist']}")
        if result.get('tags'):
            parts.append(f"  🏷️ {result['tags']}")
        if result.get('source'):
            parts.append(f"  📍 {result['source']}")
        parts.append(f"  📅 {result['indexed_at'][:10]}")
        return "\n".join(parts)


if __name__ == '__main__':
    agent = EroticSearchAgent()

    test_messages = [
        "検索: キーワード:最高, タグ:おすすめ",
        "追加: id:001, タイトル:素晴らしい作品, アーティスト:名前なし, タグ:最高",
        "統計",
    ]

    for msg in test_messages:
        print(f"\n入力 / Input: {msg}")
        result = agent.handle_message(msg)
        if result:
            print(result)
