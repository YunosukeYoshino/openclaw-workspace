#!/usr/bin/env python3
"""
Slack Integration
Slack APIを統合して、通知・メッセージ送信を行う

Usage:
    from integrations.slack import SlackClient

    client = SlackClient(bot_token="xoxb-...")
    client.send_message(channel="#general", text="Hello, Slack!")
"""

import os
import json
import logging
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
from datetime import datetime

# Slack APIクライアントが利用可能かチェック
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class SlackMessage:
    """Slackメッセージデータクラス"""
    channel: str
    text: str
    timestamp: Optional[str] = None
    user: Optional[str] = None
    thread_ts: Optional[str] = None


@dataclass
class SlackChannel:
    """Slackチャンネルデータクラス"""
    id: str
    name: str
    is_channel: bool = True
    is_private: bool = False


class SlackClient:
    """
    Slack APIクライアント

    環境変数:
        SLACK_BOT_TOKEN: Slack Bot Token (xoxb-...)
        SLACK_SIGNING_SECRET: Slack Signing Secret（Webhook用）
    """

    API_BASE_URL = "https://slack.com/api"

    def __init__(
        self,
        bot_token: Optional[str] = None,
        signing_secret: Optional[str] = None
    ):
        if not REQUESTS_AVAILABLE:
            logger.warning("requestsライブラリがインストールされていません")
            logger.warning("インストール: pip install requests")
            raise ImportError("requestsライブラリがインストールされていません")

        self.bot_token = bot_token or os.getenv('SLACK_BOT_TOKEN')
        self.signing_secret = signing_secret or os.getenv('SLACK_SIGNING_SECRET')

        if not self.bot_token:
            raise ValueError(
                "Slack Bot Tokenが必要です。\n"
                "環境変数 SLACK_BOT_TOKEN またはコンストラクタで設定してください。\n"
                "https://api.slack.com/apps でBot Tokenを取得できます。"
            )

        self.headers = {
            'Authorization': f'Bearer {self.bot_token}',
            'Content-Type': 'application/json'
        }

        logger.info("Slack APIクライアント初期化完了")

    def _request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Slack APIにリクエストを送信

        Args:
            method: HTTPメソッド
            endpoint: APIエンドポイント
            data: リクエストボディ

        Returns:
            レスポンスJSON
        """
        url = f"{self.API_BASE_URL}{endpoint}"
        response = requests.request(
            method,
            url,
            headers=self.headers,
            json=data
        )

        result = response.json()

        if not result.get('ok'):
            error = result.get('error', 'Unknown error')
            raise RuntimeError(f"Slack API Error: {error}")

        return result

    def send_message(
        self,
        channel: str,
        text: str,
        blocks: Optional[List[Dict]] = None,
        attachments: Optional[List[Dict]] = None,
        thread_ts: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        メッセージを送信

        Args:
            channel: チャンネルIDまたは名前（例: "#general"）
            text: メッセージテキスト
            blocks: Block Kit blocks
            attachments: Attachments
            thread_ts: スレッドのタイムスタンプ（スレッド返信用）

        Returns:
            送信結果
        """
        data = {
            'channel': channel,
            'text': text
        }

        if blocks:
            data['blocks'] = blocks
        if attachments:
            data['attachments'] = attachments
        if thread_ts:
            data['thread_ts'] = thread_ts

        result = self._request('POST', '/chat.postMessage', data)
        logger.info(f"メッセージを送信: {channel}")
        return result

    def update_message(
        self,
        channel: str,
        timestamp: str,
        text: Optional[str] = None,
        blocks: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """
        メッセージを更新

        Args:
            channel: チャンネルID
            timestamp: メッセージのタイムスタンプ
            text: 新しいテキスト
            blocks: 新しいBlock Kit blocks

        Returns:
            更新結果
        """
        data = {
            'channel': channel,
            'ts': timestamp
        }

        if text:
            data['text'] = text
        if blocks:
            data['blocks'] = blocks

        result = self._request('POST', '/chat.update', data)
        logger.info(f"メッセージを更新: {timestamp}")
        return result

    def delete_message(self, channel: str, timestamp: str) -> bool:
        """
        メッセージを削除

        Args:
            channel: チャンネルID
            timestamp: メッセージのタイムスタンプ

        Returns:
            成功したらTrue
        """
        self._request('POST', '/chat.delete', {
            'channel': channel,
            'ts': timestamp
        })
        logger.info(f"メッセージを削除: {timestamp}")
        return True

    def list_channels(self) -> List[Dict[str, Any]]:
        """
        パブリックチャンネル一覧を取得

        Returns:
            チャンネルリスト
        """
        result = self._request('GET', '/conversations.list', {
            'types': 'public_channel,private_channel'
        })
        channels = result.get('channels', [])
        logger.info(f"チャンネルを{len(channels)}件取得しました")
        return channels

    def get_channel_info(self, channel_id: str) -> Dict[str, Any]:
        """
        チャンネル情報を取得

        Args:
            channel_id: チャンネルID

        Returns:
            チャンネル情報
        """
        result = self._request('GET', '/conversations.info', {
            'channel': channel_id
        })
        return result

    def get_users(self) -> List[Dict[str, Any]]:
        """
        ユーザー一覧を取得

        Returns:
            ユーザーリスト
        """
        result = self._request('GET', '/users.list')
        users = result.get('members', [])
        logger.info(f"ユーザーを{len(users)}件取得しました")
        return users

    def get_user_info(self, user_id: str) -> Dict[str, Any]:
        """
        ユーザー情報を取得

        Args:
            user_id: ユーザーID

        Returns:
            ユーザー情報
        """
        result = self._request('GET', '/users.info', {'user': user_id})
        return result

    def post_ephemeral(
        self,
        channel: str,
        user: str,
        text: str,
        blocks: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """
        エフェメラルメッセージを送信（特定のユーザーにのみ表示）

        Args:
            channel: チャンネルID
            user: ユーザーID
            text: メッセージテキスト
            blocks: Block Kit blocks

        Returns:
            送信結果
        """
        data = {
            'channel': channel,
            'user': user,
            'text': text
        }

        if blocks:
            data['blocks'] = blocks

        result = self._request('POST', '/chat.postEphemeral', data)
        logger.info(f"エフェメラルメッセージを送信: {user}")
        return result

    def add_reaction(self, channel: str, timestamp: str, reaction: str) -> bool:
        """
        リアクションを追加

        Args:
            channel: チャンネルID
            timestamp: メッセージのタイムスタンプ
            reaction: リアクション名（例: "thumbs_up"）

        Returns:
            成功したらTrue
        """
        self._request('POST', '/reactions.add', {
            'channel': channel,
            'timestamp': timestamp,
            'name': reaction
        })
        logger.info(f"リアクションを追加: {reaction}")
        return True

    def get_history(
        self,
        channel: str,
        limit: int = 100,
        latest: Optional[str] = None,
        oldest: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        チャンネル履歴を取得

        Args:
            channel: チャンネルID
            limit: 取得件数
            latest: 最新のメッセージタイムスタンプ
            oldest: 最古のメッセージタイムスタンプ

        Returns:
            履歴データ
        """
        data = {
            'channel': channel,
            'limit': limit
        }

        if latest:
            data['latest'] = latest
        if oldest:
            data['oldest'] = oldest

        result = self._request('GET', '/conversations.history', data)
        logger.info(f"履歴を取得: {len(result.get('messages', []))}件")
        return result


# CLIツールとして使用する場合
def main():
    import argparse

    parser = argparse.ArgumentParser(description="Slack API Client")
    parser.add_argument('--send', type=str, help='メッセージを送信')
    parser.add_argument('--channel', type=str, help='チャンネル')
    parser.add_argument('--list-channels', action='store_true', help='チャンネル一覧を表示')
    parser.add_argument('--list-users', action='store_true', help='ユーザー一覧を表示')

    args = parser.parse_args()

    try:
        client = SlackClient()

        if args.send:
            if not args.channel:
                print("エラー: --channel が必要です")
                return

            client.send_message(
                channel=args.channel,
                text=args.send
            )
            print(f"✅ メッセージを送信しました: {args.channel}")

        elif args.list_channels:
            channels = client.list_channels()
            print(f"\n📢 チャンネル一覧 ({len(channels)}件):")
            for channel in channels:
                channel_type = "🔒" if channel.get('is_private') else "#"
                print(f"  {channel_type} {channel.get('name', 'Unknown')} ({channel.get('id')})")

        elif args.list_users:
            users = client.get_users()
            print(f"\n👥 ユーザー一覧 ({len(users)}件):")
            for user in users:
                name = user.get('profile', {}).get('real_name', user.get('name', 'Unknown'))
                print(f"  - {name} ({user.get('id')})")

        else:
            print("オプションを指定してください。--help でヘルプを表示します。")

    except Exception as e:
        logger.error(f"エラー: {e}")
        print(f"❌ エラー: {e}")


if __name__ == "__main__":
    main()
