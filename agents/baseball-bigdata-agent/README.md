# baseball-bigdata-agent

野球ビッグデータエージェント。大規模野球データの収集・分析。

## 概要 / Overview

**日本語:**
野球ビッグデータエージェント。大規模野球データの収集・分析。を提供するエージェント。

**English:**
An agent providing 野球ビッグデータエージェント。大規模野球データの収集・分析。.

## カテゴリ / Category

- `baseball`

## 機能 / Features

- Discord Bot 連携による対話型インターフェース
- SQLite データベースによるデータ管理
- コマンドラインからの操作

## コマンド / Commands

| コマンド | 説明 | 説明 (EN) |
|----------|------|-----------|
| `!ingest_data` | ingest_data コマンド | ingest_data command |
| `!query_data` | query_data コマンド | query_data command |
| `!data_jobs` | data_jobs コマンド | data_jobs command |
| `!data_info` | data_info コマンド | data_info command |

## インストール / Installation

```bash
cd agents/baseball-bigdata-agent
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

- **big_datasets**: id INTEGER PRIMARY KEY, name TEXT, source TEXT, size_bytes INTEGER, record_count INTEGER, schema TEXT
- **data_partitions**: id INTEGER PRIMARY KEY, dataset_id INTEGER, partition_key TEXT, value TEXT, path TEXT, FOREIGN KEY (dataset_id) REFERENCES big_datasets(id
- **data_jobs**: id INTEGER PRIMARY KEY, dataset_id INTEGER, job_type TEXT, status TEXT, started_at TIMESTAMP, completed_at TIMESTAMP, FOREIGN KEY (dataset_id) REFERENCES big_datasets(id

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

_This agent is part of OpenClaw Agents ecosystem._
