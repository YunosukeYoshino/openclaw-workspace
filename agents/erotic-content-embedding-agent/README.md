# erotic-content-embedding-agent

えっちコンテンツ埋め込みエージェント。コンテンツのベクトル埋め込み生成。

## 概要 / Overview

**日本語:**
えっちコンテンツ埋め込みエージェント。コンテンツのベクトル埋め込み生成。を提供するエージェント。

**English:**
An agent providing えっちコンテンツ埋め込みエージェント。コンテンツのベクトル埋め込み生成。.

## カテゴリ / Category

- `erotic`

## 機能 / Features

- Discord Bot 連携による対話型インターフェース
- SQLite データベースによるデータ管理
- コマンドラインからの操作

## コマンド / Commands

| コマンド | 説明 | 説明 (EN) |
|----------|------|-----------|
| `!generate_embedding` | generate_embedding コマンド | generate_embedding command |
| `!similarity_search` | similarity_search コマンド | similarity_search command |
| `!batch_embed` | batch_embed コマンド | batch_embed command |
| `!model_info` | model_info コマンド | model_info command |

## インストール / Installation

```bash
cd agents/erotic-content-embedding-agent
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

- **embeddings**: id INTEGER PRIMARY KEY, content_id INTEGER, vector BLOB, model_version TEXT, dimensions INTEGER, created_at TIMESTAMP
- **similarity_search**: id INTEGER PRIMARY KEY, query_vector BLOB, results JSON, search_time REAL, timestamp TIMESTAMP
- **embedding_models**: id INTEGER PRIMARY KEY, name TEXT, architecture TEXT, dimensions INTEGER, training_data TEXT

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
