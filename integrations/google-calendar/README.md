# Google Calendar Integration

Google Calendar APIを統合して、カレンダーイベントの同期・管理を行うモジュールです。

## Features / 機能

- 📅 イベントの取得・作成・更新・削除
- 🗓️ 今日のイベント・今後のイベントの取得
- 🔐 OAuth2認証
- 📋 カレンダー一覧の取得

## Installation / インストール

```bash
pip install google-api-python-client google-auth-oauthlib
```

## Setup / 設定

1. [Google Cloud Console](https://console.cloud.google.com/)でプロジェクトを作成
2. Calendar APIを有効化
3. OAuth2認証情報をダウンロードして `credentials.json` として保存

## Usage / 使用方法

### Basic Usage / 基本的な使い方

```python
from integrations.google_calendar import GoogleCalendarClient

# クライアント初期化
client = GoogleCalendarClient()

# 今日のイベントを取得
events = client.get_today_events()
for event in events:
    print(f"- {event['summary']}")

# 新しいイベントを作成
client.create_event(
    summary="Team Meeting",
    start="2026-02-12T10:00:00Z",
    end="2026-02-12T11:00:00Z"
)

# 今後のイベントを取得
upcoming = client.get_upcoming_events(days=7)
```

### Environment Variables / 環境変数

| Variable / 変数 | Description / 説明 | Default / デフォルト |
|-----------------|---------------------|---------------------|
| `GOOGLE_CALENDAR_CREDENTIALS_PATH` | 認証情報ファイルのパス | `credentials.json` |
| `GOOGLE_CALENDAR_TOKEN_PATH` | トークンファイルのパス | `token.json` |
| `GOOGLE_CALENDAR_ID` | カレンダーID | `primary` |

### CLI Usage / CLI使用方法

```bash
# 今日のイベントを表示
python client.py --today

# 今後7日間のイベントを表示
python client.py --upcoming 7

# イベント一覧を表示
python client.py --list

# イベントを作成
python client.py --create "Meeting" --start "2026-02-12T10:00:00Z" --end "2026-02-12T11:00:00Z"
```

## API Reference / APIリファレンス

### `GoogleCalendarClient`

| Method / メソッド | Description / 説明 |
|-------------------|---------------------|
| `list_events(max_results=100, time_min=None, time_max=None)` | イベントを取得 |
| `get_event(event_id)` | 特定のイベントを取得 |
| `create_event(summary, start, end, ...)`)` | 新しいイベントを作成 |
| `update_event(event_id, ...)` | イベントを更新 |
| `delete_event(event_id)` | イベントを削除 |
| `get_today_events()` | 今日のイベントを取得 |
| `get_upcoming_events(days=7)` | 今後のイベントを取得 |
| `list_calendars()` | カレンダー一覧を取得 |

## Examples / 例

```python
# 複数日のイベントを取得
from datetime import datetime, timedelta

client = GoogleCalendarClient()

start = datetime.utcnow()
end = start + timedelta(days=30)

events = client.list_events(time_min=start, time_max=end)

# 参加者付きでイベントを作成
client.create_event(
    summary="Conference Call",
    start="2026-02-12T14:00:00Z",
    end="2026-02-12T15:00:00Z",
    description="Quarterly review meeting",
    location="Online",
    attendees=["user1@example.com", "user2@example.com"]
)

# イベントを更新
client.update_event(
    event_id="event_id",
    summary="Updated Meeting Title",
    location="New Location"
)

# イベントを削除
client.delete_event(event_id="event_id")
```

## License / ライセンス

MIT
