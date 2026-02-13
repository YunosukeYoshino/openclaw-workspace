# ゲーム確率計算エージェント / Game Probability Agent

game-probability-agent

## 概要 / Overview

ゲーム内の確率計算（ドロップ、クリティカル、等）、Monte Carloシミュレーションによる期待値計算、確率の可視化、最適戦略の提案

Calculate in-game probabilities (drop rates, crits, etc.), expected value via Monte Carlo simulation, probability visualization, optimal strategy suggestions

## 機能 / Features

- Probability Calculation
- Monte Carlo Sim
- Expected Value
- Probability Viz
- Strategy Opt
- Risk Assessment

## 技術スタック / Tech Stack

- pandas, numpy, scipy, matplotlib, seaborn

## インストール / Installation

```bash
# Clone the repository
git clone <repository-url>
cd game-probability-agent

# Install dependencies
pip install -r requirements.txt
```

## 使い方 / Usage

### エージェントとして使用 / As an Agent

```python
from db import Database
from agent import GameProbabilityAgent

# Initialize database
db = Database(db_path="data/game-probability-agent.db")
await db.initialize()

# Initialize agent
agent = GameProbabilityAgent(db)
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
