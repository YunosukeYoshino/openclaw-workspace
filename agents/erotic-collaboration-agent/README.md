# えっちコラボレーションエージェント / Erotic Collaboration Agent

erotic-collaboration-agent

## 概要 / Overview

クリエイター間のコラボ企画の提案・管理、リクエストマッチング、プロジェクト進捗管理、作品の共同作成、リリース、プロモーション

Propose and manage creator collab projects, request matching, project progress tracking, collaborative creation, releases, promotions

## 機能 / Features

- Collab Proposal
- Request Matching
- Progress Tracking
- Co-creation Tools
- Release Management
- Promotion

## 技術スタック / Tech Stack

- discord.py, requests, pandas, gitpython, yaml

## インストール / Installation

```bash
# Clone the repository
git clone <repository-url>
cd erotic-collaboration-agent

# Install dependencies
pip install -r requirements.txt
```

## 使い方 / Usage

### エージェントとして使用 / As an Agent

```python
from db import Database
from agent import EroticCollaborationAgent

# Initialize database
db = Database(db_path="data/erotic-collaboration-agent.db")
await db.initialize()

# Initialize agent
agent = EroticCollaborationAgent(db)
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
