# えっちコレクションショーケースエージェント / Erotic Collection Showcase Agent

erotic-collection-showcase-agent

## 概要 / Overview

コレクションの自動カタログ化、ギャラリー表示、テーマ別、スタイル別、タグ別での整理、シェア機能、プレビュー、コレクション比較

Auto-catalog collections, gallery display, organize by theme, style, tags, sharing features, preview, collection comparison

## 機能 / Features

- Auto Catalog
- Gallery Display
- Smart Organization
- Sharing Features
- Preview System
- Collection Comparison

## 技術スタック / Tech Stack

- Pillow, scikit-image, Pillow, pandas, numpy

## インストール / Installation

```bash
# Clone the repository
git clone <repository-url>
cd erotic-collection-showcase-agent

# Install dependencies
pip install -r requirements.txt
```

## 使い方 / Usage

### エージェントとして使用 / As an Agent

```python
from db import Database
from agent import EroticCollectionShowcaseAgent

# Initialize database
db = Database(db_path="data/erotic-collection-showcase-agent.db")
await db.initialize()

# Initialize agent
agent = EroticCollectionShowcaseAgent(db)
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
