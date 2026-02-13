# えっちフィードバックハブエージェント / Erotic Feedback Hub Agent

erotic-feedback-hub-agent

## 概要 / Overview

ファンからのフィードバック、リクエストの収集・整理、クリエイターへの定期的なフィードバックレポート、トレンド分析、人気投票、改善提案の集約

Collect and organize fan feedback and requests, periodic feedback reports to creators, trend analysis, popularity voting, improvement suggestion aggregation

## 機能 / Features

- Feedback Collection
- Request Organization
- Creator Reports
- Trend Analysis
- Popularity Voting
- Improvement Suggestions

## 技術スタック / Tech Stack

- pandas, scikit-learn, numpy, discord.py, requests

## インストール / Installation

```bash
# Clone the repository
git clone <repository-url>
cd erotic-feedback-hub-agent

# Install dependencies
pip install -r requirements.txt
```

## 使い方 / Usage

### エージェントとして使用 / As an Agent

```python
from db import Database
from agent import EroticFeedbackHubAgent

# Initialize database
db = Database(db_path="data/erotic-feedback-hub-agent.db")
await db.initialize()

# Initialize agent
agent = EroticFeedbackHubAgent(db)
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
