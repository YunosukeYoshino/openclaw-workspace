# えっちAIキュレーションエージェント / Erotic AI Curation Agent

erotic-ai-curation-agent

## 概要 / Overview

AIによるコレクションの自動キュレーション、テーマ別、ムード別、時間帯別のプレイリスト作成、機械学習によるトレンド予測、先行コンテンツの提案

AI-powered collection curation, create playlists by theme, mood, time of day, ML-based trend prediction, suggest trending content

## 機能 / Features

- Auto Curation
- Theme Playlists
- Mood Matching
- Trend Prediction
- Trending Content
- Personalized List

## 技術スタック / Tech Stack

- pandas, numpy, scikit-learn, torch, recommenders

## インストール / Installation

```bash
# Clone the repository
git clone <repository-url>
cd erotic-ai-curation-agent

# Install dependencies
pip install -r requirements.txt
```

## 使い方 / Usage

### エージェントとして使用 / As an Agent

```python
from db import Database
from agent import EroticAiCurationAgent

# Initialize database
db = Database(db_path="data/erotic-ai-curation-agent.db")
await db.initialize()

# Initialize agent
agent = EroticAiCurationAgent(db)
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
