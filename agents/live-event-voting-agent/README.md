# live-event-voting-agent

投票・アンケート管理エージェント / Voting and survey management agent

## 機能 / Features

### 日本語 / Japanese
- 投票・アンケート作成
- 投票結果集計
- 複数選択・ランク投票対応
- 投票履歴・統計

### English / 英語
- Create voting and surveys
- Aggregate voting results
- Multiple choice and ranking voting support
- Voting history and statistics

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
