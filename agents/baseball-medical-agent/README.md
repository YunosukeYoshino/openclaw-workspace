# 野球メディカルエージェント

Baseball Medical Agent

## Description / 説明

選手の怪我情報、復帰予測、メディカルデータを管理するエージェント

An agent for managing player injuries, recovery predictions, and medical data

## Features / 機能

- 怪我管理
- 復帰予測
- メディカルデータ
- 健康管理

## Installation / インストール

```bash
pip install -r requirements.txt
```

## Usage / 使用方法

### Python API / Python API

```python
from baseball-medical-agent import BaseballMedicalAgent

# エージェント初期化 / Initialize agent
agent = BaseballMedicalAgent()

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
from baseball-medical-agent.db import BaseballMedicalAgentDB

# データベース初期化 / Initialize database
db = BaseballMedicalAgentDB()
db.init_database()

# エントリー挿入 / Insert entry
entry_id = db.insert_entry("タイトル", "説明")

# エントリー取得 / Get entry
entry = db.get_entry(entry_id)
```

### Discord Bot / Discordボット

```python
from baseball-medical-agent.discord import BaseballMedicalAgentBot

# Bot起動 / Start bot
bot = BaseballMedicalAgentBot(command_prefix="!")
bot.run("YOUR_DISCORD_TOKEN")
```

## Commands / コマンド

| Command / コマンド | Description / 説明 |
|---------------------|---------------------|
| `!medicalagentadd <title> [description]` | 新しいエントリーを追加 / Add new entry |
| `!medicalagentlist [limit]` | エントリー一覧を表示 / List entries |
| `!medicalagentget <id>` | エントリーの詳細を表示 / Get entry details |
| `!medicalagentsearch <query>` | エントリーを検索 / Search entries |
| `!medicalagentstats` | 統計情報を表示 / Show statistics |
| `!medicalagenthelp` | ヘルプを表示 / Show help |

## Database Schema / データベース構造

### injuries / 怪我情報テーブル

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
baseball-medical-agent/
├── agent.py          # エージェント本体 / Main agent
├── db.py            # データベースモジュール / Database module
├── discord.py       # Discord Bot / Discord Bot
├── README.md        # このファイル / This file
└── requirements.txt # 依存パッケージ / Dependencies
```

## License / ライセンス

MIT License
