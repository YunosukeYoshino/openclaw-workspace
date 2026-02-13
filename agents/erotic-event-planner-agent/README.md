# えっちイベントプランナーエージェント / Erotic Event Planner Agent

erotic-event-planner-agent

## 概要 / Overview

コミュニティイベント、チャレンジ、コンテストの企画・管理、参加者登録、投票、結果発表の自動化、タイムライン、通知、報酬システムの統合

Plan and manage community events, challenges, contests, auto participant registration, voting, result announcements, timeline, notifications, reward system integration

## 機能 / Features

- Event Planning
- Participant Management
- Voting System
- Auto Announcements
- Timeline Management
- Reward System

## 技術スタック / Tech Stack

- discord.py, pandas, icalendar, pytz, requests

## インストール / Installation

```bash
# Clone the repository
git clone <repository-url>
cd erotic-event-planner-agent

# Install dependencies
pip install -r requirements.txt
```

## 使い方 / Usage

### エージェントとして使用 / As an Agent

```python
from db import Database
from agent import EroticEventPlannerAgent

# Initialize database
db = Database(db_path="data/erotic-event-planner-agent.db")
await db.initialize()

# Initialize agent
agent = EroticEventPlannerAgent(db)
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
