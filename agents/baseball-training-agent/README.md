# 野球トレーニングエージェント

Baseball Training Agent

## Description / 説明

選手のトレーニング記録、フィジカルデータ、練習メニューを管理するエージェント

An agent for managing player training records, physical data, and practice menus

## Features / 機能

- トレーニング記録
- フィジカル管理
- 練習メニュー
- 進捗追跡

## Installation / インストール

```bash
pip install -r requirements.txt
```

## Usage / 使用方法

### Python API / Python API

```python
from baseball-training-agent import BaseballTrainingAgent

# エージェント初期化 / Initialize agent
agent = BaseballTrainingAgent()

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
from baseball-training-agent.db import BaseballTrainingAgentDB

# データベース初期化 / Initialize database
db = BaseballTrainingAgentDB()
db.init_database()

# エントリー挿入 / Insert entry
entry_id = db.insert_entry("タイトル", "説明")

# エントリー取得 / Get entry
entry = db.get_entry(entry_id)
```

### Discord Bot / Discordボット

```python
from baseball-training-agent.discord import BaseballTrainingAgentBot

# Bot起動 / Start bot
bot = BaseballTrainingAgentBot(command_prefix="!")
bot.run("YOUR_DISCORD_TOKEN")
```

## Commands / コマンド

| Command / コマンド | Description / 説明 |
|---------------------|---------------------|
| `!trainingagentadd <title> [description]` | 新しいエントリーを追加 / Add new entry |
| `!trainingagentlist [limit]` | エントリー一覧を表示 / List entries |
| `!trainingagentget <id>` | エントリーの詳細を表示 / Get entry details |
| `!trainingagentsearch <query>` | エントリーを検索 / Search entries |
| `!trainingagentstats` | 統計情報を表示 / Show statistics |
| `!trainingagenthelp` | ヘルプを表示 / Show help |

## Database Schema / データベース構造

### training_sessions / トレーニングセッションワーブル

| Column / カラム | Type / 型 | Description / 説明 |
|------------------|-----------|---------------------|
| id | INTEGER | Primary Key / 主キー |
| title | TEXT | Title / タイトル |
| description | TEXT | Description / 説明 |
| data_json | TEXT | JSON Data / JSONデータ |
| status | TEXT | Status / ステータス |
| created_at | TIMESTAMP | Created Time / 作成日時 |
| updated_at | TIMESTAMP | Updated Time / 更新日時 |

### players / 選手テーブル

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
baseball-training-agent/
├── agent.py          # エージェント本体 / Main agent
├── db.py            # データベースモジュール / Database module
├── discord.py       # Discord Bot / Discord Bot
├── README.md        # このファイル / This file
└── requirements.txt # 依存パッケージ / Dependencies
```

## License / ライセンス

MIT License
