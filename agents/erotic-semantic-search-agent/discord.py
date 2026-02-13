#!/usr/bin/env python3
"""
えっちコンテンツ意味検索エージェント Discord連携 / Erotic Content Semantic Search Agent Discord Integration
erotic-semantic-search-agent
"""

import json
from datetime import datetime
from pathlib import Path

# Discord Bot Token（環境変数から取得）
import os
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN", "")

# データベースインポート
import sys
sys.path.insert(0, str(Path(__file__).parent))
from db import EroticAdvancedDB


class EroticSemanticSearchAgentDiscord:
    """Discordボットインターフェース"""

    def __init__(self):
        self.db = EroticAdvancedDB()

    def parse_command(self, content: str) -> dict:
        """コマンドをパース"""
        parts = content.strip().split()
        if len(parts) < 2:
            return {"error": "Invalid command"}

        command = parts[1].lower()
        args = parts[2:] if len(parts) > 2 else []

        return {
            "command": command,
            "args": args
        }

    def handle_search(self, user_id: str, args: list) -> dict:
        """検索コマンド処理"""
        if len(args) < 1:
            return {"error": "Usage: search <query>"}

        query = " ".join(args)
        contents = self.db.list_contents(tag=query, limit=10)

        # 検索ログ
        self.db.create_search_log(query, len(contents))

        if not contents:
            return {
                "success": True,
                "message": f"検索結果が見つかりませんでした: {query}"
            }

        lines = [f"**検索結果: {query}** ({len(contents)}件)"]

        for content in contents[:5]:
            lines.append(f"- {content['title']} ({content['artist']})")
            lines.append(f"  タグ: {content['tags'][:50]}..." if len(content['tags']) > 50 else f"  タグ: {content['tags']}")

        return {
            "success": True,
            "message": "\n".join(lines)
        }

    def handle_content(self, user_id: str, args: list) -> dict:
        """コンテンツ詳細コマンド処理"""
        if len(args) < 1:
            return {"error": "Usage: content <content_id>"}

        content_id = args[0]
        content = self.db.get_content(content_id)

        if not content:
            return {
                "success": True,
                "message": f"コンテンツが見つかりませんでした: {content_id}"
            }

        lines = ["**コンテンツ詳細**"]
        lines.append(f"タイトル: {content['title']}")
        lines.append(f"アーティスト: {content['artist']}")
        lines.append(f"ソース: {content['source']}")
        lines.append(f"タグ: {content['tags']}")
        if content['description']:
            lines.append(f"説明: {content['description']}")

        return {
            "success": True,
            "message": "\n".join(lines)
        }

    def handle_tags(self, user_id: str, args: list) -> dict:
        """タグ一覧コマンド処理"""
        category = args[0] if len(args) > 0 else None
        tags = self.db.list_tags(category=category, limit=30)

        if not tags:
            return {
                "success": True,
                "message": "タグが見つかりませんでした"
            }

        lines = ["**タグ一覧**"]

        for tag in tags[:20]:
            lines.append(f"- {tag['tag_name']} ({tag['count']}回)")

        return {
            "success": True,
            "message": "\n".join(lines)
        }

    def handle_collection(self, user_id: str, args: list) -> dict:
        """コレクションコマンド処理"""
        if len(args) < 1:
            # コレクション一覧
            collections = self.db.list_collections(limit=10)

            if not collections:
                return {
                    "success": True,
                    "message": "コレクションが見つかりませんでした"
                }

            lines = ["**コレクション一覧**"]

            for collection in collections:
                lines.append(f"- {collection['collection_name']}: {collection['description'][:50]}...")

            return {
                "success": True,
                "message": "\n".join(lines)
            }

        # コレクション詳細
        collection_id = int(args[0]) if args[0].isdigit() else None
        if collection_id:
            contents = self.db.get_collection_contents(collection_id)

            if not contents:
                return {
                    "success": True,
                    "message": f"コレクションID {collection_id} にコンテンツが見つかりませんでした"
                }

            lines = [f"**コレクション内容 ({len(contents)}件)**"]

            for content in contents[:10]:
                lines.append(f"- {content['title']} ({content['artist']})")

            return {
                "success": True,
                "message": "\n".join(lines)
            }

        return {"error": "Invalid collection_id"}

    def handle_stats(self, user_id: str, args: list) -> dict:
        """統計コマンド処理"""
        stats = self.db.get_statistics()

        lines = ["**統計情報**"]
        lines.append(f"総コンテンツ数: {stats['total_contents']}")
        lines.append(f"総タグ数: {stats['total_tags']}")
        lines.append(f"総コレクション数: {stats['total_collections']}")
        lines.append(f"総検索数: {stats['total_searches']}")

        if stats['top_artists']:
            lines.append("\n**トップアーティスト**:")
            for artist in stats['top_artists'][:5]:
                lines.append(f"- {artist['artist']}: {artist['count']}作品")

        return {
            "success": True,
            "message": "\n".join(lines)
        }

    def handle_command(self, user_id: str, content: str) -> dict:
        """コマンドを処理"""
        parsed = self.parse_command(content)

        if "error" in parsed:
            return {"error": "Invalid command format"}

        command = parsed["command"]
        args = parsed["args"]

        # コマンドルーター
        handlers = {
            "search": self.handle_search,
            "content": self.handle_content,
            "tags": self.handle_tags,
            "collection": self.handle_collection,
            "stats": self.handle_stats
        }

        handler = handlers.get(command)
        if handler:
            return handler(user_id, args)
        else:
            return {
                "error": f"Unknown command: {command}\nAvailable commands: search, content, tags, collection, stats"
            }

    def format_response(self, response: dict) -> str:
        """レスポンスを整形"""
        if "error" in response:
            return f"❌ {response['error']}"

        if "message" in response:
            emoji_map = {
                "search": "🔍",
                "content": "📄",
                "tags": "🏷️",
                "collection": "📚",
                "stats": "📊"
            }
            command = response.get("command", "")
            emoji = emoji_map.get(command, "✅")
            return f"{emoji} {response['message']}"

        return "✅ コマンドを実行しました"


if __name__ == "__main__":
    bot = EroticSemanticSearchAgentDiscord()

    # テスト
    user_id = "test-user"
    print("コマンドテスト:")

    # テスト: search
    result = bot.handle_command(user_id, "!erotic search アニメ")
    print(f"search: {bot.format_response(result)}")

    # テスト: stats
    result = bot.handle_command(user_id, "!erotic stats")
    print(f"stats: {bot.format_response(result)}")
