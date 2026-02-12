# Slack Integration

Slack APIを統合して、通知・メッセージ送信を行うモジュールです。

## Features / 機能

- 💬 メッセージの送信・更新・削除
- 📢 チャンネル一覧の取得
- 👥 ユーザー情報の取得
- 🕐 チャンネル履歴の取得
- 👍 リアクションの追加
- 💌 エフェメラルメッセージ

## Installation / インストール

```bash
pip install requests
```

## Setup / 設定

1. [Slack API](https://api.slack.com/apps)で新しいアプリを作成
2. Bot Token を取得 (xoxb-...)
3. 必要なスコープを追加:
   - `chat:write` - メッセージの送信
   - `chat:write.public` - パブリックチャンネルへの投稿
   - `channels:read` - チャンネル情報の読み取り
   - `users:read` - ユーザー情報の読み取り
4. ワークスペースにアプリをインストール

## Usage / 使用方法

### Basic Usage / 基本的な使い方

```python
from integrations.slack import SlackClient

# クライアント初期化
client = SlackClient()

# メッセージを送信
client.send_message(
    channel="#general",
    text="Hello, Slack!"
)

# Block Kitを使用してリッチメッセージを送信
blocks = [
    {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": "Hello, *Slack*!"
        }
    },
    {
        "type": "actions",
        "elements": [
            {
                "type": "button",
                "text": {"type": "plain_text", "text": "Click me"},
                "action_id": "button_click"
            }
        ]
    }
]
client.send_message(channel="#general", blocks=blocks)

# チャンネル一覧を取得
channels = client.list_channels()

# ユーザー情報を取得
users = client.get_users()
```

### Environment Variables / 環境変数

| Variable / 変数 | Description / 説明 | Default / デフォルト |
|-----------------|---------------------|---------------------|
| `SLACK_BOT_TOKEN` | Slack Bot Token | 必須 |
| `SLACK_SIGNING_SECRET` | Slack Signing Secret | 任意 |

### CLI Usage / CLI使用方法

```bash
# チャンネル一覧を表示
python client.py --list-channels

# ユーザー一覧を表示
python client.py --list-users

# メッセージを送信
python client.py --send "Hello, Slack!" --channel "#general"
```

## API Reference / APIリファレンス

### `SlackClient`

| Method / メソッド | Description / 説明 |
|-------------------|---------------------|
| `send_message(channel, text, ...)` | メッセージを送信 |
| `update_message(channel, timestamp, ...)` | メッセージを更新 |
| `delete_message(channel, timestamp)` | メッセージを削除 |
| `list_channels()` | チャンネル一覧を取得 |
| `get_channel_info(channel_id)` | チャンネル情報を取得 |
| `get_users()` | ユーザー一覧を取得 |
| `get_user_info(user_id)` | ユーザー情報を取得 |
| `post_ephemeral(channel, user, ...)` | エフェメラルメッセージを送信 |
| `add_reaction(channel, timestamp, reaction)` | リアクションを追加 |
| `get_history(channel, ...)` | チャンネル履歴を取得 |

## Examples / 例

```python
# スレッドに返信
client.send_message(
    channel="#general",
    text="Replying to thread",
    thread_ts="1234567890.123456"
)

# エフェメラルメッセージを送信
client.post_ephemeral(
    channel="#general",
    user="U12345678",
    text="This is only visible to you"
)

# メッセージを更新
client.update_message(
    channel="C12345678",
    timestamp="1234567890.123456",
    text="Updated message"
)

# リアクションを追加
client.add_reaction(
    channel="C12345678",
    timestamp="1234567890.123456",
    reaction="thumbs_up"
)

# 履歴を取得
history = client.get_history(
    channel="C12345678",
    limit=50
)

# Block Kitでリッチメッセージ
blocks = [
    {
        "type": "header",
        "text": {"type": "plain_text", "text": "Task Update"}
    },
    {
        "type": "section",
        "fields": [
            {"type": "mrkdwn", "text": "*Status:*\nIn Progress"},
            {"type": "mrkdwn", "text": "*Priority:*\nHigh"}
        ]
    },
    {
        "type": "section",
        "text": {"type": "mrkdwn", "text": "Description goes here..."}
    }
]
client.send_message(channel="#general", blocks=blocks)
```

## License / ライセンス

MIT
