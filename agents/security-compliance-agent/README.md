# security-compliance-agent

セキュリティコンプライアンスエージェント。コンプライアンス要件の管理・監視。

## 概要 / Overview

**日本語:**
セキュリティコンプライアンスエージェント。コンプライアンス要件の管理・監視。を提供するエージェント。

**English:**
An agent providing セキュリティコンプライアンスエージェント。コンプライアンス要件の管理・監視。.

## カテゴリ / Category

- `security`

## 機能 / Features

- Discord Bot 連携による対話型インターフェース
- SQLite データベースによるデータ管理
- コマンドラインからの操作

## コマンド / Commands

| コマンド | 説明 | 説明 (EN) |
|----------|------|-----------|
| `!frameworks` | frameworks コマンド | frameworks command |
| `!controls` | controls コマンド | controls command |
| `!run_assessment` | run_assessment コマンド | run_assessment command |
| `!compliance_report` | compliance_report コマンド | compliance_report command |

## インストール / Installation

```bash
cd agents/security-compliance-agent
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

- **frameworks**: id INTEGER PRIMARY KEY, name TEXT, description TEXT, requirements JSON
- **controls**: id INTEGER PRIMARY KEY, framework_id INTEGER, control_id TEXT, description TEXT, status TEXT, evidence TEXT, FOREIGN KEY (framework_id) REFERENCES frameworks(id
- **assessments**: id INTEGER PRIMARY KEY, framework_id INTEGER, assessment_type TEXT, score REAL, findings JSON, assessed_at TIMESTAMP, FOREIGN KEY (framework_id) REFERENCES frameworks(id

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
