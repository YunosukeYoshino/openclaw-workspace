# vtuber-ranking-agent

VTuberランキング・統計エージェント / VTuber ranking and statistics agent

## 機能 / Features

### 日本語 / Japanese
- 登録者数ランキング
- 配信視聴数統計
- 成長率計算
- お気に入りVTuber比較

### English / 英語
- Subscriber count rankings
- Streaming view count statistics
- Growth rate calculation
- Compare favorite VTubers

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
| `!add <name> [description]` | VTuberを追加 / Add VTuber |
| `!list` | VTuberリスト表示 / List VTubers |
| `!search <query>` | VTuber検索 / Search VTubers |
| `!upcoming [days]` | 近日の配信表示 / Show upcoming streams |

## ライセンス / License

MIT License
