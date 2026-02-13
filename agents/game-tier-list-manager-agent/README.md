# ゲームTierリスト管理エージェント / Game Tier List Manager Agent

game-tier-list-manager-agent

## 概要 / Overview

コミュニティ投票によるTierリストの作成・更新、バージョン別、ロール別、使用率別のTierリスト、履歴管理、トレンド表示、差分比較

Create and update tier lists via community voting, version-specific, role-specific, usage-rate specific tier lists, history management, trend display, diff comparison

## 機能 / Features

- Tier List Creation
- Community Voting
- Version Management
- Role-Based Lists
- History Tracking
- Trend Visualization

## 技術スタック / Tech Stack

- pandas, numpy, matplotlib, seaborn, discord.py

## インストール / Installation

```bash
# Clone the repository
git clone <repository-url>
cd game-tier-list-manager-agent

# Install dependencies
pip install -r requirements.txt
```

## 使い方 / Usage

### エージェントとして使用 / As an Agent

```python
from db import Database
from agent import GameTierListManagerAgent

# Initialize database
db = Database(db_path="data/game-tier-list-manager-agent.db")
await db.initialize()

# Initialize agent
agent = GameTierListManagerAgent(db)
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
