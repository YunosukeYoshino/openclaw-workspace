# えっちコミュニティエージェント

Erotic Community Agent

## Description / 説明

えっちコミュニティ、フォーラム、SNSグループ情報を管理するエージェント

An agent for managing erotic communities, forums, and social groups

## Features / 機能

- コミュニティ管理
- メンバー追跡
- 議論管理
- 通知機能

## Installation / インストール

```bash
pip install -r requirements.txt
```

## Usage / 使用方法

### Python API / Python API

```python
from erotic-community-agent import EroticCommunityAgent

# エージェント初期化 / Initialize agent
agent = EroticCommunityAgent()

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
from erotic-community-agent.db import EroticCommunityAgentDB

# データベース初期化 / Initialize database
db = EroticCommunityAgentDB()
db.init_database()

# エントリー挿入 / Insert entry
entry_id = db.insert_entry("タイトル", "説明")

# エントリー取得 / Get entry
entry = db.get_entry(entry_id)
```

### Discord Bot / Discordボット

```python
from erotic-community-agent.discord import EroticCommunityAgentBot

# Bot起動 / Start bot
bot = EroticCommunityAgentBot(command_prefix="!")
bot.run("YOUR_DISCORD_TOKEN")
```

## Commands / コマンド

| Command / コマンド | Description / 説明 |
|---------------------|---------------------|
| `!communityagentadd <title> [description]` | 新しいエントリーを追加 / Add new entry |
| `!communityagentlist [limit]` | エントリー一覧を表示 / List entries |
| `!communityagentget <id>` | エントリーの詳細を表示 / Get entry details |
| `!communityagentsearch <query>` | エントリーを検索 / Search entries |
| `!communityagentstats` | 統計情報を表示 / Show statistics |
| `!communityagenthelp` | ヘルプを表示 / Show help |

## Database Schema / データベース構造

### communities / コミュニティテーブル

| Column / カラム | Type / 型 | Description / 説明 |
|------------------|-----------|---------------------|
| id | INTEGER | Primary Key / 主キー |
| title | TEXT | Title / タイトル |
| description | TEXT | Description / 説明 |
| data_json | TEXT | JSON Data / JSONデータ |
| status | TEXT | Status / ステータス |
| created_at | TIMESTAMP | Created Time / 作成日時 |
| updated_at | TIMESTAMP | Updated Time / 更新日時 |

### members / メンバーテーブル

| Column / カラム | Type / 型 | Description / 説明 |
|------------------|-----------|---------------------|
| id | INTEGER | Primary Key / 主キー |
| name | TEXT | Name / 名前 |
| data_json | TEXT | JSON Data / JSONデータ |
| created_at | TIMESTAMP | Created Time / 作成日時 |
| updated_at | TIMESTAMP | Updated Time / 更新日時 |

## Project Structure / プロジェクト構造

```
erotic-community-agent/
├── agent.py          # エージェント本体 / Main agent
├── db.py            # データベースモジュール / Database module
├── discord.py       # Discord Bot / Discord Bot
├── README.md        # このファイル / This file
└── requirements.txt # 依存パッケージ / Dependencies
```

## License / ライセンス

MIT License
