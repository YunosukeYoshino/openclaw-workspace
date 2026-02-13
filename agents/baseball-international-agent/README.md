# 野球国際選手エージェント / Baseball International Agent

baseball-international-agent

## 概要 / Overview

海外選手（アジア、中南米等）の情報収集、ポスティングシステム、FA市場の分析、文化適応、移籍のリスク評価

Collect info on international players (Asia, Latin America, etc.), analyze posting system, FA market, cultural adaptation, transfer risk assessment

## 機能 / Features

- International Players
- Posting System
- FA Market
- Cultural Adaptation
- Risk Assessment
- Global Scouting

## 技術スタック / Tech Stack

- pandas, numpy, requests, beautifulsoup4, geopandas

## インストール / Installation

```bash
# Clone the repository
git clone <repository-url>
cd baseball-international-agent

# Install dependencies
pip install -r requirements.txt
```

## 使い方 / Usage

### エージェントとして使用 / As an Agent

```python
from db import Database
from agent import BaseballInternationalAgent

# Initialize database
db = Database(db_path="data/baseball-international-agent.db")
await db.initialize()

# Initialize agent
agent = BaseballInternationalAgent(db)
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
