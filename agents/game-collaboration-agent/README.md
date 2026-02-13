# ゲームコラボエージェント

Game Collaboration Agent

## Description / 説明

ゲームコラボイベント、コラボキャラ、限定アイテムを管理するエージェント

An agent for managing game collaborations, collab characters, and limited items

## Features / 機能

- コラボ管理
- キャラ追跡
- 限定アイテム
- 履歴記録

## Installation / インストール

```bash
pip install -r requirements.txt
```

## Usage / 使用方法

### Python API / Python API

```python
from game-collaboration-agent import GameCollaborationAgent

# エージェント初期化 / Initialize agent
agent = GameCollaborationAgent()

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
from game-collaboration-agent.db import GameCollaborationAgentDB

# データベース初期化 / Initialize database
db = GameCollaborationAgentDB()
db.init_database()

# エントリー挿入 / Insert entry
entry_id = db.insert_entry("タイトル", "説明")

# エントリー取得 / Get entry
entry = db.get_entry(entry_id)
```

### Discord Bot / Discordボット

```python
from game-collaboration-agent.discord import GameCollaborationAgentBot

# Bot起動 / Start bot
bot = GameCollaborationAgentBot(command_prefix="!")
bot.run("YOUR_DISCORD_TOKEN")
```

## Commands / コマンド

| Command / コマンド | Description / 説明 |
|---------------------|---------------------|
| `!collaborationagentadd <title> [description]` | 新しいエントリーを追加 / Add new entry |
| `!collaborationagentlist [limit]` | エントリー一覧を表示 / List entries |
| `!collaborationagentget <id>` | エントリーの詳細を表示 / Get entry details |
| `!collaborationagentsearch <query>` | エントリーを検索 / Search entries |
| `!collaborationagentstats` | 統計情報を表示 / Show statistics |
| `!collaborationagenthelp` | ヘルプを表示 / Show help |

## Database Schema / データベース構造

### collaborations / コラボテーブル

| Column / カラム | Type / 型 | Description / 説明 |
|------------------|-----------|---------------------|
| id | INTEGER | Primary Key / 主キー |
| title | TEXT | Title / タイトル |
| description | TEXT | Description / 説明 |
| data_json | TEXT | JSON Data / JSONデータ |
| status | TEXT | Status / ステータス |
| created_at | TIMESTAMP | Created Time / 作成日時 |
| updated_at | TIMESTAMP | Updated Time / 更新日時 |

### characters / キャラクターテーブル

| Column / カラム | Type / 型 | Description / 説明 |
|------------------|-----------|---------------------|
| id | INTEGER | Primary Key / 主キー |
| name | TEXT | Name / 名前 |
| data_json | TEXT | JSON Data / JSONデータ |
| created_at | TIMESTAMP | Created Time / 作成日時 |
| updated_at | TIMESTAMP | Updated Time / 更新日時 |

## Project Structure / プロジェクト構造

```
game-collaboration-agent/
├── agent.py          # エージェント本体 / Main agent
├── db.py            # データベースモジュール / Database module
├── discord.py       # Discord Bot / Discord Bot
├── README.md        # このファイル / This file
└── requirements.txt # 依存パッケージ / Dependencies
```

## License / ライセンス

MIT License
