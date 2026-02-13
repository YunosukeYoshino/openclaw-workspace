# ゲーム大会エージェント

Game Tournament Agent

## Description / 説明

ゲーム大会情報、大会結果、優勝者データを管理するエージェント

An agent for managing game tournaments, results, and winner data

## Features / 機能

- 大会管理
- 結果記録
- 参加者管理
- 賞金記録

## Installation / インストール

```bash
pip install -r requirements.txt
```

## Usage / 使用方法

### Python API / Python API

```python
from game-tournament-agent import GameTournamentAgent

# エージェント初期化 / Initialize agent
agent = GameTournamentAgent()

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
from game-tournament-agent.db import GameTournamentAgentDB

# データベース初期化 / Initialize database
db = GameTournamentAgentDB()
db.init_database()

# エントリー挿入 / Insert entry
entry_id = db.insert_entry("タイトル", "説明")

# エントリー取得 / Get entry
entry = db.get_entry(entry_id)
```

### Discord Bot / Discordボット

```python
from game-tournament-agent.discord import GameTournamentAgentBot

# Bot起動 / Start bot
bot = GameTournamentAgentBot(command_prefix="!")
bot.run("YOUR_DISCORD_TOKEN")
```

## Commands / コマンド

| Command / コマンド | Description / 説明 |
|---------------------|---------------------|
| `!tournamentagentadd <title> [description]` | 新しいエントリーを追加 / Add new entry |
| `!tournamentagentlist [limit]` | エントリー一覧を表示 / List entries |
| `!tournamentagentget <id>` | エントリーの詳細を表示 / Get entry details |
| `!tournamentagentsearch <query>` | エントリーを検索 / Search entries |
| `!tournamentagentstats` | 統計情報を表示 / Show statistics |
| `!tournamentagenthelp` | ヘルプを表示 / Show help |

## Database Schema / データベース構造

### tournaments / 大会テーブル

| Column / カラム | Type / 型 | Description / 説明 |
|------------------|-----------|---------------------|
| id | INTEGER | Primary Key / 主キー |
| title | TEXT | Title / タイトル |
| description | TEXT | Description / 説明 |
| data_json | TEXT | JSON Data / JSONデータ |
| status | TEXT | Status / ステータス |
| created_at | TIMESTAMP | Created Time / 作成日時 |
| updated_at | TIMESTAMP | Updated Time / 更新日時 |

### participants / 参加者テーブル

| Column / カラム | Type / 型 | Description / 説明 |
|------------------|-----------|---------------------|
| id | INTEGER | Primary Key / 主キー |
| name | TEXT | Name / 名前 |
| data_json | TEXT | JSON Data / JSONデータ |
| created_at | TIMESTAMP | Created Time / 作成日時 |
| updated_at | TIMESTAMP | Updated Time / 更新日時 |

## Project Structure / プロジェクト構造

```
game-tournament-agent/
├── agent.py          # エージェント本体 / Main agent
├── db.py            # データベースモジュール / Database module
├── discord.py       # Discord Bot / Discord Bot
├── README.md        # このファイル / This file
└── requirements.txt # 依存パッケージ / Dependencies
```

## License / ライセンス

MIT License
