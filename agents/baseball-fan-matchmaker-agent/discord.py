#!/usr/bin/env python3
"""
野球ファンマッチメイキングエージェント Discord連携 / Baseball Fan Matchmaker Agent Discord Integration
baseball-fan-matchmaker-agent
"""

import os
from datetime import datetime
from pathlib import Path

# Discord Bot Token (from environment)
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN", "")

# Database import
import sys
sys.path.insert(0, str(Path(__file__).parent))
from db import BaseballFanEngagementDB


class BaseballFanMatchmakerAgentDiscord:
    """Discord Bot Interface for Fan Engagement"""

    def __init__(self):
        self.db = BaseballFanEngagementDB()

    def parse_command(self, content: str) -> dict:
        """Parse command"""
        parts = content.strip().split()
        if len(parts) < 2:
            return {"error": "Invalid command"}

        command = parts[1].lower()
        args = parts[2:] if len(parts) > 2 else []

        return {
            "command": command,
            "args": args
        }

    def handle_register(self, user_id: str, username: str, args: list) -> dict:
        """Handle registration command"""
        team = args[0] if len(args) > 0 else None
        players = args[1] if len(args) > 1 else None
        location = args[2] if len(args) > 2 else None

        fan_id = self.db.create_fan(user_id, username, team, players, location)

        return {
            "success": True,
            "command": "register",
            "message": f"✅ 登録完了！\nユーザー: {username}\nチーム: {team or '未設定'}\n場所: {location or '未設定'}"
        }

    def handle_match(self, user_id: str, args: list) -> dict:
        """Handle find match command"""
        fan = self.db.get_fan_by_discord_id(user_id)
        if not fan:
            return {
                "success": False,
                "error": "先に !bf register で登録してください"
            }

        limit = int(args[0]) if len(args) > 0 and args[0].isdigit() else 5
        matches = self.db.find_matches(fan['id'], limit=limit, min_score=30.0)

        if not matches:
            return {
                "success": True,
                "command": "match",
                "message": "🔍 一致するファンが見つかりませんでした"
            }

        lines = [f"🎯 おすすめのマッチ ({len(matches)}件):\n"]

        for i, match in enumerate(matches[:10], 1):
            lines.append(
                f"{i}. {match['username']}\n"
                f"   チーム: {match.get('favorite_team', '-')}\n"
                f"   相性: {match['compatibility_score']:.1f}%\n"
            )

        return {
            "success": True,
            "command": "match",
            "message": "\n".join(lines)
        }

    def handle_party(self, user_id: str, args: list) -> dict:
        """Handle watch party commands"""
        fan = self.db.get_fan_by_discord_id(user_id)
        if not fan:
            return {"success": False, "error": "登録が必要です"}

        subcommand = args[0].lower() if len(args) > 0 else "list"

        if subcommand == "create" or subcommand == "new":
            title = " ".join(args[1:])
            party_id = self.db.create_watch_party(
                fan['id'],
                title,
                description=None,
                max_participants=10
            )
            return {
                "success": True,
                "command": "party",
                "message": f"📺 観戦パーティーを作成しました！\nID: {party_id}\nタイトル: {title}"
            }

        elif subcommand == "join":
            if len(args) < 2:
                return {"success": False, "error": "パーティーIDを指定してください"}

            party_id = int(args[1])
            if self.db.join_watch_party(party_id, fan['id']):
                return {
                    "success": True,
                    "command": "party",
                    "message": f"✅ パーティー {party_id} に参加しました！"
                }
            else:
                return {
                    "success": False,
                    "error": "参加に失敗しました（既に参加済み？）"
                }

        elif subcommand == "list":
            parties = self.db.get_watch_parties(status='scheduled', limit=10)
            if not parties:
                return {
                    "success": True,
                    "command": "party",
                    "message": "📺 現在開催中のパーティーはありません"
                }

            lines = ["📺 開催中の観戦パーティー:\n"]
            for party in parties[:10]:
                lines.append(
                    f"ID: {party['id']} - {party['title']}\n"
                    f"  最大参加者: {party['max_participants']}\n"
                )

            return {
                "success": True,
                "command": "party",
                "message": "\n".join(lines)
            }

        else:
            return {"success": False, "error": "サブコマンド: create, join, list"}

    def handle_story(self, user_id: str, args: list) -> dict:
        """Handle story commands"""
        fan = self.db.get_fan_by_discord_id(user_id)
        if not fan:
            return {"success": False, "error": "登録が必要です"}

        subcommand = args[0].lower() if len(args) > 0 else "list"

        if subcommand == "post":
            content = " ".join(args[1:])
            if not content:
                return {"success": False, "error": "内容を入力してください"}

            story_id = self.db.create_fan_story(
                fan['id'],
                None,
                content,
                is_public=True
            )
            return {
                "success": True,
                "command": "story",
                "message": f"📖 ストーリーを投稿しました！\nID: {story_id}"
            }

        elif subcommand == "list":
            limit = int(args[1]) if len(args) > 1 and args[1].isdigit() else 10
            stories = self.db.get_fan_stories(is_public=True, limit=limit)

            if not stories:
                return {
                    "success": True,
                    "command": "story",
                    "message": "📖 ストーリーはまだありません"
                }

            lines = ["📖 ファンストーリー:\n"]
            for story in stories[:10]:
                lines.append(
                    f"{story['username']}:\n"
                    f"  {story['content'][:100]}...\n"
                )

            return {
                "success": True,
                "command": "story",
                "message": "\n".join(lines)
            }

        elif subcommand == "mine":
            limit = int(args[1]) if len(args) > 1 and args[1].isdigit() else 10
            stories = self.db.get_fan_stories(fan_id=fan['id'], limit=limit)

            if not stories:
                return {
                    "success": True,
                    "command": "story",
                    "message": "📖 あなたのストーリーはまだありません"
                }

            lines = [f"📖 あなたのストーリー ({len(stories)}件):\n"]
            for story in stories[:10]:
                lines.append(f"  {story['content'][:80]}...\n")

            return {
                "success": True,
                "command": "story",
                "message": "\n".join(lines)
            }

        else:
            return {"success": False, "error": "サブコマンド: post, list, mine"}

    def handle_challenge(self, user_id: str, args: list) -> dict:
        """Handle challenge commands"""
        fan = self.db.get_fan_by_discord_id(user_id)
        if not fan:
            return {"success": False, "error": "登録が必要です"}

        subcommand = args[0].lower() if len(args) > 0 else "list"

        if subcommand == "list":
            challenges = self.db.get_challenges(is_active=True, limit=10)

            if not challenges:
                return {
                    "success": True,
                    "command": "challenge",
                    "message": "🎮 チャレンジはまだありません"
                }

            lines = ["🎮 チャレンジ一覧:\n"]
            for challenge in challenges[:10]:
                lines.append(
                    f"ID: {challenge['id']} - {challenge['title']}\n"
                    f"  報酬: {challenge['points_reward']} ポイント\n"
                )

            return {
                "success": True,
                "command": "challenge",
                "message": "\n".join(lines)
            }

        elif subcommand == "complete":
            if len(args) < 2:
                return {"success": False, "error": "チャレンジIDを指定してください"}

            challenge_id = int(args[1])
            success, points = self.db.complete_challenge(fan['id'], challenge_id)

            if success:
                return {
                    "success": True,
                    "command": "challenge",
                    "message": f"🎉 チャレンジ完了！\n獲得ポイント: {points}"
                }
            else:
                return {
                    "success": False,
                    "error": "完了に失敗しました（既に完了済み？）"
                }

        elif subcommand == "points":
            fan_points = self.db.get_fan_points(fan['id'])
            if not fan_points:
                return {
                    "success": True,
                    "command": "challenge",
                    "message": "まだポイントがありません"
                }

            return {
                "success": True,
                "command": "challenge",
                "message": f"🏆 あなたのポイント: {fan_points['total_points']}\nランク: {fan_points.get('current_rank', '-')}"
            }

        elif subcommand == "leaderboard":
            limit = int(args[1]) if len(args) > 1 and args[1].isdigit() else 10
            leaderboard = self.db.get_leaderboard(limit=limit)

            if not leaderboard:
                return {
                    "success": True,
                    "command": "challenge",
                    "message": "リーダーボードはまだありません"
                }

            lines = ["🏆 ポイントリーダーボード:\n"]
            for i, entry in enumerate(leaderboard[:10], 1):
                lines.append(f"{i}. {entry['username']} - {entry['total_points']} ポイント\n")

            return {
                "success": True,
                "command": "challenge",
                "message": "\n".join(lines)
            }

        else:
            return {"success": False, "error": "サブコマンド: list, complete, points, leaderboard"}

    def handle_analytics(self, user_id: str, args: list) -> dict:
        """Handle analytics commands"""
        subcommand = args[0].lower() if len(args) > 0 else "summary"

        if subcommand == "summary":
            fan = self.db.get_fan_by_discord_id(user_id)
            if not fan:
                return {"success": False, "error": "登録が必要です"}

            fan_points = self.db.get_fan_points(fan['id'])
            event_stats = self.db.get_event_stats(event_type=None, days=30)

            lines = [f"📊 アクティビティサマリー\n"]
            lines.append(f"ユーザー: {fan['username']}\n")
            lines.append(f"チーム: {fan.get('favorite_team', '未設定')}\n")
            lines.append(f"ポイント: {fan_points['total_points'] if fan_points else 0}\n")
            lines.append(f"総イベント数: {event_stats['count']}\n")

            return {
                "success": True,
                "command": "analytics",
                "message": "\n".join(lines)
            }

        elif subcommand == "leaderboard":
            limit = int(args[1]) if len(args) > 1 and args[1].isdigit() else 10
            leaderboard = self.db.get_leaderboard(limit=limit)

            if not leaderboard:
                return {
                    "success": True,
                    "command": "analytics",
                    "message": "リーダーボードはまだありません"
                }

            lines = ["📊 アクティビティリーダーボード:\n"]
            for i, entry in enumerate(leaderboard[:10], 1):
                lines.append(f"{i}. {entry['username']} - {entry['total_points']} ポイント\n")

            return {
                "success": True,
                "command": "analytics",
                "message": "\n".join(lines)
            }

        else:
            return {"success": False, "error": "サブコマンド: summary, leaderboard"}

    def handle_feedback(self, user_id: str, args: list) -> dict:
        """Handle feedback command"""
        fan = self.db.get_fan_by_discord_id(user_id)

        if not args:
            return {
                "success": False,
                "error": "Usage: !bf feedback <feedback_type> <comments>"
            }

        feedback_type = args[0]
        comments = " ".join(args[1:]) if len(args) > 1 else None

        fan_id = fan['id'] if fan else None
        self.db.submit_feedback(fan_id, feedback_type, None, comments)

        return {
            "success": True,
            "command": "feedback",
            "message": f"📝 フィードバックありがとうございます！\nタイプ: {feedback_type}"
        }

    def handle_help(self, user_id: str, args: list) -> dict:
        """Handle help command"""
        help_text = """
🎮 野球ファンエンゲージメント Bot コマンド一覧

👤 **ユーザー管理**
- `!bf register <team> [players] [location]` - ユーザー登録
- `!bf profile` - プロフィール確認

🤝 **マッチング**
- `!bf match [limit]` - おすすめファンを検索

📺 **観戦パーティー**
- `!bf party create <title>` - パーティー作成
- `!bf party join <party_id>` - パーティー参加
- `!bf party list` - パーティー一覧

📖 **ファンストーリー**
- `!bf story post <content>` - ストーリー投稿
- `!bf story list [limit]` - ストーリー一覧
- `!bf story mine` - 自分のストーリー

🎮 **チャレンジ**
- `!bf challenge list` - チャレンジ一覧
- `!bf challenge complete <id>` - チャレンジ完了
- `!bf challenge points` - ポイント確認
- `!bf challenge leaderboard` - リーダーボード

📊 **分析**
- `!bf analytics summary` - アクティビティサマリー
- `!bf analytics leaderboard` - リーダーボード

📝 **フィードバック**
- `!bf feedback <type> <comments>` - フィードバック送信

❓ `!bf help` - このヘルプを表示
"""

        return {
            "success": True,
            "command": "help",
            "message": help_text.strip()
        }

    def handle_command(self, user_id: str, username: str, content: str) -> dict:
        """Handle incoming command"""
        parsed = self.parse_command(content)

        if "error" in parsed:
            return {"error": "Invalid command format"}

        command = parsed["command"]
        args = parsed["args"]

        # Command router
        handlers = {
            "register": self.handle_register,
            "match": self.handle_match,
            "party": self.handle_party,
            "story": self.handle_story,
            "challenge": self.handle_challenge,
            "analytics": self.handle_analytics,
            "feedback": self.handle_feedback,
            "help": self.handle_help
        }

        handler = handlers.get(command)
        if handler:
            return handler(user_id, username, args)
        else:
            return {
                "error": f"Unknown command: {command}\nUse !bf help for available commands"
            }

    def format_response(self, response: dict) -> str:
        """Format response for Discord"""
        if "error" in response:
            return f"❌ {response['error']}"

        if "message" in response:
            emoji_map = {
                "register": "👤",
                "match": "🎯",
                "party": "📺",
                "story": "📖",
                "challenge": "🎮",
                "analytics": "📊",
                "feedback": "📝",
                "help": "❓"
            }
            command = response.get("command", "")
            emoji = emoji_map.get(command, "✅")
            return f"{emoji} {response['message']}"

        return "✅ コマンドを実行しました"


if __name__ == "__main__":
    bot = BaseballFanMatchmakerAgentDiscord()

    # Test commands
    user_id = "test-user-123"
    username = "TestFan"

    print("=== コマンドテスト ===\n")

    # Test: help
    result = bot.handle_command(user_id, username, "!bf help")
    print(f"help:\n{bot.format_response(result)}\n")

    # Test: register
    result = bot.handle_command(user_id, username, "!bf register Giants Ohtani Tokyo")
    print(f"register:\n{bot.format_response(result)}\n")

    # Test: match
    result = bot.handle_command(user_id, username, "!bf match 3")
    print(f"match:\n{bot.format_response(result)}\n")

    # Test: challenge list
    result = bot.handle_command(user_id, username, "!bf challenge list")
    print(f"challenge list:\n{bot.format_response(result)}\n")
