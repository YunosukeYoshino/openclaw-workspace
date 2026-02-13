# 野球ドラフト候補エージェント / Baseball Draft Candidate Agent

baseball-draft-candidate-agent

## 概要 / Overview

ドラフト候補選手のプロフィール、統計、評価、大学、高校、社会人選手の情報収集、チームのニーズに応じた候補選手の提案

Draft candidate profiles, statistics, evaluations, collect info on college, high school, industrial league players, suggest candidates based on team needs

## 機能 / Features

- Candidate Profiles
- Stats Tracking
- Evaluations
- Multi-Source Data
- Team Matching
- Draft Rankings

## 技術スタック / Tech Stack

- pandas, numpy, requests, beautifulsoup4, scikit-learn

## インストール / Installation

```bash
# Clone the repository
git clone <repository-url>
cd baseball-draft-candidate-agent

# Install dependencies
pip install -r requirements.txt
```

## 使い方 / Usage

### エージェントとして使用 / As an Agent

```python
from db import Database
from agent import BaseballDraftCandidateAgent

# Initialize database
db = Database(db_path="data/baseball-draft-candidate-agent.db")
await db.initialize()

# Initialize agent
agent = BaseballDraftCandidateAgent(db)
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
