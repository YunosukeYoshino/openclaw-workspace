# 野球戦略分析エージェント

Baseball Strategy Analysis Agent

## Description / 説明

監督の采配、戦術分析、試合の戦略パターンを管理するエージェント

An agent for analyzing manager decisions, game tactics, and strategy patterns

## Features / 機能

- 戦術分析
- 采配評価
- 戦略パターン
- 監督比較

## Installation / インストール

```bash
pip install -r requirements.txt
```

## Usage / 使用方法

### Python API / Python API

```python
from baseball-strategy-agent import BaseballStrategyAgent

# エージェント初期化 / Initialize agent
agent = BaseballStrategyAgent()

# エントリー追加 / Add entry
entry_id = agent.add_entry("タイトル", "説明")

# エントリー取得 / Get entry
entry = agent.get_entry(entry_id)

# エントリー一覧 / List entries
entries = agent.list_entries(limit=10)

# 検索 / Search
results = agent.search_entries("検索クエリ")

# 統計情報 / Statistics
stats = agent.get_stats()
```

### Database / データベース

```python
from baseball-strategy-agent.db import BaseballStrategyAgentDB

# データベース初期化 / Initialize database
db = BaseballStrategyAgentDB()
db.init_database()

# エントリー挿入 / Insert entry
entry_id = db.insert_entry("タイトル", "説明")

# エントリー取得 / Get entry
entry = db.get_entry(entry_id)
```

### Discord Bot / Discordボット

```python
from baseball-strategy-agent.discord import BaseballStrategyAgentBot

# Bot起動 / Start bot
bot = BaseballStrategyAgentBot(command_prefix="!")
bot.run("YOUR_DISCORD_TOKEN")
```

## Commands / コマンド

| Command / コマンド | Description / 説明 |
|---------------------|---------------------|
| `!strategyagentadd <title> [description]` | 新しいエントリーを追加 / Add new entry |
| `!strategyagentlist [limit]` | エントリー一覧を表示 / List entries |
| `!strategyagentget <id>` | エントリーの詳細を表示 / Get entry details |
| `!strategyagentsearch <query>` | エントリーを検索 / Search entries |
| `!strategyagentstats` | 統計情報を表示 / Show statistics |
| `!strategyagenthelp` | ヘルプを表示 / Show help |

## Database Schema / データベース構造

### strategies / 戦略・戦術テーブル

| Column / カラム | Type / 型 | Description / 説明 |
|------------------|-----------|---------------------|
| id | INTEGER | Primary Key / 主キー |
| title | TEXT | Title / タイトル |
| description | TEXT | Description / 説明 |
| data_json | TEXT | JSON Data / JSONデータ |
| status | TEXT | Status / ステータス |
| created_at | TIMESTAMP | Created Time / 作成日時 |
| updated_at | TIMESTAMP | Updated Time / 更新日時 |

### matches / 試合・戦略紐付けテーブル

| Column / カラム | Type / 型 | Description / 説明 |
|------------------|-----------|---------------------|
| id | INTEGER | Primary Key / 主キー |
| name | TEXT | Name / 名前 |
| team | TEXT | Team / チーム |
| data_json | TEXT | JSON Data / JSONデータ |
| created_at | TIMESTAMP | Created Time / 作成日時 |
| updated_at | TIMESTAMP | Updated Time / 更新日時 |

## Project Structure / プロジェクト構造

```
baseball-strategy-agent/
├── agent.py          # エージェント本体 / Main agent
├── db.py            # データベースモジュール / Database module
├── discord.py       # Discord Bot / Discord Bot
├── README.md        # このファイル / This file
└── requirements.txt # 依存パッケージ / Dependencies
```

## License / ライセンス

MIT License
