# data-lake-agent

データレイクエージェント。データレイクの管理・運用。

## 概要 / Overview

**日本語:**
データレイクエージェント。データレイクの管理・運用。を提供するエージェント。

**English:**
An agent providing データレイクエージェント。データレイクの管理・運用。.

## カテゴリ / Category

- `data`

## 機能 / Features

- Discord Bot 連携による対話型インターフェース
- SQLite データベースによるデータ管理
- コマンドラインからの操作

## コマンド / Commands

| コマンド | 説明 | 説明 (EN) |
|----------|------|-----------|
| `!ingest` | ingest コマンド | ingest command |
| `!list_datasets` | list_datasets コマンド | list_datasets command |
| `!dataset_info` | dataset_info コマンド | dataset_info command |
| `!query_lake` | query_lake コマンド | query_lake command |

## インストール / Installation

```bash
cd agents/data-lake-agent
pip install -r requirements.txt
```

## 使用方法 / Usage

### エージェントの実行 / Run Agent

```bash
python agent.py
```

### Discord Bot の起動 / Start Discord Bot

```bash
export DISCORD_TOKEN="your_bot_token"
python discord.py
```

## データベース / Database

データベースファイル: `data.db`

### テーブル / Tables

- **datasets**: id INTEGER PRIMARY KEY, name TEXT, format TEXT, size_bytes INTEGER, path TEXT, ingested_at TIMESTAMP
- **partitions**: id INTEGER PRIMARY KEY, dataset_id INTEGER, partition_key TEXT, value TEXT, path TEXT, FOREIGN KEY (dataset_id) REFERENCES datasets(id
- **schemas**: id INTEGER PRIMARY KEY, dataset_id INTEGER, schema JSON, version INTEGER, FOREIGN KEY (dataset_id) REFERENCES datasets(id

## 開発 / Development

```bash
# テスト
python -m pytest

# フォーマット
black agent.py db.py discord.py
```

## ライセンス / License

MIT License

---

_This agent is part of the OpenClaw Agents ecosystem._
