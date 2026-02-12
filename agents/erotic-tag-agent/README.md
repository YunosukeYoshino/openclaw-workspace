# erotic-tag-agent

えっちなコンテンツのタグ付け・検索機能を提供するエージェント

🏷️

## 機能

- エントリーの追加・編集・削除
- キーワード検索
- タグによるフィルタリング
- 評価機能
- 統計情報の表示
- Discord Botからの操作

## インストール

```bash
pip install -r requirements.txt
```

## 使い方

### Python API

```python
from db import EroticTagAgentDB

# データベース初期化
db = EroticTagAgentDB()
db.initialize()

# エントリー追加
db.add_entry(
    title="サンプル",
    description="これはサンプルです",
    source="test",
    tags="サンプル,テスト"
)

# エントリー検索
entries = db.search_entries("サンプル")
for entry in entries:
    print(str(entry['title']) + ": " + str(entry['description']))

# 統計情報
stats = db.get_stats()
print("総エントリー数: " + str(stats['total_entries']))
```

### Discord Bot

```bash
export DISCORD_TOKEN="your_bot_token"
python discord.py
```

## Discordコマンド

| コマンド | 説明 |
|----------|------|
| `!追加 <タイトル> [説明]` | エントリーを追加 |
| `!検索 <キーワード>` | キーワードで検索 |
| `!一覧 [件数]` | エントリー一覧を表示 |
| `!詳細 <ID>` | 指定IDの詳細を表示 |
| `!タグ検索 <タグ名>` | タグで検索 |
| `!統計` | 統計情報を表示 |
| `!削除 <ID>` | エントリーを削除 |
| `!ヘルプ` | ヘルプを表示 |

## データベース構造

### entriesテーブル

| カラム | 型 | 説明 |
|--------|------|------|
| id | INTEGER | 主キー |
| title | TEXT | タイトル |
| description | TEXT | 説明 |
| source | TEXT | ソース |
| url | TEXT | URL |
| tags | TEXT | タグ（カンマ区切り） |
| rating | INTEGER | 評価 (0-5) |
| created_at | TIMESTAMP | 作成日時 |
| updated_at | TIMESTAMP | 更新日時 |

### tagsテーブル

| カラム | 型 | 説明 |
|--------|------|------|
| id | INTEGER | 主キー |
| name | TEXT | タグ名 |
| count | INTEGER | 使用回数 |
| created_at | TIMESTAMP | 作成日時 |

## ライセンス

MIT

---

# erotic-tag-agent (English)

えっちなコンテンツのタグ付け・検索機能を提供するAgent

🏷️

## Features

- Add, edit, and delete entries
- Keyword search
- Filter by tags
- Rating system
- Statistics display
- Discord Bot control

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Python API

```python
from db import EroticTagAgentDB

# Initialize database
db = EroticTagAgentDB()
db.initialize()

# Add entry
db.add_entry(
    title="Sample",
    description="This is a sample",
    source="test",
    tags="sample,test"
)

# Search entries
entries = db.search_entries("sample")
for entry in entries:
    print(str(entry['title']) + ": " + str(entry['description']))

# Statistics
stats = db.get_stats()
print("Total entries: " + str(stats['total_entries']))
```

### Discord Bot

```bash
export DISCORD_TOKEN="your_bot_token"
python discord.py
```

## Discord Commands

| Command | Description |
|---------|-------------|
| `!add <title> [description]` | Add an entry |
| `!search <keyword>` | Search by keyword |
| `!list [count]` | List entries |
| `!detail <id>` | Show entry details |
| `!tag <tagname>` | Search by tag |
| `!stats` | Show statistics |
| `!delete <id>` | Delete an entry |
| `!help` | Show help |

## License

MIT
