# ai-feature-store-agent

AIフィーチャーストアエージェント。MLフィーチャーの管理・提供。

## 概要 / Overview

**日本語:**
AIフィーチャーストアエージェント。MLフィーチャーの管理・提供。を提供するエージェント。

**English:**
An agent providing AIフィーチャーストアエージェント。MLフィーチャーの管理・提供。.

## カテゴリ / Category

- `ai`

## 機能 / Features

- Discord Bot 連携による対話型インターフェース
- SQLite データベースによるデータ管理
- コマンドラインからの操作

## コマンド / Commands

| コマンド | 説明 | 説明 (EN) |
|----------|------|-----------|
| `!add_feature` | add_feature コマンド | add_feature command |
| `!create_group` | create_group コマンド | create_group command |
| `!get_features` | get_features コマンド | get_features command |
| `!feature_history` | feature_history コマンド | feature_history command |

## インストール / Installation

```bash
cd agents/ai-feature-store-agent
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

- **features**: id INTEGER PRIMARY KEY, name TEXT, type TEXT, source TEXT, description TEXT, schema JSON
- **feature_groups**: id INTEGER PRIMARY KEY, name TEXT, features JSON, refresh_schedule TEXT
- **feature_values**: id INTEGER PRIMARY KEY, feature_id INTEGER, entity_id INTEGER, value TEXT, timestamp TIMESTAMP, FOREIGN KEY (feature_id) REFERENCES features(id

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
