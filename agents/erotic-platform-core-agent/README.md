# erotic-platform-core-agent

えっちプラットフォームコアエージェント。えっちコンテンツプラットフォームの中核機能。

## 概要 / Overview

**日本語:**
えっちプラットフォームコアエージェント。えっちコンテンツプラットフォームの中核機能。を提供するエージェント。

**English:**
An agent providing えっちプラットフォームコアエージェント。えっちコンテンツプラットフォームの中核機能。.

## カテゴリ / Category

- `erotic`

## 機能 / Features

- Discord Bot 連携による対話型インターフェース
- SQLite データベースによるデータ管理
- コマンドラインからの操作

## コマンド / Commands

| コマンド | 説明 | 説明 (EN) |
|----------|------|-----------|
| `!platform_status` | platform_status コマンド | platform_status command |
| `!config` | config コマンド | config command |
| `!features` | features コマンド | features command |
| `!integrations` | integrations コマンド | integrations command |

## インストール / Installation

```bash
cd agents/erotic-platform-core-agent
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

- **platform_config**: id INTEGER PRIMARY KEY, key TEXT, value TEXT, description TEXT
- **features**: id INTEGER PRIMARY KEY, name TEXT, status TEXT, priority INTEGER, description TEXT
- **integrations**: id INTEGER PRIMARY KEY, service TEXT, config JSON, status TEXT

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
