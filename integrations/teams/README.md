# Microsoft Teams Integration

Microsoft Teams APIを統合して、通知・メッセージ送信を行うモジュールです。

## Features / 機能

- 💬 メッセージの送信
- 📋 カード形式メッセージ
- 🔔 通知レベル別メッセージ（info, warning, error, success）
- 📊 進捗レポート
- ❌ エラーメッセージ

## Installation / インストール

```bash
pip install requests
```

## Setup / 設定

1. Teamsチャンネルで「Incoming Webhook」コネクタを追加
2. Webhook URLを取得
3. 環境変数に設定: `export TEAMS_WEBHOOK_URL=https://outlook.office.com/webhook/...`

## Usage / 使用方法

### Basic Usage / 基本的な使い方

```python
from integrations.teams import TeamsClient

# クライアント初期化
client = TeamsClient()

# メッセージを送信
client.send_message(
    text="Hello, Teams!",
    title="Notification"
)

# カード形式で送信
client.send_card(
    title="Task Completed",
    text="The task has been completed successfully",
    facts=[
        {"name": "Status", "value": "Complete"},
        {"name": "Duration", "value": "2 hours"}
    ]
)

# 通知を送信
client.send_notification(
    title="Important Update",
    message="System update completed",
    level="success"
)

# エラーを報告
client.send_error(
    title="Build Failed",
    error_message="Compilation error in module X",
    context={"file": "main.py", "line": 42}
)

# 進捗を報告
client.send_progress(
    title="Data Migration",
    progress=0.75,
    status="Processing..."
)
```

### Environment Variables / 環境変数

| Variable / 変数 | Description / 説明 | Default / デフォルト |
|-----------------|---------------------|---------------------|
| `TEAMS_WEBHOOK_URL` | Teams Incoming Webhook URL | 必須 |

### CLI Usage / CLI使用方法

```bash
# メッセージを送信
python client.py --send "Hello, Teams!" --title "Notification"

# 通知を送信
python client.py --notify "Important" "Message content" --level info

# 警告を送信
python client.py --notify "Warning" "Something needs attention" --level warning

# エラーを送信
python client.py --notify "Error" "Something went wrong" --level error
```

## API Reference / APIリファレンス

### `TeamsClient`

| Method / メソッド | Description / 説明 |
|-------------------|---------------------|
| `send_message(text, ...)` | メッセージを送信 |
| `send_card(title, text, ...)` | カード形式でメッセージを送信 |
| `send_notification(title, message, level)` | 通知メッセージを送信 |
| `send_progress(title, progress, status)` | 進捗メッセージを送信 |
| `send_error(title, error_message, ...)` | エラーメッセージを送信 |

## Colors / 色

通知レベルと色の対応:

| Level / レベル | Color / 色 |
|----------------|------------|
| `info` | `0078D4` (Blue) |
| `warning` | `FF8C00` (Orange) |
| `error` | `FF0000` (Red) |
| `success` | `00FF00` (Green) |

## Examples / 例

```python
from integrations.teams import TeamsClient

client = TeamsClient()

# 複数のfactsを含むカード
client.send_card(
    title="Deployment Report",
    text="Deployment completed successfully",
    facts=[
        {"name": "Environment", "value": "Production"},
        {"name": "Version", "value": "v1.2.3"},
        {"name": "Duration", "value": "5m 32s"},
        {"name": "Status", "value": "Success"}
    ]
)

# リッチなセクション付きメッセージ
sections = [
    {
        "activityTitle": "New Task",
        "activitySubtitle": "Priority: High",
        "activityImage": "https://example.com/icon.png"
    },
    {
        "title": "Details",
        "text": "Task description goes here..."
    }
]
client.send_message(
    text="Message text",
    sections=sections
)

# カスタム色
client.send_message(
    text="Custom color message",
    color="800080"  # Purple
)

# 進捗更新
for i in range(0, 101, 25):
    client.send_progress(
        title="Data Processing",
        progress=i / 100,
        status=f"{i}% complete"
    )
```

## License / ライセンス

MIT
