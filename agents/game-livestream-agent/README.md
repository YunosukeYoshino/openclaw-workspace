# ゲームライブ配信エージェント

Game Livestream Agent

## Description / 説明

ゲームのライブ配信情報、配信スケジュール、人気配信者を管理するエージェント

An agent for managing game livestream info, schedules, and popular streamers

## Features / 機能

- 配信管理
- スケジュール
- 配信者管理
- 配信履歴

## Installation / インストール

```bash
pip install -r requirements.txt
```

## Usage / 使用方法

### Python API / Python API

```python
from game-livestream-agent import GameLivestreamAgent

# エージェント初期化 / Initialize agent
agent = GameLivestreamAgent()

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
from game-livestream-agent.db import GameLivestreamAgentDB

# データベース初期化 / Initialize database
db = GameLivestreamAgentDB()
db.init_database()

# エントリー挿入 / Insert entry
entry_id = db.insert_entry("タイトル", "説明")

# エントリー取得 / Get entry
entry = db.get_entry(entry_id)
```

### Discord Bot / Discordボット

```python
from game-livestream-agent.discord import GameLivestreamAgentBot

# Bot起動 / Start bot
bot = GameLivestreamAgentBot(command_prefix="!")
bot.run("YOUR_DISCORD_TOKEN")
```

## Commands / コマンド

| Command / コマンド | Description / 説明 |
|---------------------|---------------------|
| `!livestreamagentadd <title> [description]` | 新しいエントリーを追加 / Add new entry |
| `!livestreamagentlist [limit]` | エントリー一覧を表示 / List entries |
| `!livestreamagentget <id>` | エントリーの詳細を表示 / Get entry details |
| `!livestreamagentsearch <query>` | エントリーを検索 / Search entries |
| `!livestreamagentstats` | 統計情報を表示 / Show statistics |
| `!livestreamagenthelp` | ヘルプを表示 / Show help |

## Database Schema / データベース構造

### livestreams / ライブ配信テーブル

| Column / カラム | Type / 型 | Description / 説明 |
|------------------|-----------|---------------------|
| id | INTEGER | Primary Key / 主キー |
| title | TEXT | Title / タイトル |
| description | TEXT | Description / 説明 |
| data_json | TEXT | JSON Data / JSONデータ |
| status | TEXT | Status / ステータス |
| created_at | TIMESTAMP | Created Time / 作成日時 |
| updated_at | TIMESTAMP | Updated Time / 更新日時 |

### streamers / 配信者テーブル

| Column / カラム | Type / 型 | Description / 説明 |
|------------------|-----------|---------------------|
| id | INTEGER | Primary Key / 主キー |
| name | TEXT | Name / 名前 |
| data_json | TEXT | JSON Data / JSONデータ |
| created_at | TIMESTAMP | Created Time / 作成日時 |
| updated_at | TIMESTAMP | Updated Time / 更新日時 |

## Project Structure / プロジェクト構造

```
game-livestream-agent/
├── agent.py          # エージェント本体 / Main agent
├── db.py            # データベースモジュール / Database module
├── discord.py       # Discord Bot / Discord Bot
├── README.md        # このファイル / This file
└── requirements.txt # 依存パッケージ / Dependencies
```

## License / ライセンス

MIT License
