# ゲームプロ選手エージェント / Game Pro Player Agent

game-pro-player-agent

## 概要 / Overview

プロ選手のプロフィール、成績、プレイスタイル、チャンピオン/キャラクターの得意・苦手、ランキング、賞金、キャリアの追跡

Pro player profile, performance, play style, champ/character strengths/weaknesses, ranking, prize money, career tracking

## 機能 / Features

- Player Profiles
- Performance Stats
- Play Style
- Champ Mastery
- Rankings
- Prize Tracking

## 技術スタック / Tech Stack

- pandas, numpy, requests, scikit-learn, matplotlib

## インストール / Installation

```bash
# Clone the repository
git clone <repository-url>
cd game-pro-player-agent

# Install dependencies
pip install -r requirements.txt
```

## 使い方 / Usage

### エージェントとして使用 / As an Agent

```python
from db import Database
from agent import GameProPlayerAgent

# Initialize database
db = Database(db_path="data/game-pro-player-agent.db")
await db.initialize()

# Initialize agent
agent = GameProPlayerAgent(db)
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
