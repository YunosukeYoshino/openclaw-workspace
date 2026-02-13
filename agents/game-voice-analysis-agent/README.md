# {agent_name}

{japanese_name} - {description}

## Description / 概要

{full_description}

## Features / 機能

{features}

## Installation / インストール

```bash
pip install -r requirements.txt
```

## Usage / 使用方法

```python
from {agent_name} import {class_name}

# Create an agent / エージェントを作成
agent = {class_name}()

# Add an entry / エントリーを追加
agent.add_entry("Title", "Content")

# List entries / エントリーを一覧
entries = agent.list_entries()
```

## Database Schema / データベーススキーマ

```sql
CREATE TABLE {table_name} (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    {content_field} TEXT NOT NULL,
    commentator TEXT,
    game_name TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    tags TEXT
);
```

## Discord Commands / Discordコマンド

- `!{discord_prefix}add <title> <content>` - Add entry / エントリーを追加
- `!{discord_prefix}list [limit]` - List entries / エントリーを一覧
- `!{discord_prefix}search <query>` - Search entries / エントリーを検索

## Requirements / 要件

- Python 3.8+
- discord.py
- sqlite3

## License / ライセンス

MIT
