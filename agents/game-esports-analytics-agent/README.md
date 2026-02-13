# ゲームeスポーツ分析エージェント / Game Esports Analytics Agent

game-esports-analytics-agent

## 概要 / Overview

プロレベルのプレイ分析、メタの追跡、パッチによる環境変化の影響分析、アマチュア・プロのギャップ分析、上達のヒント

Pro-level play analysis, meta tracking, analyze patch impact on meta, amateur-pro gap analysis, improvement tips

## 機能 / Features

- Pro Play Analysis
- Meta Tracking
- Patch Impact
- Gap Analysis
- Improvement Tips
- Trend Reports

## 技術スタック / Tech Stack

- pandas, numpy, scikit-learn, matplotlib, seaborn

## インストール / Installation

```bash
# Clone the repository
git clone <repository-url>
cd game-esports-analytics-agent

# Install dependencies
pip install -r requirements.txt
```

## 使い方 / Usage

### エージェントとして使用 / As an Agent

```python
from db import Database
from agent import GameEsportsAnalyticsAgent

# Initialize database
db = Database(db_path="data/game-esports-analytics-agent.db")
await db.initialize()

# Initialize agent
agent = GameEsportsAnalyticsAgent(db)
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
