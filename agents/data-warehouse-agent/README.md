# data-warehouse-agent

データウェアハウスエージェント。データウェアハウスの管理・クエリ。

## 概要 / Overview

**日本語:**
データウェアハウスエージェント。データウェアハウスの管理・クエリ。を提供するエージェント。

**English:**
An agent providing データウェアハウスエージェント。データウェアハウスの管理・クエリ。.

## カテゴリ / Category

- `data`

## 機能 / Features

- Discord Bot 連携による対話型インターフェース
- SQLite データベースによるデータ管理
- コマンドラインからの操作

## コマンド / Commands

| コマンド | 説明 | 説明 (EN) |
|----------|------|-----------|
| `!create_fact` | create_fact コマンド | create_fact command |
| `!add_dimension` | add_dimension コマンド | add_dimension command |
| `!run_etl` | run_etl コマンド | run_etl command |
| `!warehouse_status` | warehouse_status コマンド | warehouse_status command |

## インストール / Installation

```bash
cd agents/data-warehouse-agent
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

- **fact_tables**: id INTEGER PRIMARY KEY, name TEXT, grain TEXT, source TEXT, rows INTEGER
- **dimensions**: id INTEGER PRIMARY KEY, name TEXT, key_columns TEXT, attributes JSON
- **etl_jobs**: id INTEGER PRIMARY KEY, name TEXT, source TEXT, target TEXT, status TEXT, last_run TIMESTAMP, next_run TIMESTAMP

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
