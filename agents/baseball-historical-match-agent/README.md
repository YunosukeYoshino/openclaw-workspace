# 野球歴史的名試合エージェント / Baseball Historical Match Agent

baseball-historical-match-agent

## 概要 / Overview

歴史的な名試合、ドラマチックな展開の記録、勝敗を決めた重要場面の分析、映像・音声との統合、再現プレイ、記念イベントの自動提案

Record historic dramatic matches, analyze key moments, integrate with video/audio, suggest replay recreations and commemorative events

## 機能 / Features

- Historical Match Records
- Key Moment Analysis
- Media Integration
- Replay Suggestions
- Commemorative Events
- Match Search

## 技術スタック / Tech Stack

- pandas, numpy, requests, beautifulsoup4, matplotlib

## インストール / Installation

```bash
# Clone the repository
git clone <repository-url>
cd baseball-historical-match-agent

# Install dependencies
pip install -r requirements.txt
```

## 使い方 / Usage

### エージェントとして使用 / As an Agent

```python
from db import Database
from agent import BaseballHistoricalMatchAgent

# Initialize database
db = Database(db_path="data/baseball-historical-match-agent.db")
await db.initialize()

# Initialize agent
agent = BaseballHistoricalMatchAgent(db)
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
