# erotic-subscription-agent

えっちサブスクリプションエージェント。サブスクリプション・会員プランの管理。

## 概要 / Overview

**日本語:**
えっちサブスクリプションエージェント。サブスクリプション・会員プランの管理。を提供するエージェント。

**English:**
An agent providing えっちサブスクリプションエージェント。サブスクリプション・会員プランの管理。.

## カテゴリ / Category

- `erotic`

## 機能 / Features

- Discord Bot 連携による対話型インターフェース
- SQLite データベースによるデータ管理
- コマンドラインからの操作

## コマンド / Commands

| コマンド | 説明 | 説明 (EN) |
|----------|------|-----------|
| `!plans` | plans コマンド | plans command |
| `!subscribe` | subscribe コマンド | subscribe command |
| `!subscription_status` | subscription_status コマンド | subscription_status command |
| `!cancel_subscription` | cancel_subscription コマンド | cancel_subscription command |

## インストール / Installation

```bash
cd agents/erotic-subscription-agent
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

- **plans**: id INTEGER PRIMARY KEY, name TEXT, price INTEGER, currency TEXT, duration_days INTEGER, features JSON
- **subscriptions**: id INTEGER PRIMARY KEY, user_id INTEGER, plan_id INTEGER, start_date TIMESTAMP, end_date TIMESTAMP, status TEXT, FOREIGN KEY (plan_id) REFERENCES plans(id
- **payments**: id INTEGER PRIMARY KEY, subscription_id INTEGER, amount INTEGER, status TEXT, method TEXT, timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY (subscription_id) REFERENCES subscriptions(id

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
