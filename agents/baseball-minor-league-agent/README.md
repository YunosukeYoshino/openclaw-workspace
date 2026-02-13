# 野球マイナーリーグエージェント / Baseball Minor League Agent

baseball-minor-league-agent

## 概要 / Overview

マイナーリーグ選手のパフォーマンス追跡、昇格の可能性、開発状況の評価、ロスター管理、メジャー昇格のタイミング提案

Track minor league player performance, promotion potential, development evaluation, roster management, suggest major league call-up timing

## 機能 / Features

- Performance Track
- Promotion Potential
- Development Eval
- Roster Mgmt
- Call-up Timing
- Progress Tracking

## 技術スタック / Tech Stack

- pandas, numpy, requests, matplotlib, scikit-learn

## インストール / Installation

```bash
# Clone the repository
git clone <repository-url>
cd baseball-minor-league-agent

# Install dependencies
pip install -r requirements.txt
```

## 使い方 / Usage

### エージェントとして使用 / As an Agent

```python
from db import Database
from agent import BaseballMinorLeagueAgent

# Initialize database
db = Database(db_path="data/baseball-minor-league-agent.db")
await db.initialize()

# Initialize agent
agent = BaseballMinorLeagueAgent(db)
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
