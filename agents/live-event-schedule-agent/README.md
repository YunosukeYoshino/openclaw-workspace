# live-event-schedule-agent

ライブイベント・コンサートスケジュール管理エージェント / Live event and concert schedule management agent

## 機能 / Features

### 日本語 / Japanese
- ライブイベントスケジュール登録・管理
- アーティスト別イベント一覧
- 開催場所・会場情報管理
- イベント通知・リマインダー

### English / 英語
- Register and manage live event schedules
- Event lists by artist
- Venue and location information management
- Event notifications and reminders

## インストール / Installation

```bash
pip install -r requirements.txt
```

## 使用方法 / Usage

### エージェント実行 / Running the Agent

```bash
python3 agent.py
```

### Discord Bot / Discord Bot

```bash
export DISCORD_TOKEN="your_bot_token"
python3 discord.py
```

## データベース / Database

SQLiteデータベースを使用しています。初回実行時に自動的に作成されます。

## コマンド / Commands

| コマンド / Command | 説明 / Description |
|-------------------|-------------------|
| `!add <title> <artist> [venue]` | イベントを追加 / Add event |
| `!list [artist]` | イベントリスト表示 / List events |
| `!search <query>` | イベント検索 / Search events |
| `!upcoming [days]` | 近日のイベント表示 / Show upcoming events |

## ライセンス / License

MIT License
