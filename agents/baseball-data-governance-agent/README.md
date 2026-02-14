# baseball-data-governance-agent

野球データガバナンスエージェント。野球データの品質管理・ガバナンス。

## 概要 / Overview

**日本語:**
野球データガバナンスエージェント。野球データの品質管理・ガバナンス。を提供するエージェント。

**English:**
An agent providing 野球データガバナンスエージェント。野球データの品質管理・ガバナンス。.

## カテゴリ / Category

- `baseball`

## 機能 / Features

- Discord Bot 連携による対話型インターフェース
- SQLite データベースによるデータ管理
- コマンドラインからの操作

## コマンド / Commands

| コマンド | 説明 | 説明 (EN) |
|----------|------|-----------|
| `!add_rule` | add_rule コマンド | add_rule command |
| `!run_checks` | run_checks コマンド | run_checks command |
| `!lineage` | lineage コマンド | lineage command |
| `!governance_status` | governance_status コマンド | governance_status command |

## インストール / Installation

```bash
cd agents/baseball-data-governance-agent
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

- **data_quality_rules**: id INTEGER PRIMARY KEY, name TEXT, table TEXT, column TEXT, condition TEXT, severity TEXT
- **quality_checks**: id INTEGER PRIMARY KEY, rule_id INTEGER, checked_at TIMESTAMP, passed INTEGER, failed_count INTEGER, details TEXT, FOREIGN KEY (rule_id) REFERENCES data_quality_rules(id
- **data_lineage**: id INTEGER PRIMARY KEY, source_table TEXT, target_table TEXT, transformation TEXT, created_at TIMESTAMP

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
