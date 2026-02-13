# ゲームカウンターピックエージェント / Game Counter Pick Agent

game-counter-pick-agent

## 概要 / Overview

特定キャラ・デッキへの最適カウンターピック提案、シナジー、アンチシナジーの分析、ビルドガイド、戦略解説の自動生成

Suggest optimal counter picks for specific characters/decks, analyze synergies and anti-synergies, auto-generate build guides and strategy explanations

## 機能 / Features

- Counter Pick Suggest
- Synergy Analysis
- Anti-Synergy Detection
- Build Guide Gen
- Strategy Explain
- Win Rate Stats

## 技術スタック / Tech Stack

- pandas, numpy, scikit-learn, networkx, requests

## インストール / Installation

```bash
# Clone the repository
git clone <repository-url>
cd game-counter-pick-agent

# Install dependencies
pip install -r requirements.txt
```

## 使い方 / Usage

### エージェントとして使用 / As an Agent

```python
from db import Database
from agent import GameCounterPickAgent

# Initialize database
db = Database(db_path="data/game-counter-pick-agent.db")
await db.initialize()

# Initialize agent
agent = GameCounterPickAgent(db)
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
