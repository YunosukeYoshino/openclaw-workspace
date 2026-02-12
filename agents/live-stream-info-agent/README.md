# live-stream-info-agent

ライブ配信情報・アーカイブ管理エージェント / Live streaming information and archive management agent

## 機能 / Features

### 日本語 / Japanese
- ライブ配信スケジュール管理
- アーカイブ動画URL管理
- 配信プラットフォーム対応
- 視聴履歴・メモ

### English / 英語
- Live streaming schedule management
- Archive video URL management
- Streaming platform support
- Watch history and notes

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
