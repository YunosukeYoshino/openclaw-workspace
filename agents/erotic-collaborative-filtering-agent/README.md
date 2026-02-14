# erotic-collaborative-filtering-agent

えっち協調フィルタリングエージェント。ユーザー間の類似性に基づく推薦。

## 概要 / Overview

**日本語:**
えっち協調フィルタリングエージェント。ユーザー間の類似性に基づく推薦。を提供するエージェント。

**English:**
An agent providing えっち協調フィルタリングエージェント。ユーザー間の類似性に基づく推薦。.

## カテゴリ / Category

- `erotic`

## 機能 / Features

- Discord Bot 連携による対話型インターフェース
- SQLite データベースによるデータ管理
- コマンドラインからの操作

## コマンド / Commands

| コマンド | 説明 | 説明 (EN) |
|----------|------|-----------|
| `!find_similar_users` | find_similar_users コマンド | find_similar_users command |
| `!find_similar_items` | find_similar_items コマンド | find_similar_items command |
| `!user_neighborhood` | user_neighborhood コマンド | user_neighborhood command |
| `!collaborative_recommend` | collaborative_recommend コマンド | collaborative_recommend command |

## インストール / Installation

```bash
cd agents/erotic-collaborative-filtering-agent
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

- **user_preferences**: id INTEGER PRIMARY KEY, user_id INTEGER, content_id INTEGER, rating INTEGER, timestamp TIMESTAMP
- **similar_users**: id INTEGER PRIMARY KEY, user_id INTEGER, similar_user_id INTEGER, similarity_score REAL, updated_at TIMESTAMP
- **item_similarities**: id INTEGER PRIMARY KEY, item_id INTEGER, similar_item_id INTEGER, similarity_score REAL, updated_at TIMESTAMP

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
