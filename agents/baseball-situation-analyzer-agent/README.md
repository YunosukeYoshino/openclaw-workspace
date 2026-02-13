# 野球状況分析エージェント / Baseball Situation Analyzer Agent

baseball-situation-analyzer-agent

## 概要 / Overview

試合の流れ、勢い、勝率のリアルタイム分析、キーポイント（9回裏2アウト満塁等）の特定と警告、勝敗分岐点の検出、重要場面のハイライト

Real-time analysis of game flow, momentum, win probability, key moment identification and alerts (9th inning 2 outs bases loaded, etc.), win/loss branching point detection, key situation highlights

## 機能 / Features

- Game Flow Analysis
- Momentum Tracking
- Win Probability
- Key Moment Alerts
- Branching Detection
- Highlight Generation

## 技術スタック / Tech Stack

- pandas, numpy, scikit-learn, matplotlib, requests

## インストール / Installation

```bash
# Clone the repository
git clone <repository-url>
cd baseball-situation-analyzer-agent

# Install dependencies
pip install -r requirements.txt
```

## 使い方 / Usage

### エージェントとして使用 / As an Agent

```python
from db import Database
from agent import BaseballSituationAnalyzerAgent

# Initialize database
db = Database(db_path="data/baseball-situation-analyzer-agent.db")
await db.initialize()

# Initialize agent
agent = BaseballSituationAnalyzerAgent(db)
await agent.initialize()

# Process data
result = await agent.process({"key": "value"})
print(result)
```

### Discord Botとして使用 / As a Discord Bot

```python
from discord import DiscordBot

# Create bot
bot = create_bot(db, token="YOUR_DISCORD_TOKEN", command_prefix="!")

# Run bot
bot.run()
```

## データベース構造 / Database Schema

### entries テーブル

| カラム | 型 | 説明 |
|--------|------|------|
| id | INTEGER | 主キー |
| title | TEXT | タイトル |
| content | TEXT | コンテンツ |
| category | TEXT | カテゴリ |
| tags | TEXT | タグ（カンマ区切り） |
| created_at | TIMESTAMP | 作成日時 |
| updated_at | TIMESTAMP | 更新日時 |

## Discordコマンド / Discord Commands

| コマンド | 説明 |
|----------|------|
| `!status` | エージェントのステータスを確認 |
| `!help` | ヘルプを表示 |
| `!create <title> <content>` | 新しいエントリーを作成 |
| `!list [category]` | エントリーを一覧表示 |
| `!search <query>` | エントリーを検索 |
| `!get <id>` | IDでエントリーを取得 |

## ライセンス / License

MIT License
