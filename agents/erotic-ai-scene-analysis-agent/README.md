# えっちシーンAI分析エージェント / Erotic AI Scene Analysis Agent

erotic-ai-scene-analysis-agent

## 概要 / Overview

シーンの分類、タグ付け、重要要素の抽出、シチュエーション、プレイスタイルの分類、シーン間の類似度計算、関連シーンの提案

Scene classification, tagging, key element extraction, situation and play style classification, scene similarity calculation, related scene suggestions

## 機能 / Features

- Scene Classification
- Auto Tagging
- Key Elements
- Situation Analysis
- Similarity Search
- Related Scenes

## 技術スタック / Tech Stack

- pandas, numpy, scikit-learn, torch, transformers

## インストール / Installation

```bash
# Clone the repository
git clone <repository-url>
cd erotic-ai-scene-analysis-agent

# Install dependencies
pip install -r requirements.txt
```

## 使い方 / Usage

### エージェントとして使用 / As an Agent

```python
from db import Database
from agent import EroticAiSceneAnalysisAgent

# Initialize database
db = Database(db_path="data/erotic-ai-scene-analysis-agent.db")
await db.initialize()

# Initialize agent
agent = EroticAiSceneAnalysisAgent(db)
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
