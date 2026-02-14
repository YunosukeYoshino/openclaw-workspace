# data-lakehouse-agent

データレイクハウスエージェント。データレイクハウスアーキテクチャの管理。

## 概要 / Overview

**日本語:**
データレイクハウスエージェント。データレイクハウスアーキテクチャの管理。を提供するエージェント。

**English:**
An agent providing データレイクハウスエージェント。データレイクハウスアーキテクチャの管理。.

## カテゴリ / Category

- `data`

## 機能 / Features

- Discord Bot 連携による対話型インターフェース
- SQLite データベースによるデータ管理
- コマンドラインからの操作

## コマンド / Commands

| コマンド | 説明 | 説明 (EN) |
|----------|------|-----------|
| `!create_table` | create_table コマンド | create_table command |
| `!zones` | zones コマンド | zones command |
| `!table_lineage` | table_lineage コマンド | table_lineage command |
| `!query_lakehouse` | query_lakehouse コマンド | query_lakehouse command |

## インストール / Installation

```bash
cd agents/data-lakehouse-agent
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

- **tables**: id INTEGER PRIMARY KEY, name TEXT, format TEXT, location TEXT, properties JSON
- **zones**: id INTEGER PRIMARY KEY, name TEXT, type TEXT, path TEXT, description TEXT
- **table_lineage**: id INTEGER PRIMARY KEY, source_table INTEGER, target_table INTEGER, transformation TEXT, FOREIGN KEY (source_table) REFERENCES tables(id), FOREIGN KEY (target_table) REFERENCES tables(id

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
