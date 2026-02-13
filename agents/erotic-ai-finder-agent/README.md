# えっちAI検索エージェント / Erotic AI Finder Agent

erotic-ai-finder-agent

## 概要 / Overview

自然言語でのあいまい検索（「切ない」「情熱的」等）、画像、動画からの類似コンテンツ検索、複合条件検索、パーソナライズ順位付け

Natural language fuzzy search (sad, passionate, etc.), similar content search from images/videos, complex condition search, personalized ranking

## 機能 / Features

- Natural Search
- Semantic Search
- Image Search
- Video Search
- Complex Filters
- Personalized Rank

## 技術スタック / Tech Stack

- pandas, numpy, scikit-learn, torch, sentence-transformers

## インストール / Installation

```bash
# Clone the repository
git clone <repository-url>
cd erotic-ai-finder-agent

# Install dependencies
pip install -r requirements.txt
```

## 使い方 / Usage

### エージェントとして使用 / As an Agent

```python
from db import Database
from agent import EroticAiFinderAgent

# Initialize database
db = Database(db_path="data/erotic-ai-finder-agent.db")
await db.initialize()

# Initialize agent
agent = EroticAiFinderAgent(db)
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
