# baseball-statistical-modeling-agent

野球統計モデリングエージェント。野球データの統計的モデリング・予測。

## 概要 / Overview

**日本語:**
野球統計モデリングエージェント。野球データの統計的モデリング・予測。を提供するエージェント。

**English:**
An agent providing 野球統計モデリングエージェント。野球データの統計的モデリング・予測。.

## カテゴリ / Category

- `baseball`

## 機能 / Features

- Discord Bot 連携による対話型インターフェース
- SQLite データベースによるデータ管理
- コマンドラインからの操作

## コマンド / Commands

| コマンド | 説明 | 説明 (EN) |
|----------|------|-----------|
| `!create_model` | create_model コマンド | create_model command |
| `!train_model` | train_model コマンド | train_model command |
| `!predict` | predict コマンド | predict command |
| `!evaluate_model` | evaluate_model コマンド | evaluate_model command |

## インストール / Installation

```bash
cd agents/baseball-statistical-modeling-agent
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

- **models**: id INTEGER PRIMARY KEY, name TEXT, type TEXT, features TEXT, hyperparameters TEXT, accuracy REAL
- **predictions**: id INTEGER PRIMARY KEY, model_id INTEGER, player_id INTEGER, prediction TEXT, confidence REAL, created_at TIMESTAMP, FOREIGN KEY (model_id) REFERENCES models(id
- **model_evaluations**: id INTEGER PRIMARY KEY, model_id INTEGER, metric TEXT, value REAL, evaluated_at TIMESTAMP, FOREIGN KEY (model_id) REFERENCES models(id

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
