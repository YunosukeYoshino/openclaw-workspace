# 野球スカウトレポートエージェント / Baseball Scout Report Agent

baseball-scout-report-agent

## 概要 / Overview

スカウトリポートの統合・管理、複数スカウトの評価の統合、バイアス補正、選手比較、プロジェクション、ツール評価

Integrate and manage scout reports, aggregate multiple scout evaluations, bias correction, player comparison, projection, tool grading

## 機能 / Features

- Report Mgmt
- Multi-Scout Agg
- Bias Correction
- Player Compare
- Projection
- Tool Grading

## 技術スタック / Tech Stack

- pandas, numpy, scikit-learn, matplotlib, seaborn

## インストール / Installation

```bash
# Clone the repository
git clone <repository-url>
cd baseball-scout-report-agent

# Install dependencies
pip install -r requirements.txt
```

## 使い方 / Usage

### エージェントとして使用 / As an Agent

```python
from db import Database
from agent import BaseballScoutReportAgent

# Initialize database
db = Database(db_path="data/baseball-scout-report-agent.db")
await db.initialize()

# Initialize agent
agent = BaseballScoutReportAgent(db)
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
