# えっちファンクラブエージェント / Erotic Fan Club Agent

erotic-fan-club-agent

## 概要 / Overview

お気に入りクリエイター・作品のファンクラブ管理、専用のニュース、リリース、イベント情報の提供、ファン投票、リクエスト機能、限定コンテンツへのアクセス

Fan club management for favorite creators/content, dedicated news, releases, event info, fan voting, request features, exclusive content access

## 機能 / Features

- Fan Club Management
- News & Releases
- Event Information
- Fan Voting
- Request System
- Exclusive Content

## 技術スタック / Tech Stack

- discord.py, requests, beautifulsoup4, pandas, numpy

## インストール / Installation

```bash
# Clone the repository
git clone <repository-url>
cd erotic-fan-club-agent

# Install dependencies
pip install -r requirements.txt
```

## 使い方 / Usage

### エージェントとして使用 / As an Agent

```python
from db import Database
from agent import EroticFanClubAgent

# Initialize database
db = Database(db_path="data/erotic-fan-club-agent.db")
await db.initialize()

# Initialize agent
agent = EroticFanClubAgent(db)
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
