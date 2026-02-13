#!/usr/bin/env python3
"""
ユーザー行動分析エージェント Discord連携 / User Behavior Analysis Agent Discord Integration
personalized-behavior-agent
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
from db import PreferenceDB


class PersonalizedBehaviorAgentDiscord:
    """Discordボットインターフェース"""

    def __init__(self):
        self.db = PreferenceDB()

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

    def handle_add_preference(self, user_id: str, args: list) -> dict:
        """嗜好追加コマンド処理"""
        if len(args) < 2:
            return {"error": "Usage: add <category> <item_id> [rating] [tags]"}

        category = args[0]
        item_id = args[1]
        rating = float(args[2]) if len(args) > 2 and args[2].replace('.', '').isdigit() else None
        tags = " ".join(args[3:]) if len(args) > 3 else None

        pref_id = self.db.create_preference(category, item_id, rating, tags)

        # 行動ログ
        self.db.create_behavior_log(user_id, "add_preference", category, item_id)

        return {
            "success": True,
            "message": f"嗜好を追加しました: {category}/{item_id}",
            "preference_id": pref_id
        }

    def handle_list_preferences(self, user_id: str, args: list) -> dict:
        """嗜好一覧コマンド処理"""
        category = args[0] if len(args) > 0 else None

        preferences = self.db.list_preferences(category=category)

        if not preferences:
            return {
                "success": True,
                "message": "嗜好が見つかりませんでした"
            }

        # 整形
        lines = ["**嗜好一覧**"]
        for pref in preferences[:10]:  # 上位10件
            rating_str = f"⭐{pref['rating']}" if pref['rating'] else ""
            lines.append(f"- {pref['category']}/{pref['item_id']} {rating_str} ({pref['interaction_count']}回)")

        return {
            "success": True,
            "message": "\n".join(lines)
        }

    def handle_analyze(self, user_id: str, args: list) -> dict:
        """分析コマンド処理"""
        category = args[0] if len(args) > 0 else None

        preferences = self.db.list_preferences(category=category)

        if not preferences:
            return {
                "success": True,
                "message": "分析対象の嗜好が見つかりませんでした"
            }

        # 簡易分析
        category_counts = {}
        total_rating = 0
        rating_count = 0

        for pref in preferences:
            cat = pref['category']
            category_counts[cat] = category_counts.get(cat, 0) + 1

            if pref['rating']:
                total_rating += pref['rating']
                rating_count += 1

        lines = ["**嗜好分析**"]
        lines.append(f"総アイテム数: {len(preferences)}")
        lines.append(f"総インタラクション: {sum(p['interaction_count'] for p in preferences)}")

        if rating_count > 0:
            lines.append(f"平均評価: {total_rating / rating_count:.2f}")

        lines.append("\n**カテゴリ分布**:")
        for cat, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True):
            lines.append(f"- {cat}: {count}アイテム")

        return {
            "success": True,
            "message": "\n".join(lines)
        }

    def handle_recommend(self, user_id: str, args: list) -> dict:
        """推薦コマンド処理"""
        category = args[0] if len(args) > 0 else None

        # 行動履歴に基づいて推薦
        behavior = self.db.get_user_behavior(user_id, limit=50)

        if not behavior:
            return {
                "success": True,
                "message": "行動履歴が不足しています。まずはいくつかのアイテムに反応してみてください。"
            }

        # 簡易推薦: 頻度の高いカテゴリから提案
        category_freq = {}
        for log in behavior:
            cat = log['category']
            category_freq[cat] = category_freq.get(cat, 0) + 1

        top_category = max(category_freq.items(), key=lambda x: x[1])[0]

        # 推薦アイテムを取得
        if category:
            top_category = category

        preferences = self.db.list_preferences(category=top_category)

        if not preferences:
            return {
                "success": True,
                "message": f"{top_category}カテゴリの推薦アイテムが見つかりませんでした"
            }

        lines = ["**おすすめ**"]
        lines.append(f"カテゴリ: {top_category}")

        for pref in preferences[:5]:
            rating_str = f"⭐{pref['rating']}" if pref['rating'] else ""
            lines.append(f"- {pref['item_id']} {rating_str}")

        # 推薦ログ
        self.db.create_recommendation(
            user_id,
            top_category,
            ",".join([p['item_id'] for p in preferences[:5]]),
            "frequency-based",
            0.8
        )

        return {
            "success": True,
            "message": "\n".join(lines)
        }

    def handle_stats(self, user_id: str, args: list) -> dict:
        """統計コマンド処理"""
        stats = self.db.get_statistics()

        lines = ["**統計情報**"]
        lines.append(f"総嗜好数: {stats['total_preferences']}")
        lines.append(f"総行動ログ: {stats['total_behavior_logs']}")
        lines.append(f"総推薦数: {stats['total_recommendations']}")

        if stats['category_distribution']:
            lines.append("\n**カテゴリ別**:")
            for cat in stats['category_distribution'][:5]:
                lines.append(f"- {cat['category']}: {cat['count']}")

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
            "add": self.handle_add_preference,
            "list": self.handle_list_preferences,
            "analyze": self.handle_analyze,
            "recommend": self.handle_recommend,
            "stats": self.handle_stats
        }

        handler = handlers.get(command)
        if handler:
            return handler(user_id, args)
        else:
            return {
                "error": f"Unknown command: {command}\nAvailable commands: add, list, analyze, recommend, stats"
            }

    def format_response(self, response: dict) -> str:
        """レスポンスを整形"""
        if "error" in response:
            return f"❌ {response['error']}"

        if "message" in response:
            emoji_map = {
                "add": "➕",
                "list": "📋",
                "analyze": "📊",
                "recommend": "🎯",
                "stats": "📈"
            }
            command = response.get("command", "")
            emoji = emoji_map.get(command, "✅")
            return f"{emoji} {response['message']}"

        return "✅ コマンドを実行しました"


if __name__ == "__main__":
    bot = PersonalizedBehaviorAgentDiscord()

    # テスト
    user_id = "test-user"
    print("コマンドテスト:")

    # テスト: add
    result = bot.handle_command(user_id, "!pref add baseball npb-2024 5.0")
    print(f"add: {bot.format_response(result)}")

    # テスト: list
    result = bot.handle_command(user_id, "!pref list")
    print(f"list: {bot.format_response(result)}")

    # テスト: recommend
    result = bot.handle_command(user_id, "!pref recommend")
    print(f"recommend: {bot.format_response(result)}")
