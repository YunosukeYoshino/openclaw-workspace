# security-pci-dss-agent

セキュリティPCI DSSエージェント。PCI DSSコンプライアンスの管理・対応。

## 概要 / Overview

**日本語:**
セキュリティPCI DSSエージェント。PCI DSSコンプライアンスの管理・対応。を提供するエージェント。

**English:**
An agent providing セキュリティPCI DSSエージェント。PCI DSSコンプライアンスの管理・対応。.

## カテゴリ / Category

- `security`

## 機能 / Features

- Discord Bot 連携による対話型インターフェース
- SQLite データベースによるデータ管理
- コマンドラインからの操作

## コマンド / Commands

| コマンド | 説明 | 説明 (EN) |
|----------|------|-----------|
| `!requirements` | requirements コマンド | requirements command |
| `!run_scan` | run_scan コマンド | run_scan command |
| `!remediation_plan` | remediation_plan コマンド | remediation_plan command |
| `!compliance_status` | compliance_status コマンド | compliance_status command |

## インストール / Installation

```bash
cd agents/security-pci-dss-agent
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

- **requirements**: id INTEGER PRIMARY KEY, requirement_id TEXT, description TEXT, control_procedures TEXT, status TEXT
- **scans**: id INTEGER PRIMARY KEY, scan_type TEXT, start_time TIMESTAMP, end_time TIMESTAMP, vulnerabilities JSON, status TEXT
- **remediations**: id INTEGER PRIMARY KEY, requirement_id INTEGER, vulnerability_id TEXT, plan TEXT, status TEXT, completed_at TIMESTAMP, FOREIGN KEY (requirement_id) REFERENCES requirements(id

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
