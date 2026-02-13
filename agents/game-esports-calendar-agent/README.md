# ゲームeスポーツカレンダーエージェント / Game Esports Calendar Agent

game-esports-calendar-agent

## 概要 / Overview

主要eスポーツ大会のスケジュール管理、資格、予選、決勝の情報統合、リマインダー、ストリームリンクの提供

Major esports tournament schedule management, integrate qualification, prelim, finals info, reminders, stream links

## 機能 / Features

- Tournament Schedule
- Qualification Info
- Reminders
- Stream Links
- Multi-Game Support
- Calendar Export

## 技術スタック / Tech Stack

- pandas, numpy, requests, icalendar, discord.py

## インストール / Installation

```bash
# Clone the repository
git clone <repository-url>
cd game-esports-calendar-agent

# Install dependencies
pip install -r requirements.txt
```

## 使い方 / Usage

### エージェントとして使用 / As an Agent

```python
from db import Database
from agent import GameEsportsCalendarAgent

# Initialize database
db = Database(db_path="data/game-esports-calendar-agent.db")
await db.initialize()

# Initialize agent
agent = GameEsportsCalendarAgent(db)
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
