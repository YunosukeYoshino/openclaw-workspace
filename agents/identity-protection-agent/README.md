# identity-protection-agent

ID保護エージェント。ユーザーIDの保護・監視・警告。

## 概要 / Overview

**日本語:**
ID保護エージェント。ユーザーIDの保護・監視・警告。を提供するエージェント。

**English:**
An agent providing ID保護エージェント。ユーザーIDの保護・監視・警告。.

## カテゴリ / Category

- `security`

## 機能 / Features

- Discord Bot 連携による対話型インターフェース
- SQLite データベースによるデータ管理
- コマンドラインからの操作

## コマンド / Commands

| コマンド | 説明 | 説明 (EN) |
|----------|------|-----------|
| `!protected_ids` | protected_ids コマンド | protected_ids command |
| `!check_breach` | check_breach コマンド | check_breach command |
| `!alerts` | alerts コマンド | alerts command |
| `!acknowledge_alert` | acknowledge_alert コマンド | acknowledge_alert command |

## インストール / Installation

```bash
cd agents/identity-protection-agent
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

- **identities**: id INTEGER PRIMARY KEY, user_id INTEGER, type TEXT, value TEXT, verified INTEGER, protected INTEGER
- **breach_checks**: id INTEGER PRIMARY KEY, identity_id INTEGER, source TEXT, found INTEGER, details JSON, checked_at TIMESTAMP, FOREIGN KEY (identity_id) REFERENCES identities(id
- **alerts**: id INTEGER PRIMARY KEY, identity_id INTEGER, type TEXT, severity TEXT, message TEXT, acknowledged INTEGER, created_at TIMESTAMP, FOREIGN KEY (identity_id) REFERENCES identities(id

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
