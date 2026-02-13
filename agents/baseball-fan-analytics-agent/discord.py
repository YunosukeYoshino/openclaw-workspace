#!/usr/bin/env python3
"""
野球ファン分析エージェント Discord連携 / Baseball Fan Analytics Agent Discord Integration
"""

import os
from pathlib import Path

# Discord Bot Token
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN", "")

# Database import
import sys
sys.path.insert(0, str(Path(__file__).parent))
from db import BaseballFanEngagementDB


class BaseballFanAnalyticsAgentDiscord:
    """Discord Bot Interface for Fan Engagement"""

    def __init__(self):
        self.db = BaseballFanEngagementDB()

    def parse_command(self, content: str) -> dict:
        """Parse command"""
        parts = content.strip().split()
        if len(parts) < 2:
            return dict(error="Invalid command")

        command = parts[1].lower()
        args = parts[2:] if len(parts) > 2 else []

        return dict(
            command=command,
            args=args
        )

    def handle_register(self, user_id: str, username: str, args: list) -> dict:
        """Handle registration command"""
        team = args[0] if len(args) > 0 else None
        location = args[1] if len(args) > 1 else None

        fan_id = self.db.create_fan(user_id, username, team, location)

        return dict(
            success=True,
            command="register",
            message=f"✅ 登録完了！\nユーザー: {username}\nチーム: {team or '未設定'}\n場所: {location or '未設定'}"
        )

    def handle_help(self, user_id: str, args: list) -> dict:
        """Handle help command"""
        help_text = """
🎮 野球ファンエンゲージメント Bot コマンド一覧

👤 **ユーザー管理**
- `!bf register <team> [location]` - ユーザー登録

📺 **観戦パーティー**
- `!bf party create <title>` - パーティー作成
- `!bf party join <party_id>` - パーティー参加
- `!bf party list` - パーティー一覧

📖 **ファンストーリー**
- `!bf story post <content>` - ストーリー投稿
- `!bf story list` - ストーリー一覧

🎮 **チャレンジ**
- `!bf challenge list` - チャレンジ一覧
- `!bf challenge complete <id>` - チャレンジ完了
- `!bf challenge points` - ポイント確認
- `!bf challenge leaderboard` - リーダーボード

📊 **分析**
- `!bf analytics summary` - アクティビティサマリー

❓ `!bf help` - このヘルプを表示
"""

        return dict(
            success=True,
            command="help",
            message=help_text.strip()
        )

    def handle_command(self, user_id: str, username: str, content: str) -> dict:
        """Handle incoming command"""
        parsed = self.parse_command(content)

        if "error" in parsed:
            return dict(error="Invalid command format")

        command = parsed["command"]
        args = parsed["args"]

        # Command router
        handlers = dict(
            register=self.handle_register,
            help=self.handle_help
        )

        handler = handlers.get(command)
        if handler:
            return handler(user_id, username, args)
        else:
            return dict(
                error=f"Unknown command: {command}\nUse !bf help for available commands"
            )

    def format_response(self, response: dict) -> str:
        """Format response for Discord"""
        if "error" in response:
            return f"❌ {response['error']}"

        if "message" in response:
            emoji_map = dict(
                register="👤",
                match="🎯",
                party="📺",
                story="📖",
                challenge="🎮",
                analytics="📊",
                help="❓"
            )
            command = response.get("command", "")
            emoji = emoji_map.get(command, "✅")
            return f"{emoji} {response['message']}"

        return "✅ コマンドを実行しました"


if __name__ == "__main__":
    bot = BaseballFanAnalyticsAgentDiscord()

    # Test commands
    user_id = "test-user-123"
    username = "TestFan"

    print("=== コマンドテスト ===\n")

    result = bot.handle_command(user_id, username, "!bf help")
    print(f"help:\n{bot.format_response(result)}\n")

    result = bot.handle_command(user_id, username, "!bf register Giants Tokyo")
    print(f"register:\n{bot.format_response(result)}\n")
