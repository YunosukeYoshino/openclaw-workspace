# 野球イニング戦略エージェント / Baseball Inning Strategy Agent

baseball-inning-strategy-agent

## 概要 / Overview

イニングごとの最適戦略（盗塁、バント、犠打等）、点差、アウトカウント、ランナー状況に応じた提案、守備シフト、リリーフ投入タイミングのアドバイス

Optimal strategy by inning (stealing, bunting, sacrifice, etc.), suggestions based on score, out count, runner situation, defensive shifts, relief pitching timing advice

## 機能 / Features

- Inning Strategy
- Situation Analysis
- Score-Based Tactics
- Runner Situation
- Defensive Shifts
- Relief Timing

## 技術スタック / Tech Stack

- pandas, numpy, scikit-learn, pytz, requests

## インストール / Installation

```bash
# Clone the repository
git clone <repository-url>
cd baseball-inning-strategy-agent

# Install dependencies
pip install -r requirements.txt
```

## 使い方 / Usage

### エージェントとして使用 / As an Agent

```python
from db import Database
from agent import BaseballInningStrategyAgent

# Initialize database
db = Database(db_path="data/baseball-inning-strategy-agent.db")
await db.initialize()

# Initialize agent
agent = BaseballInningStrategyAgent(db)
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
