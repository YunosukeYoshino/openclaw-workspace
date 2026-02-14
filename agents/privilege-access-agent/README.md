# privilege-access-agent

特権アクセスエージェント。特権アクセスの管理・監査・承認。

## 概要 / Overview

**日本語:**
特権アクセスエージェント。特権アクセスの管理・監査・承認。を提供するエージェント。

**English:**
An agent providing 特権アクセスエージェント。特権アクセスの管理・監査・承認。.

## カテゴリ / Category

- `security`

## 機能 / Features

- Discord Bot 連携による対話型インターフェース
- SQLite データベースによるデータ管理
- コマンドラインからの操作

## コマンド / Commands

| コマンド | 説明 | 説明 (EN) |
|----------|------|-----------|
| `!privileges` | privileges コマンド | privileges command |
| `!request_access` | request_access コマンド | request_access command |
| `!approve_request` | approve_request コマンド | approve_request command |
| `!audit_log` | audit_log コマンド | audit_log command |

## インストール / Installation

```bash
cd agents/privilege-access-agent
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

- **privileges**: id INTEGER PRIMARY KEY, name TEXT, description TEXT, level INTEGER, approval_required INTEGER
- **assignments**: id INTEGER PRIMARY KEY, user_id INTEGER, privilege_id INTEGER, granted_by INTEGER, granted_at TIMESTAMP, expires_at TIMESTAMP, FOREIGN KEY (privilege_id) REFERENCES privileges(id
- **requests**: id INTEGER PRIMARY KEY, user_id INTEGER, privilege_id INTEGER, reason TEXT, status TEXT, requested_at TIMESTAMP, approved_by INTEGER, FOREIGN KEY (privilege_id) REFERENCES privileges(id

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
