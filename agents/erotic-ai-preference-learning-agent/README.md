# えっち嗜好AI学習エージェント / Erotic AI Preference Learning Agent

erotic-ai-preference-learning-agent

## 概要 / Overview

ユーザーの閲覧履歴、評価、フィードバックから嗜好を学習、時間経過による嗜好変化の追跡、潜在的嗜好の発見、新ジャンルの提案

Learn preferences from viewing history, ratings, feedback, track preference changes over time, discover latent preferences, suggest new genres

## 機能 / Features

- Preference Learning
- History Tracking
- Trend Detection
- Latent Preference
- New Genre Suggest
- Feedback Loop

## 技術スタック / Tech Stack

- pandas, numpy, scikit-learn, torch, surprise

## インストール / Installation

```bash
# Clone the repository
git clone <repository-url>
cd erotic-ai-preference-learning-agent

# Install dependencies
pip install -r requirements.txt
```

## 使い方 / Usage

### エージェントとして使用 / As an Agent

```python
from db import Database
from agent import EroticAiPreferenceLearningAgent

# Initialize database
db = Database(db_path="data/erotic-ai-preference-learning-agent.db")
await db.initialize()

# Initialize agent
agent = EroticAiPreferenceLearningAgent(db)
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
