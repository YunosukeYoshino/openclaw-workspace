# security-gdpr-agent

セキュリティGDPRエージェント。GDPRコンプライアンスの管理・対応。

## 概要 / Overview

**日本語:**
セキュリティGDPRエージェント。GDPRコンプライアンスの管理・対応。を提供するエージェント。

**English:**
An agent providing セキュリティGDPRエージェント。GDPRコンプライアンスの管理・対応。.

## カテゴリ / Category

- `security`

## 機能 / Features

- Discord Bot 連携による対話型インターフェース
- SQLite データベースによるデータ管理
- コマンドラインからの操作

## コマンド / Commands

| コマンド | 説明 | 説明 (EN) |
|----------|------|-----------|
| `!subject_info` | subject_info コマンド | subject_info command |
| `!manage_consent` | manage_consent コマンド | manage_consent command |
| `!handle_request` | handle_request コマンド | handle_request command |
| `!privacy_audit` | privacy_audit コマンド | privacy_audit command |

## インストール / Installation

```bash
cd agents/security-gdpr-agent
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

- **data_subjects**: id INTEGER PRIMARY KEY, user_id INTEGER, consent_records JSON, data_categories TEXT, created_at TIMESTAMP
- **consent_records**: id INTEGER PRIMARY KEY, subject_id INTEGER, consent_type TEXT, granted INTEGER, timestamp TEXT, expiry TEXT, FOREIGN KEY (subject_id) REFERENCES data_subjects(id
- **data_requests**: id INTEGER PRIMARY KEY, subject_id INTEGER, request_type TEXT, status TEXT, response_data TEXT, completed_at TIMESTAMP, FOREIGN KEY (subject_id) REFERENCES data_subjects(id

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
