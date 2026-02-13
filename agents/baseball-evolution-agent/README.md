# 野球戦術・ルール進化エージェント / Baseball Evolution Agent

baseball-evolution-agent

## 概要 / Overview

野球戦術の歴史的進化（死球打法、シフト等）の追跡、ルール変更の影響分析、時代ごとのプレイスタイル比較、未来の戦術・ルールの予測・提案

Track historical evolution of tactics (sacrifice bunt, shift), analyze rule change impacts, compare play styles across eras, predict future tactics and rules

## 機能 / Features

- Tactic Evolution Tracking
- Rule Change Analysis
- Era Comparison
- Future Prediction
- Trend Analysis
- Historical Search

## 技術スタック / Tech Stack

- pandas, numpy, matplotlib, seaborn, scikit-learn

## インストール / Installation

```bash
# Clone the repository
git clone <repository-url>
cd baseball-evolution-agent

# Install dependencies
pip install -r requirements.txt
```

## 使い方 / Usage

### エージェントとして使用 / As an Agent

```python
from db import Database
from agent import BaseballEvolutionAgent

# Initialize database
db = Database(db_path="data/baseball-evolution-agent.db")
await db.initialize()

# Initialize agent
agent = BaseballEvolutionAgent(db)
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
