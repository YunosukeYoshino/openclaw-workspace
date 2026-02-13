# ゲームビルド最適化エージェント / Game Build Optimizer Agent

game-build-optimizer-agent

## 概要 / Overview

アイテム、スキル、ルーンの最適ビルド提案、対戦相手、状況別のビルド変化案、パッチ対応、成功率統計、ビルド共有

Suggest optimal builds for items, skills, runes, build variations based on opponent and situation, patch support, success rate statistics, build sharing

## 機能 / Features

- Build Optimization
- Item Suggestions
- Skill Priorities
- Rune Configs
- Patch Updates
- Build Sharing

## 技術スタック / Tech Stack

- pandas, numpy, scikit-learn, requests, beautifulsoup4

## インストール / Installation

```bash
# Clone the repository
git clone <repository-url>
cd game-build-optimizer-agent

# Install dependencies
pip install -r requirements.txt
```

## 使い方 / Usage

### エージェントとして使用 / As an Agent

```python
from db import Database
from agent import GameBuildOptimizerAgent

# Initialize database
db = Database(db_path="data/game-build-optimizer-agent.db")
await db.initialize()

# Initialize agent
agent = GameBuildOptimizerAgent(db)
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
