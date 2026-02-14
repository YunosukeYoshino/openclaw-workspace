# security-hipaa-agent

セキュリティHIPAAエージェント。HIPAAコンプライアンスの管理・対応。

## 概要 / Overview

**日本語:**
セキュリティHIPAAエージェント。HIPAAコンプライアンスの管理・対応。を提供するエージェント。

**English:**
An agent providing セキュリティHIPAAエージェント。HIPAAコンプライアンスの管理・対応。.

## カテゴリ / Category

- `security`

## 機能 / Features

- Discord Bot 連携による対話型インターフェース
- SQLite データベースによるデータ管理
- コマンドラインからの操作

## コマンド / Commands

| コマンド | 説明 | 説明 (EN) |
|----------|------|-----------|
| `!phi_inventory` | phi_inventory コマンド | phi_inventory command |
| `!access_audit` | access_audit コマンド | access_audit command |
| `!risk_assessment` | risk_assessment コマンド | risk_assessment command |
| `!compliance_check` | compliance_check コマンド | compliance_check command |

## インストール / Installation

```bash
cd agents/security-hipaa-agent
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

- **phi_records**: id INTEGER PRIMARY KEY, record_id TEXT, phi_type TEXT, access_controls TEXT, encryption_status TEXT
- **audit_logs**: id INTEGER PRIMARY KEY, phi_id INTEGER, action_type TEXT, user_id INTEGER, timestamp TIMESTAMP, details TEXT, FOREIGN KEY (phi_id) REFERENCES phi_records(id
- **risk_assessments**: id INTEGER PRIMARY KEY, phi_id INTEGER, risk_level TEXT, mitigation_plan TEXT, assessed_at TIMESTAMP, FOREIGN KEY (phi_id) REFERENCES phi_records(id

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
