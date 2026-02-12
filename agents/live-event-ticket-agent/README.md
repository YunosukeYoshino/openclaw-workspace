# live-event-ticket-agent

チケット販売・予約管理エージェント / Ticket sales and reservation management agent

## 機能 / Features

### 日本語 / Japanese
- チケット販売情報管理
- 予約状況トラッキング
- 販売サイトURL保存
- 購入履歴管理

### English / 英語
- Ticket sales information management
- Reservation status tracking
- Sales site URL storage
- Purchase history management

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
