# ゲームイベントエージェント

Game Event Agent

## Description / 説明

ゲーム内イベント、期間限定イベント、シーズンイベントを管理するエージェント

An agent for managing in-game events, limited-time events, and seasonal events

## Features / 機能

- イベント管理
- 報酬追跡
- 期間設定
- 参加記録

## Installation / インストール

```bash
pip install -r requirements.txt
```

## Usage / 使用方法

### Python API / Python API

```python
from game-event-agent import GameEventAgent

# エージェント初期化 / Initialize agent
agent = GameEventAgent()

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
from game-event-agent.db import GameEventAgentDB

# データベース初期化 / Initialize database
db = GameEventAgentDB()
db.init_database()

# エントリー挿入 / Insert entry
entry_id = db.insert_entry("タイトル", "説明")

# エントリー取得 / Get entry
entry = db.get_entry(entry_id)
```

### Discord Bot / Discordボット

```python
from game-event-agent.discord import GameEventAgentBot

# Bot起動 / Start bot
bot = GameEventAgentBot(command_prefix="!")
bot.run("YOUR_DISCORD_TOKEN")
```

## Commands / コマンド

| Command / コマンド | Description / 説明 |
|---------------------|---------------------|
| `!eventagentadd <title> [description]` | 新しいエントリーを追加 / Add new entry |
| `!eventagentlist [limit]` | エントリー一覧を表示 / List entries |
| `!eventagentget <id>` | エントリーの詳細を表示 / Get entry details |
| `!eventagentsearch <query>` | エントリーを検索 / Search entries |
| `!eventagentstats` | 統計情報を表示 / Show statistics |
| `!eventagenthelp` | ヘルプを表示 / Show help |

## Database Schema / データベース構造

### events / イベントテーブル

| Column / カラム | Type / 型 | Description / 説明 |
|------------------|-----------|---------------------|
| id | INTEGER | Primary Key / 主キー |
| title | TEXT | Title / タイトル |
| description | TEXT | Description / 説明 |
| data_json | TEXT | JSON Data / JSONデータ |
| status | TEXT | Status / ステータス |
| created_at | TIMESTAMP | Created Time / 作成日時 |
| updated_at | TIMESTAMP | Updated Time / 更新日時 |

### rewards / 報酬テーブル

| Column / カラム | Type / 型 | Description / 説明 |
|------------------|-----------|---------------------|
| id | INTEGER | Primary Key / 主キー |
| name | TEXT | Name / 名前 |
| data_json | TEXT | JSON Data / JSONデータ |
| created_at | TIMESTAMP | Created Time / 作成日時 |
| updated_at | TIMESTAMP | Updated Time / 更新日時 |

## Project Structure / プロジェクト構造

```
game-event-agent/
├── agent.py          # エージェント本体 / Main agent
├── db.py            # データベースモジュール / Database module
├── discord.py       # Discord Bot / Discord Bot
├── README.md        # このファイル / This file
└── requirements.txt # 依存パッケージ / Dependencies
```

## License / ライセンス

MIT License
