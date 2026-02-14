# erotic-recommendation-v3-agent

えっちコンテンツ推薦V3エージェント。高度なAIによるパーソナライズ推薦。

## 概要 / Overview

**日本語:**
えっちコンテンツ推薦V3エージェント。高度なAIによるパーソナライズ推薦。を提供するエージェント。

**English:**
An agent providing えっちコンテンツ推薦V3エージェント。高度なAIによるパーソナライズ推薦。.

## カテゴリ / Category

- `erotic`

## 機能 / Features

- Discord Bot 連携による対話型インターフェース
- SQLite データベースによるデータ管理
- コマンドラインからの操作

## コマンド / Commands

| コマンド | 説明 | 説明 (EN) |
|----------|------|-----------|
| `!recommend` | recommend コマンド | recommend command |
| `!train_model` | train_model コマンド | train_model command |
| `!model_performance` | model_performance コマンド | model_performance command |
| `!recommendation_history` | recommendation_history コマンド | recommendation_history command |

## インストール / Installation

```bash
cd agents/erotic-recommendation-v3-agent
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

- **models**: id INTEGER PRIMARY KEY, name TEXT, algorithm TEXT, features TEXT, accuracy REAL, version TEXT
- **recommendations**: id INTEGER PRIMARY KEY, user_id INTEGER, content_id INTEGER, score REAL, reason TEXT, created_at TIMESTAMP
- **feedback**: id INTEGER PRIMARY KEY, recommendation_id INTEGER, rating INTEGER, clicked INTEGER, timestamp TIMESTAMP

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
