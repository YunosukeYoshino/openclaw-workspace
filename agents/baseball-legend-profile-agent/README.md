# 野球伝説選手プロフィールエージェント / Baseball Legend Profile Agent

baseball-legend-profile-agent

## 概要 / Overview

殿堂入り選手、レジェンド選手のプロフィール管理、統計、ハイライト、語り継がれるエピソードの収集、クロス世代比較、影響力の可視化

Manage Hall of Fame and legend player profiles, collect stats, highlights, and legendary stories, cross-generational comparison, influence visualization

## 機能 / Features

- Legend Profiles
- Statistics Tracking
- Highlight Collection
- Cross-Gen Comparison
- Influence Metrics
- Search & Discovery

## 技術スタック / Tech Stack

- pandas, numpy, requests, matplotlib, networkx

## インストール / Installation

```bash
# Clone the repository
git clone <repository-url>
cd baseball-legend-profile-agent

# Install dependencies
pip install -r requirements.txt
```

## 使い方 / Usage

### エージェントとして使用 / As an Agent

```python
from db import Database
from agent import BaseballLegendProfileAgent

# Initialize database
db = Database(db_path="data/baseball-legend-profile-agent.db")
await db.initialize()

# Initialize agent
agent = BaseballLegendProfileAgent(db)
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
