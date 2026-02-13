# 野球ライブ予測エージェント / Baseball Live Prediction Agent

baseball-prediction-live-agent

## 概要 / Overview

試合中の勝率予測（リーグワイドのデータ活用）、得点期待値、イニングごとの得点確率、延長戦の可能性、クローザー投入タイミングの予測

Win probability prediction during games (using league-wide data), run expectancy, inning-by-inning scoring probability, extra innings possibility, closer deployment timing prediction

## 機能 / Features

- Live Win Probability
- Run Expectancy
- Scoring Probability
- Extra Innings Predict
- Closer Timing
- Real-time Updates

## 技術スタック / Tech Stack

- pandas, numpy, scikit-learn, xgboost, requests

## インストール / Installation

```bash
# Clone the repository
git clone <repository-url>
cd baseball-prediction-live-agent

# Install dependencies
pip install -r requirements.txt
```

## 使い方 / Usage

### エージェントとして使用 / As an Agent

```python
from db import Database
from agent import BaseballPredictionLiveAgent

# Initialize database
db = Database(db_path="data/baseball-prediction-live-agent.db")
await db.initialize()

# Initialize agent
agent = BaseballPredictionLiveAgent(db)
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
