# 野球投球マッチアップエージェント / Baseball Pitch Matchup Agent

baseball-pitch-matchup-agent

## 概要 / Overview

投手 vs 打者の過去対戦成績、相性分析、投球傾向、苦手球種、ストライクゾーンの可視化、次の投球予測、最適戦略の提案

Pitcher vs batter past matchup records, compatibility analysis, pitching tendencies, weak pitches, strike zone visualization, next pitch prediction, optimal strategy suggestions

## 機能 / Features

- Matchup Analysis
- Pitching Tendencies
- Strike Zone Viz
- Weakness Detection
- Next Pitch Prediction
- Strategy Suggestions

## 技術スタック / Tech Stack

- pandas, numpy, scikit-learn, matplotlib, requests

## インストール / Installation

```bash
# Clone the repository
git clone <repository-url>
cd baseball-pitch-matchup-agent

# Install dependencies
pip install -r requirements.txt
```

## 使い方 / Usage

### エージェントとして使用 / As an Agent

```python
from db import Database
from agent import BaseballPitchMatchupAgent

# Initialize database
db = Database(db_path="data/baseball-pitch-matchup-agent.db")
await db.initialize()

# Initialize agent
agent = BaseballPitchMatchupAgent(db)
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
