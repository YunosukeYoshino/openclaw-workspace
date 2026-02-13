# 野球ライブ通知エージェント

Sends notifications for important events during live baseball games

野球ライブ中継中の重要イベントの通知を送ります

## 機能

- Real-time event alerts\n- Score change notifications\n- Key moment alerts\n- Game start/end reminders\n- Custom alert rules

## コマンド

- `notify setup - Configure notifications`\n- `notify game <game_id> - Get game notifications`\n- `notify team <team> - Get team notifications`\n- `notify alerts - Show active alerts`

## インストール

```bash
pip install -r requirements.txt
```

## 使い方

```bash
# エージェントを実行
python3 agent.py

# データベースを操作
python3 db.py
```

## データベーススキーマ

### entries

エントリー（ノート、タスク、アイデア等）を保存します。

| カラム | タイプ | 説明 |
|--------|--------|------|
| id | INTEGER | 主キー |
| title | TEXT | タイトル |
| content | TEXT | 内容 |
| type | TEXT | タイプ（note, task, idea, goal, project） |
| tags | TEXT | タグ（JSON） |
| status | TEXT | ステータス（active, archived, completed） |
| created_at | TIMESTAMP | 作成日時 |
| updated_at | TIMESTAMP | 更新日時 |

### notifications

通知を保存します。

| カラム | タイプ | 説明 |
|--------|--------|------|
| id | INTEGER | 主キー |
| event_id | TEXT | イベントID |
| event_type | TEXT | イベントタイプ |
| message | TEXT | 通知メッセージ |
| sent_at | TIMESTAMP | 送信日時 |
| status | TEXT | ステータス（pending, sent） |

### stats

統計を保存します。

| カラム | タイプ | 説明 |
|--------|--------|------|
| id | INTEGER | 主キー |
| game_id | TEXT | ゲームID |
| stat_type | TEXT | 統計タイプ |
| stat_value | TEXT | 統計値 |
| recorded_at | TIMESTAMP | 記録日時 |

### highlights

ハイライトを保存します。

| カラム | タイプ | 説明 |
|--------|--------|------|
| id | INTEGER | 主キー |
| game_id | TEXT | ゲームID |
| title | TEXT | タイトル |
| description | TEXT | 説明 |
| timestamp | INTEGER | タイムスタンプ |
| video_url | TEXT | 動画URL |
| created_at | TIMESTAMP | 作成日時 |

### settings

設定を保存します。

| カラム | タイプ | 説明 |
|--------|--------|------|
| key | TEXT | 設定キー（主キー） |
| value | TEXT | 設定値 |
| updated_at | TIMESTAMP | 更新日時 |

## API Reference

### Baseball_Live_Notifications_AgentDB

```python
from db import Baseball_Live_Notifications_AgentDB

db = Baseball_Live_Notifications_AgentDB()

# エントリーを追加
entry_id = db.add_entry("タイトル", "内容", "note", ["tag1", "tag2"])

# エントリーを取得
entry = db.get_entry(entry_id)

# エントリーを一覧表示
entries = db.list_entries(entry_type="note", limit=10)

# エントリーを更新
db.update_entry(entry_id, title="新しいタイトル", content="新しい内容")

# エントリーを削除
db.delete_entry(entry_id)

# 通知を追加
notification_id = db.add_notification("event123", "game_start", "試合開始！")

# 統計を追加
stat_id = db.add_stat("game123", "home_runs", "5")

# ハイライトを追加
highlight_id = db.add_highlight("game123", "ホームラン", "特大HR", 3600, "https://example.com/video.mp4")

# 設定を取得/設定
db.set_setting("language", "ja")
language = db.get_setting("language")
```

## License

MIT

---

## English

# 野球ライブ通知エージェント

Sends notifications for important events during live baseball games

## Features

- Real-time event alerts\n- Score change notifications\n- Key moment alerts\n- Game start/end reminders\n- Custom alert rules

## Commands

- `notify setup - Configure notifications`\n- `notify game <game_id> - Get game notifications`\n- `notify team <team> - Get team notifications`\n- `notify alerts - Show active alerts`

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
# Run the agent
python3 agent.py

# Interact with database
python3 db.py
```

## Database Schema

### entries

Stores entries (notes, tasks, ideas, etc.).

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| title | TEXT | Title |
| content | TEXT | Content |
| type | TEXT | Type (note, task, idea, goal, project) |
| tags | TEXT | Tags (JSON) |
| status | TEXT | Status (active, archived, completed) |
| created_at | TIMESTAMP | Created at |
| updated_at | TIMESTAMP | Updated at |

### notifications

Stores notifications.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| event_id | TEXT | Event ID |
| event_type | TEXT | Event type |
| message | TEXT | Notification message |
| sent_at | TIMESTAMP | Sent at |
| status | TEXT | Status (pending, sent) |

### stats

Stores statistics.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| game_id | TEXT | Game ID |
| stat_type | TEXT | Stat type |
| stat_value | TEXT | Stat value |
| recorded_at | TIMESTAMP | Recorded at |

### highlights

Stores highlights.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| game_id | TEXT | Game ID |
| title | TEXT | Title |
| description | TEXT | Description |
| timestamp | INTEGER | Timestamp |
| video_url | TEXT | Video URL |
| created_at | TIMESTAMP | Created at |

### settings

Stores settings.

| Column | Type | Description |
|--------|------|-------------|
| key | TEXT | Setting key (primary key) |
| value | TEXT | Setting value |
| updated_at | TIMESTAMP | Updated at |

## License

MIT
