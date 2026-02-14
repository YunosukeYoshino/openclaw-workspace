# baseball-data-science-platform-agent

野球データサイエンスプラットフォームエージェント。野球データサイエンスのための統合プラットフォーム。

## 概要 / Overview

**日本語:**
野球データサイエンスプラットフォームエージェント。野球データサイエンスのための統合プラットフォーム。を提供するエージェント。

**English:**
An agent providing 野球データサイエンスプラットフォームエージェント。野球データサイエンスのための統合プラットフォーム。.

## カテゴリ / Category

- `baseball`

## 機能 / Features

- Discord Bot 連携による対話型インターフェース
- SQLite データベースによるデータ管理
- コマンドラインからの操作

## コマンド / Commands

| コマンド | 説明 | 説明 (EN) |
|----------|------|-----------|
| `!create_notebook` | create_notebook コマンド | create_notebook command |
| `!run_experiment` | run_experiment コマンド | run_experiment command |
| `!list_models` | list_models コマンド | list_models command |
| `!platform_status` | platform_status コマンド | platform_status command |

## インストール / Installation

```bash
cd agents/baseball-data-science-platform-agent
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

- **notebooks**: id INTEGER PRIMARY KEY, title TEXT, author TEXT, code TEXT, created_at TIMESTAMP, updated_at TIMESTAMP
- **experiments**: id INTEGER PRIMARY KEY, name TEXT, parameters TEXT, metrics TEXT, status TEXT, created_at TIMESTAMP
- **models**: id INTEGER PRIMARY KEY, name TEXT, version TEXT, accuracy REAL, created_at TIMESTAMP, path TEXT

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
