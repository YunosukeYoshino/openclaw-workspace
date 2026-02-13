# 野球ドラフトエージェント

Baseball Draft Agent

## Description / 説明

ドラフト情報、有望選手データ、指名傾向を管理するエージェント

An agent for managing draft information, prospect data, and team selection trends

## Features / 機能

- ドラフト情報
- 有望選手
- 指名傾向
- データ分析

## Installation / インストール

```bash
pip install -r requirements.txt
```

## Usage / 使用方法

### Python API / Python API

```python
from baseball-draft-agent import BaseballDraftAgent

# エージェント初期化 / Initialize agent
agent = BaseballDraftAgent()

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
from baseball-draft-agent.db import BaseballDraftAgentDB

# データベース初期化 / Initialize database
db = BaseballDraftAgentDB()
db.init_database()

# エントリー挿入 / Insert entry
entry_id = db.insert_entry("タイトル", "説明")

# エントリー取得 / Get entry
entry = db.get_entry(entry_id)
```

### Discord Bot / Discordボット

```python
from baseball-draft-agent.discord import BaseballDraftAgentBot

# Bot起動 / Start bot
bot = BaseballDraftAgentBot(command_prefix="!")
bot.run("YOUR_DISCORD_TOKEN")
```

## Commands / コマンド

| Command / コマンド | Description / 説明 |
|---------------------|---------------------|
| `!draftagentadd <title> [description]` | 新しいエントリーを追加 / Add new entry |
| `!draftagentlist [limit]` | エントリー一覧を表示 / List entries |
| `!draftagentget <id>` | エントリーの詳細を表示 / Get entry details |
| `!draftagentsearch <query>` | エントリーを検索 / Search entries |
| `!draftagentstats` | 統計情報を表示 / Show statistics |
| `!draftagenthelp` | ヘルプを表示 / Show help |

## Database Schema / データベース構造

### drafts / ドラフト情報テーブル

| Column / カラム | Type / 型 | Description / 説明 |
|------------------|-----------|---------------------|
| id | INTEGER | Primary Key / 主キー |
| title | TEXT | Title / タイトル |
| description | TEXT | Description / 説明 |
| data_json | TEXT | JSON Data / JSONデータ |
| status | TEXT | Status / ステータス |
| created_at | TIMESTAMP | Created Time / 作成日時 |
| updated_at | TIMESTAMP | Updated Time / 更新日時 |

### prospects / 有望選手テーブル

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
baseball-draft-agent/
├── agent.py          # エージェント本体 / Main agent
├── db.py            # データベースモジュール / Database module
├── discord.py       # Discord Bot / Discord Bot
├── README.md        # このファイル / This file
└── requirements.txt # 依存パッケージ / Dependencies
```

## License / ライセンス

MIT License
