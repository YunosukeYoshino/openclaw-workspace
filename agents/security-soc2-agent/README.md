# security-soc2-agent

セキュリティSOC 2エージェント。SOC 2コンプライアンスの管理・対応。

## 概要 / Overview

**日本語:**
セキュリティSOC 2エージェント。SOC 2コンプライアンスの管理・対応。を提供するエージェント。

**English:**
An agent providing セキュリティSOC 2エージェント。SOC 2コンプライアンスの管理・対応。.

## カテゴリ / Category

- `security`

## 機能 / Features

- Discord Bot 連携による対話型インターフェース
- SQLite データベースによるデータ管理
- コマンドラインからの操作

## コマンド / Commands

| コマンド | 説明 | 説明 (EN) |
|----------|------|-----------|
| `!trust_services` | trust_services コマンド | trust_services command |
| `!collect_evidence` | collect_evidence コマンド | collect_evidence command |
| `!audit_status` | audit_status コマンド | audit_status command |
| `!soc2_report` | soc2_report コマンド | soc2_report command |

## インストール / Installation

```bash
cd agents/security-soc2-agent
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

- **trust_services**: id INTEGER PRIMARY KEY, service_type TEXT, criteria TEXT, controls JSON, status TEXT
- **evidence**: id INTEGER PRIMARY KEY, control_id INTEGER, evidence_type TEXT, file_path TEXT, collected_at TIMESTAMP, reviewer_id INTEGER
- **audit_reports**: id INTEGER PRIMARY KEY, report_id TEXT, report_type TEXT, period_start TEXT, period_end TEXT, status TEXT, issued_at TIMESTAMP

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
