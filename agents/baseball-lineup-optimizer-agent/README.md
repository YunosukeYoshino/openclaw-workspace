# 野球打順最適化エージェント / Baseball Lineup Optimizer Agent

baseball-lineup-optimizer-agent

## 概要 / Overview

対戦先発投手に応じた最適打順提案、左右の打席、相性、状況別の最適化、代打、守備固めの入れ替え提案

Optimal batting order suggestions based on opposing starter, left/right handedness, compatibility, situation-based optimization, pinch hitter, defensive replacement suggestions

## 機能 / Features

- Lineup Optimization
- Left/Right Matchup
- Compatibility Analysis
- Situation Optimization
- Pinch Hitter Suggest
- Defensive Replacements

## 技術スタック / Tech Stack

- pandas, numpy, scipy, scikit-learn, pulp

## インストール / Installation

```bash
# Clone the repository
git clone <repository-url>
cd baseball-lineup-optimizer-agent

# Install dependencies
pip install -r requirements.txt
```

## 使い方 / Usage

### エージェントとして使用 / As an Agent

```python
from db import Database
from agent import BaseballLineupOptimizerAgent

# Initialize database
db = Database(db_path="data/baseball-lineup-optimizer-agent.db")
await db.initialize()

# Initialize agent
agent = BaseballLineupOptimizerAgent(db)
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
