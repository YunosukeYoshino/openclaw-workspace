# 野球場歴史エージェント / Baseball Stadium History Agent

baseball-stadium-history-agent

## 概要 / Overview

歴史的野球場の建設、改名、移転などの歴史、球場の特徴、伝説的なイベント、記録的な試合との紐付け、球場ツアー、記念日の自動通知

History of ballpark construction, renaming, relocation, stadium features, legendary events, tie to record games, stadium tours, anniversary notifications

## 機能 / Features

- Stadium Histories
- Feature Tracking
- Event Records
- Historic Matches
- Tour Planning
- Anniversary Alerts

## 技術スタック / Tech Stack

- pandas, numpy, requests, geopandas, matplotlib

## インストール / Installation

```bash
# Clone the repository
git clone <repository-url>
cd baseball-stadium-history-agent

# Install dependencies
pip install -r requirements.txt
```

## 使い方 / Usage

### エージェントとして使用 / As an Agent

```python
from db import Database
from agent import BaseballStadiumHistoryAgent

# Initialize database
db = Database(db_path="data/baseball-stadium-history-agent.db")
await db.initialize()

# Initialize agent
agent = BaseballStadiumHistoryAgent(db)
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
