# live-event-recap-agent

イベントレポート・まとめ作成エージェント / Event report and summary creation agent

## 機能 / Features

### 日本語 / Japanese
- イベントレポート作成
- 写真・動画管理
- 参加者感想・コメント
- イベントハイライトまとめ

### English / 英語
- Create event reports
- Photo and video management
- Participant impressions and comments
- Event highlights summary

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
