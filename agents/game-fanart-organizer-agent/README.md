# ゲームファンアート整理エージェント / Game Fanart Organizer Agent

game-fanart-organizer-agent

## 概要 / Overview

ファンアートの自動収集、タグ付け、分類、キャラクター、スタイル、テーマでの整理、コレクション作成、ギャラリー表示、検索機能

Auto-collect fanart, auto-tagging, categorization, organize by character, style, theme, collection creation, gallery display, search

## 機能 / Features

- Auto Collection
- Smart Tagging
- Categorization
- Gallery Display
- Advanced Search

## 技術スタック / Tech Stack

- Pillow, scikit-image, scikit-learn, pillow-heif, exifread

## インストール / Installation

```bash
# Clone the repository
git clone <repository-url>
cd game-fanart-organizer-agent

# Install dependencies
pip install -r requirements.txt
```

## 使い方 / Usage

### エージェントとして使用 / As an Agent

```python
from db import Database
from agent import GameFanartOrganizerAgent

# Initialize database
db = Database(db_path="data/game-fanart-organizer-agent.db")
await db.initialize()

# Initialize agent
agent = GameFanartOrganizerAgent(db)
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

### tags テーブル

| カラム | 型 | 説明 |
|--------|------|------|
| id | INTEGER | 主キー |
| name | TEXT | タグ名（ユニーク） |
| created_at | TIMESTAMP | 作成日時 |

### entry_tags テーブル

| カラム | 型 | 説明 |
|--------|------|------|
| entry_id | INTEGER | エントリーID（外部キー） |
| tag_id | INTEGER | タグID（外部キー） |

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
