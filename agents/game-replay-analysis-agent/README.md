# ゲームリプレイ分析エージェント / Game Replay Analysis Agent

game-replay-analysis-agent

## 概要 / Overview

リプレイファイルの解析、重要局面の抽出、プレイヤー行動のパターン認識、改善提案、プロ選手との比較、スキルギャップの特定

Parse replay files, extract key moments, pattern recognition for player behavior, improvement suggestions, compare with pros, identify skill gaps

## 機能 / Features

- Replay Parsing
- Key Moments
- Pattern Recognition
- Improvement Suggest
- Pro Comparison
- Skill Gap Analysis

## 技術スタック / Tech Stack

- pandas, numpy, scikit-learn, matplotlib, opencv-python

## インストール / Installation

```bash
# Clone the repository
git clone <repository-url>
cd game-replay-analysis-agent

# Install dependencies
pip install -r requirements.txt
```

## 使い方 / Usage

### エージェントとして使用 / As an Agent

```python
from db import Database
from agent import GameReplayAnalysisAgent

# Initialize database
db = Database(db_path="data/game-replay-analysis-agent.db")
await db.initialize()

# Initialize agent
agent = GameReplayAnalysisAgent(db)
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
