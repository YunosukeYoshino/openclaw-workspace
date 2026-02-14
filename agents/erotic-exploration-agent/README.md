# erotic-exploration-agent

えっち探索エージェント。ユーザーの新たな興味を発見・提案。

## 概要 / Overview

**日本語:**
えっち探索エージェント。ユーザーの新たな興味を発見・提案。を提供するエージェント。

**English:**
An agent providing えっち探索エージェント。ユーザーの新たな興味を発見・提案。.

## カテゴリ / Category

- `erotic`

## 機能 / Features

- Discord Bot 連携による対話型インターフェース
- SQLite データベースによるデータ管理
- コマンドラインからの操作

## コマンド / Commands

| コマンド | 説明 | 説明 (EN) |
|----------|------|-----------|
| `!discover_new` | discover_new コマンド | discover_new command |
| `!diversity_report` | diversity_report コマンド | diversity_report command |
| `!exploration_history` | exploration_history コマンド | exploration_history command |
| `!tune_exploration` | tune_exploration コマンド | tune_exploration command |

## インストール / Installation

```bash
cd agents/erotic-exploration-agent
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

- **exploration_items**: id INTEGER PRIMARY KEY, user_id INTEGER, content_id INTEGER, score REAL, reason TEXT, suggested_at TIMESTAMP
- **diversity_metrics**: id INTEGER PRIMARY KEY, user_id INTEGER, diversity_score REAL, novelty_score REAL, serendipity_score REAL, calculated_at TIMESTAMP
- **exploration_history**: id INTEGER PRIMARY KEY, user_id INTEGER, content_id INTEGER, accepted INTEGER, interaction_type TEXT, timestamp TIMESTAMP

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
