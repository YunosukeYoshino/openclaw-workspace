# 野球文化エージェント / Baseball Culture Agent

baseball-culture-agent

## 概要 / Overview

野球に関連する音楽、映画、文学、アートの収集、ファン文化、チーム伝統、サポーターの歴史、野球の社会的影響、文化への統合分析

Collect baseball-related music, film, literature, art, fan culture, team traditions, supporter history, social impact, cultural integration analysis

## 機能 / Features

- Cultural Content
- Fan Culture
- Team Traditions
- Media Collection
- Social Impact
- Cultural Analysis

## 技術スタック / Tech Stack

- pandas, numpy, requests, beautifulsoup4, networkx

## インストール / Installation

```bash
# Clone the repository
git clone <repository-url>
cd baseball-culture-agent

# Install dependencies
pip install -r requirements.txt
```

## 使い方 / Usage

### エージェントとして使用 / As an Agent

```python
from db import Database
from agent import BaseballCultureAgent

# Initialize database
db = Database(db_path="data/baseball-culture-agent.db")
await db.initialize()

# Initialize agent
agent = BaseballCultureAgent(db)
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
