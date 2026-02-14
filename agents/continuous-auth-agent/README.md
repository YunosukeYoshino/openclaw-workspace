# continuous-auth-agent

継続認証エージェント。継続的な認証・再認証の管理。

## 概要 / Overview

**日本語:**
継続認証エージェント。継続的な認証・再認証の管理。を提供するエージェント。

**English:**
An agent providing 継続認証エージェント。継続的な認証・再認証の管理。.

## カテゴリ / Category

- `security`

## 機能 / Features

- Discord Bot 連携による対話型インターフェース
- SQLite データベースによるデータ管理
- コマンドラインからの操作

## コマンド / Commands

| コマンド | 説明 | 説明 (EN) |
|----------|------|-----------|
| `!session_status` | session_status コマンド | session_status command |
| `!auth_history` | auth_history コマンド | auth_history command |
| `!set_trigger` | set_trigger コマンド | set_trigger command |
| `!force_reauth` | force_reauth コマンド | force_reauth command |

## インストール / Installation

```bash
cd agents/continuous-auth-agent
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

- **sessions**: id INTEGER PRIMARY KEY, user_id INTEGER, token TEXT, created_at TIMESTAMP, last_activity TIMESTAMP, trust_level INTEGER
- **auth_events**: id INTEGER PRIMARY KEY, session_id INTEGER, event_type TEXT, success INTEGER, details JSON, timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY (session_id) REFERENCES sessions(id
- **reauth_triggers**: id INTEGER PRIMARY KEY, name TEXT, condition JSON, action TEXT

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
