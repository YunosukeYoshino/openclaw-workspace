# ゲームメカニクス分析エージェント / Game Mechanics Analysis Agent

game-mechanics-analysis-agent

## 概要 / Overview

ゲーム内メカニクスの逆解析、数式化、バランス問題、不公平性の検出、パッチ変更によるメカニクス変化の追跡

Reverse engineer game mechanics, mathematical modeling, detect balance issues and unfairness, track mechanics changes from patches

## 機能 / Features

- Mechanics Reverse
- Math Modeling
- Balance Detection
- Patch Tracking
- Unfairness Alert
- Mechanics Docs

## 技術スタック / Tech Stack

- pandas, numpy, scipy, scikit-learn, matplotlib

## インストール / Installation

```bash
# Clone the repository
git clone <repository-url>
cd game-mechanics-analysis-agent

# Install dependencies
pip install -r requirements.txt
```

## 使い方 / Usage

### エージェントとして使用 / As an Agent

```python
from db import Database
from agent import GameMechanicsAnalysisAgent

# Initialize database
db = Database(db_path="data/game-mechanics-analysis-agent.db")
await db.initialize()

# Initialize agent
agent = GameMechanicsAnalysisAgent(db)
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
