# ゲームメタ議論エージェント / Game Meta Discussion Agent

game-meta-discussion-agent

## 概要 / Overview

メタ環境に関する議論スレッドの自動生成、注目トピック、投票、アンケートの作成、コミュニティ意見の集約、サマリー表示

Auto-generate discussion threads about meta environment, create trending topics, polls, surveys, aggregate community opinions, display summaries

## 機能 / Features

- Thread Generation
- Topic Detection
- Poll Creation
- Survey Management
- Opinion Aggregation
- Summary Display

## 技術スタック / Tech Stack

- discord.py, pandas, numpy, scikit-learn, requests

## インストール / Installation

```bash
# Clone the repository
git clone <repository-url>
cd game-meta-discussion-agent

# Install dependencies
pip install -r requirements.txt
```

## 使い方 / Usage

### エージェントとして使用 / As an Agent

```python
from db import Database
from agent import GameMetaDiscussionAgent

# Initialize database
db = Database(db_path="data/game-meta-discussion-agent.db")
await db.initialize()

# Initialize agent
agent = GameMetaDiscussionAgent(db)
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
