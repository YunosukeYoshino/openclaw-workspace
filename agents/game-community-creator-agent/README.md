# ゲームコミュニティ作成エージェント / Game Community Creator Agent

game-community-creator-agent

## 概要 / Overview

ディスコードサーバー、フォーラムの自動セットアップ、ロール、チャンネル、ボットの初期化、コミュニティガイドライン、ルールのテンプレート提供

Auto-setup Discord servers, forums, initialize roles, channels, bots, provide community guidelines, rules templates

## 機能 / Features

- Discord Setup
- Forum Creation
- Role Management
- Channel Config
- Rule Templates

## 技術スタック / Tech Stack

- discord.py, pyyaml, jinja2

## インストール / Installation

```bash
# Clone the repository
git clone <repository-url>
cd game-community-creator-agent

# Install dependencies
pip install -r requirements.txt
```

## 使い方 / Usage

### エージェントとして使用 / As an Agent

```python
from db import Database
from agent import GameCommunityCreatorAgent

# Initialize database
db = Database(db_path="data/game-community-creator-agent.db")
await db.initialize()

# Initialize agent
agent = GameCommunityCreatorAgent(db)
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
