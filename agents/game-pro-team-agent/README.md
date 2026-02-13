# ゲームプロチームエージェント / Game Pro Team Agent

game-pro-team-agent

## 概要 / Overview

プロチームの情報、ロスター、成績追跡、チーム戦略、シグネチャーの分析、移籍、契約、解散の情報管理

Pro team info, roster, performance tracking, team strategy, signature analysis, manage transfer, contract, disband info

## 機能 / Features

- Team Profiles
- Roster Tracking
- Performance Stats
- Strategy Analysis
- Transfer News
- Contract Info

## 技術スタック / Tech Stack

- pandas, numpy, requests, networkx, matplotlib

## インストール / Installation

```bash
# Clone the repository
git clone <repository-url>
cd game-pro-team-agent

# Install dependencies
pip install -r requirements.txt
```

## 使い方 / Usage

### エージェントとして使用 / As an Agent

```python
from db import Database
from agent import GameProTeamAgent

# Initialize database
db = Database(db_path="data/game-pro-team-agent.db")
await db.initialize()

# Initialize agent
agent = GameProTeamAgent(db)
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
