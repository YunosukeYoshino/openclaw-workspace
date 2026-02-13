# ゲームマーケットプレイスエージェント

Game Marketplace Agent

## Description / 説明

ゲーム内マーケット、アイテム取引、価格推移を管理するエージェント

An agent for managing in-game marketplaces, item trading, and price trends

## Features / 機能

- マーケット管理
- 価格追跡
- 取引記録
- トレンド分析

## Installation / インストール

```bash
pip install -r requirements.txt
```

## Usage / 使用方法

### Python API / Python API

```python
from game-marketplace-agent import GameMarketplaceAgent

# エージェント初期化 / Initialize agent
agent = GameMarketplaceAgent()

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
from game-marketplace-agent.db import GameMarketplaceAgentDB

# データベース初期化 / Initialize database
db = GameMarketplaceAgentDB()
db.init_database()

# エントリー挿入 / Insert entry
entry_id = db.insert_entry("タイトル", "説明")

# エントリー取得 / Get entry
entry = db.get_entry(entry_id)
```

### Discord Bot / Discordボット

```python
from game-marketplace-agent.discord import GameMarketplaceAgentBot

# Bot起動 / Start bot
bot = GameMarketplaceAgentBot(command_prefix="!")
bot.run("YOUR_DISCORD_TOKEN")
```

## Commands / コマンド

| Command / コマンド | Description / 説明 |
|---------------------|---------------------|
| `!marketplaceagentadd <title> [description]` | 新しいエントリーを追加 / Add new entry |
| `!marketplaceagentlist [limit]` | エントリー一覧を表示 / List entries |
| `!marketplaceagentget <id>` | エントリーの詳細を表示 / Get entry details |
| `!marketplaceagentsearch <query>` | エントリーを検索 / Search entries |
| `!marketplaceagentstats` | 統計情報を表示 / Show statistics |
| `!marketplaceagenthelp` | ヘルプを表示 / Show help |

## Database Schema / データベース構造

### marketplace / マーケットテーブル

| Column / カラム | Type / 型 | Description / 説明 |
|------------------|-----------|---------------------|
| id | INTEGER | Primary Key / 主キー |
| title | TEXT | Title / タイトル |
| description | TEXT | Description / 説明 |
| data_json | TEXT | JSON Data / JSONデータ |
| status | TEXT | Status / ステータス |
| created_at | TIMESTAMP | Created Time / 作成日時 |
| updated_at | TIMESTAMP | Updated Time / 更新日時 |

### items / アイテムテーブル

| Column / カラム | Type / 型 | Description / 説明 |
|------------------|-----------|---------------------|
| id | INTEGER | Primary Key / 主キー |
| name | TEXT | Name / 名前 |
| data_json | TEXT | JSON Data / JSONデータ |
| created_at | TIMESTAMP | Created Time / 作成日時 |
| updated_at | TIMESTAMP | Updated Time / 更新日時 |

## Project Structure / プロジェクト構造

```
game-marketplace-agent/
├── agent.py          # エージェント本体 / Main agent
├── db.py            # データベースモジュール / Database module
├── discord.py       # Discord Bot / Discord Bot
├── README.md        # このファイル / This file
└── requirements.txt # 依存パッケージ / Dependencies
```

## License / ライセンス

MIT License
