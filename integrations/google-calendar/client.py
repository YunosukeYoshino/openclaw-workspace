#!/usr/bin/env python3
"""
Google Calendar API Client
Google Calendar APIを統合して、カレンダーイベントの同期・管理を行う

Usage:
    from integrations.google_calendar import GoogleCalendarClient

    client = GoogleCalendarClient(credentials_path="credentials.json")
    events = client.list_events()
    client.create_event(summary="Meeting", start="2026-02-12T10:00:00Z", end="2026-02-12T11:00:00Z")
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from dataclasses import dataclass

# Google APIクライアントが利用可能かチェック
try:
    from googleapiclient.discovery import build
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    GOOGLE_API_AVAILABLE = True
except ImportError:
    GOOGLE_API_AVAILABLE = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class CalendarEvent:
    """カレンダーイベントデータクラス"""
    id: str
    summary: str
    description: Optional[str] = None
    start: Optional[datetime] = None
    end: Optional[datetime] = None
    location: Optional[str] = None
    attendees: List[str] = None

    def __post_init__(self):
        if self.attendees is None:
            self.attendees = []


class GoogleCalendarClient:
    """
    Google Calendar APIクライアント

    環境変数:
        GOOGLE_CALENDAR_CREDENTIALS_PATH: 認証情報ファイルのパス
        GOOGLE_CALENDAR_TOKEN_PATH: トークンファイルのパス
        GOOGLE_CALENDAR_ID: カレンダーID（デフォルトは'primary'）
    """

    # 必要なスコープ
    SCOPES = ['https://www.googleapis.com/auth/calendar']

    def __init__(
        self,
        credentials_path: Optional[str] = None,
        token_path: Optional[str] = None,
        calendar_id: Optional[str] = None
    ):
        if not GOOGLE_API_AVAILABLE:
            logger.warning("Google APIクライアントライブラリがインストールされていません")
            logger.warning("インストール: pip install google-api-python-client google-auth-oauthlib")
            raise ImportError("Google APIライブラリがインストールされていません")

        self.credentials_path = credentials_path or os.getenv(
            'GOOGLE_CALENDAR_CREDENTIALS_PATH',
            'credentials.json'
        )
        self.token_path = token_path or os.getenv(
            'GOOGLE_CALENDAR_TOKEN_PATH',
            'token.json'
        )
        self.calendar_id = calendar_id or os.getenv('GOOGLE_CALENDAR_ID', 'primary')

        self.service = None
        self._authenticate()

    def _authenticate(self):
        """Google APIの認証を行う"""
        creds = None

        # 保存されたトークンがあれば読み込む
        if os.path.exists(self.token_path):
            creds = Credentials.from_authorized_user_file(self.token_path, self.SCOPES)

        # トークンが無効または存在しない場合、認証フローを実行
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(self.credentials_path):
                    raise FileNotFoundError(
                        f"認証情報ファイルが見つかりません: {self.credentials_path}\n"
                        "Google Cloud ConsoleでOAuth2認証情報をダウンロードしてください"
                    )
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, self.SCOPES
                )
                creds = flow.run_local_server(port=0)

            # トークンを保存
            with open(self.token_path, 'w') as token:
                token.write(creds.to_json())

        # サービスオブジェクトを作成
        self.service = build('calendar', 'v3', credentials=creds)
        logger.info("Google Calendar API認証完了")

    def list_events(
        self,
        max_results: int = 100,
        time_min: Optional[datetime] = None,
        time_max: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """
        カレンダーイベントを取得

        Args:
            max_results: 取得する最大件数
            time_min: 取得開始日時
            time_max: 取取終了日時

        Returns:
            イベントリスト
        """
        if not self.service:
            raise RuntimeError("認証されていません")

        params = {
            'calendarId': self.calendar_id,
            'maxResults': max_results,
            'singleEvents': True,
            'orderBy': 'startTime'
        }

        if time_min:
            params['timeMin'] = time_min.isoformat() + 'Z'
        else:
            # デフォルトは現在時刻から
            params['timeMin'] = datetime.utcnow().isoformat() + 'Z'

        if time_max:
            params['timeMax'] = time_max.isoformat() + 'Z'

        events_result = self.service.events().list(**params).execute()
        events = events_result.get('items', [])

        logger.info(f"イベントを{len(events)}件取得しました")
        return events

    def get_event(self, event_id: str) -> Dict[str, Any]:
        """
        特定のイベントを取得

        Args:
            event_id: イベントID

        Returns:
            イベント情報
        """
        if not self.service:
            raise RuntimeError("認証されていません")

        event = self.service.events().get(
            calendarId=self.calendar_id,
            eventId=event_id
        ).execute()

        logger.info(f"イベントを取得: {event.get('summary', 'No title')}")
        return event

    def create_event(
        self,
        summary: str,
        start: str,
        end: str,
        description: Optional[str] = None,
        location: Optional[str] = None,
        attendees: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        新しいイベントを作成

        Args:
            summary: イベントタイトル
            start: 開始日時 (ISO 8601形式: "2026-02-12T10:00:00Z")
            end: 終了日時 (ISO 8601形式: "2026-02-12T11:00:00Z")
            description: 説明
            location: 場所
            attendees: 参加者のメールアドレスリスト

        Returns:
            作成されたイベント情報
        """
        if not self.service:
            raise RuntimeError("認証されていません")

        event_body = {
            'summary': summary,
            'start': {'dateTime': start},
            'end': {'dateTime': end}
        }

        if description:
            event_body['description'] = description
        if location:
            event_body['location'] = location
        if attendees:
            event_body['attendees'] = [{'email': email} for email in attendees]

        event = self.service.events().insert(
            calendarId=self.calendar_id,
            body=event_body
        ).execute()

        logger.info(f"イベントを作成: {summary}")
        return event

    def update_event(
        self,
        event_id: str,
        summary: Optional[str] = None,
        description: Optional[str] = None,
        location: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        イベントを更新

        Args:
            event_id: イベントID
            summary: 新しいタイトル
            description: 新しい説明
            location: 新しい場所

        Returns:
            更新されたイベント情報
        """
        if not self.service:
            raise RuntimeError("認証されていません")

        event = self.get_event(event_id)

        if summary:
            event['summary'] = summary
        if description:
            event['description'] = description
        if location:
            event['location'] = location

        updated_event = self.service.events().update(
            calendarId=self.calendar_id,
            eventId=event_id,
            body=event
        ).execute()

        logger.info(f"イベントを更新: {event_id}")
        return updated_event

    def delete_event(self, event_id: str) -> bool:
        """
        イベントを削除

        Args:
            event_id: イベントID

        Returns:
            成功したらTrue
        """
        if not self.service:
            raise RuntimeError("認証されていません")

        self.service.events().delete(
            calendarId=self.calendar_id,
            eventId=event_id
        ).execute()

        logger.info(f"イベントを削除: {event_id}")
        return True

    def get_today_events(self) -> List[Dict[str, Any]]:
        """今日のイベントを取得"""
        now = datetime.utcnow()
        start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1)

        return self.list_events(
            time_min=start_of_day,
            time_max=end_of_day
        )

    def get_upcoming_events(self, days: int = 7) -> List[Dict[str, Any]]:
        """
        指定された日数分の今後のイベントを取得

        Args:
            days: 取得する日数

        Returns:
            イベントリスト
        """
        now = datetime.utcnow()
        future_date = now + timedelta(days=days)

        return self.list_events(
            time_min=now,
            time_max=future_date
        )

    def list_calendars(self) -> List[Dict[str, Any]]:
        """ユーザーのカレンダー一覧を取得"""
        if not self.service:
            raise RuntimeError("認証されていません")

        calendar_list = self.service.calendarList().list().execute()
        calendars = calendar_list.get('items', [])

        logger.info(f"カレンダーを{len(calendars)}個取得しました")
        return calendars


# CLIツールとして使用する場合
def main():
    import argparse

    parser = argparse.ArgumentParser(description="Google Calendar API Client")
    parser.add_argument('--list', action='store_true', help='イベント一覧を表示')
    parser.add_argument('--today', action='store_true', help='今日のイベントを表示')
    parser.add_argument('--upcoming', type=int, default=7, help='今後N日分のイベントを表示')
    parser.add_argument('--create', help='イベントを作成')
    parser.add_argument('--start', help='開始日時 (ISO 8601)')
    parser.add_argument('--end', help='終了日時 (ISO 8601)')

    args = parser.parse_args()

    try:
        client = GoogleCalendarClient()

        if args.today:
            events = client.get_today_events()
            print(f"\n📅 今日のイベント ({len(events)}件):")
            for event in events:
                print(f"  - {event.get('summary', 'No title')}")
                print(f"    時間: {event.get('start', {}).get('dateTime', 'N/A')}")

        elif args.upcoming:
            events = client.get_upcoming_events(days=args.upcoming)
            print(f"\n📅 今後{args.upcoming}日間のイベント ({len(events)}件):")
            for event in events:
                print(f"  - {event.get('summary', 'No title')}")
                print(f"    時間: {event.get('start', {}).get('dateTime', 'N/A')}")

        elif args.create:
            if not args.start or not args.end:
                print("エラー: --start と --end が必要です")
                return

            client.create_event(
                summary=args.create,
                start=args.start,
                end=args.end
            )
            print(f"✅ イベントを作成しました: {args.create}")

        elif args.list:
            events = client.list_events()
            print(f"\n📅 イベント一覧 ({len(events)}件):")
            for event in events:
                print(f"  - {event.get('summary', 'No title')}")
                print(f"    時間: {event.get('start', {}).get('dateTime', 'N/A')}")

        else:
            print("オプションを指定してください。--help でヘルプを表示します。")

    except Exception as e:
        logger.error(f"エラー: {e}")
        print(f"❌ エラー: {e}")


if __name__ == "__main__":
    main()
