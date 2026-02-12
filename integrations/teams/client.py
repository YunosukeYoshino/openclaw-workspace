#!/usr/bin/env python3
"""
Microsoft Teams Integration
Microsoft Teams APIを統合して、通知・メッセージ送信を行う

Usage:
    from integrations.teams import TeamsClient

    client = TeamsClient(webhook_url="https://...")
    client.send_message(text="Hello, Teams!")
"""

import os
import json
import logging
from typing import List, Dict, Optional, Any
from dataclasses import dataclass

# Teams APIクライアントが利用可能かチェック
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class TeamsMessage:
    """Teamsメッセージデータクラス"""
    text: str
    title: Optional[str] = None
    color: Optional[str] = None
    summary: Optional[str] = None


class TeamsClient:
    """
    Microsoft Teams APIクライアント (Incoming Webhookベース)

    環境変数:
        TEAMS_WEBHOOK_URL: Teams Incoming Webhook URL
    """

    def __init__(self, webhook_url: Optional[str] = None):
        if not REQUESTS_AVAILABLE:
            logger.warning("requestsライブラリがインストールされていません")
            logger.warning("インストール: pip install requests")
            raise ImportError("requestsライブラリがインストールされていません")

        self.webhook_url = webhook_url or os.getenv('TEAMS_WEBHOOK_URL')

        if not self.webhook_url:
            raise ValueError(
                "Teams Webhook URLが必要です。\n"
                "環境変数 TEAMS_WEBHOOK_URL またはコンストラクタで設定してください。\n"
                "TeamsチャンネルでIncoming Webhookコネクタを設定してURLを取得してください。"
            )

        logger.info("Teams APIクライアント初期化完了")

    def send_message(
        self,
        text: str,
        title: Optional[str] = None,
        summary: Optional[str] = None,
        color: Optional[str] = None,
        sections: Optional[List[Dict]] = None,
        facts: Optional[List[Dict]] = None
    ) -> bool:
        """
        メッセージを送信

        Args:
            text: メッセージテキスト
            title: タイトル
            summary: 概要
            color: メッセージの色（例: "0078D4", "FF0000"）
            sections: セクションリスト
            facts: 事実リスト（キー: バリュー）

        Returns:
            成功したらTrue
        """
        payload = {
            "@type": "MessageCard",
            "@context": "https://schema.org/extensions",
            "text": text
        }

        if title:
            payload["title"] = title
        if summary:
            payload["summary"] = summary
        if color:
            payload["themeColor"] = color

        if sections or facts:
            if sections is None:
                sections = []

            if facts:
                sections.append({
                    "type": "TextBlock",
                    "text": "",
                    "facts": facts
                })

            payload["sections"] = sections

        response = requests.post(self.webhook_url, json=payload)

        if response.status_code == 200:
            logger.info("メッセージを送信しました")
            return True
        else:
            logger.error(f"メッセージ送信に失敗: {response.status_code}")
            return False

    def send_card(
        self,
        title: str,
        text: str,
        facts: Optional[List[Dict]] = None,
        color: str = "0078D4"
    ) -> bool:
        """
        カード形式でメッセージを送信

        Args:
            title: タイトル
            text: 本文
            facts: 事実リスト（例: [{"name": "Status", "value": "Complete"}]）
            color: テーマカラー

        Returns:
            成功したらTrue
        """
        return self.send_message(
            text=text,
            title=title,
            facts=facts,
            color=color
        )

    def send_notification(
        self,
        title: str,
        message: str,
        level: str = "info"
    ) -> bool:
        """
        通知メッセージを送信

        Args:
            title: タイトル
            message: メッセージ
            level: 通知レベル（info, warning, error, success）

        Returns:
            成功したらTrue
        """
        colors = {
            "info": "0078D4",
            "warning": "FF8C00",
            "error": "FF0000",
            "success": "00FF00"
        }

        return self.send_card(
            title=title,
            text=message,
            color=colors.get(level, "0078D4")
        )

    def send_progress(
        self,
        title: str,
        progress: float,
        status: str
    ) -> bool:
        """
        進捗メッセージを送信

        Args:
            title: タイトル
            progress: 進捗率（0.0〜1.0）
            status: ステータステキスト

        Returns:
            成功したらTrue
        """
        facts = [
            {"name": "Progress", "value": f"{progress * 100:.1f}%"},
            {"name": "Status", "value": status}
        ]

        return self.send_card(
            title=title,
            text=f"Progress update",
            facts=facts
        )

    def send_error(
        self,
        title: str,
        error_message: str,
        context: Optional[Dict] = None
    ) -> bool:
        """
        エラーメッセージを送信

        Args:
            title: エラータイトル
            error_message: エラーメッセージ
            context: 追加コンテキスト

        Returns:
            成功したらTrue
        """
        facts = [
            {"name": "Error", "value": error_message}
        ]

        if context:
            for key, value in context.items():
                facts.append({"name": key, "value": str(value)})

        return self.send_card(
            title=title,
            text="An error occurred",
            facts=facts,
            color="FF0000"
        )


# CLIツールとして使用する場合
def main():
    import argparse

    parser = argparse.ArgumentParser(description="Microsoft Teams Client")
    parser.add_argument('--send', type=str, help='メッセージを送信')
    parser.add_argument('--title', type=str, help='タイトル')
    parser.add_argument('--notify', type=str, nargs=2, metavar=('TITLE', 'MESSAGE'), help='通知を送信')
    parser.add_argument('--level', type=str, default='info', choices=['info', 'warning', 'error', 'success'], help='通知レベル')

    args = parser.parse_args()

    try:
        client = TeamsClient()

        if args.send:
            client.send_message(
                text=args.send,
                title=args.title
            )
            print(f"✅ メッセージを送信しました")

        elif args.notify:
            title, message = args.notify
            client.send_notification(
                title=title,
                message=message,
                level=args.level
            )
            print(f"✅ 通知を送信しました")

        else:
            print("オプションを指定してください。--help でヘルプを表示します。")

    except Exception as e:
        logger.error(f"エラー: {e}")
        print(f"❌ エラー: {e}")


if __name__ == "__main__":
    main()
