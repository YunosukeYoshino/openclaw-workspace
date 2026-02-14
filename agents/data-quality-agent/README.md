# data-quality-agent

データ品質エージェント。データ品質のチェック・監視・改善。

## 概要 / Overview

**日本語:**
データ品質エージェント。データ品質のチェック・監視・改善。を提供するエージェント。

**English:**
An agent providing データ品質エージェント。データ品質のチェック・監視・改善。.

## カテゴリ / Category

- `data`

## 機能 / Features

- Discord Bot 連携による対話型インターフェース
- SQLite データベースによるデータ管理
- コマンドラインからの操作

## コマンド / Commands

| コマンド | 説明 | 説明 (EN) |
|----------|------|-----------|
| `!add_rule` | add_rule コマンド | add_rule command |
| `!run_checks` | run_checks コマンド | run_checks command |
| `!quality_report` | quality_report コマンド | quality_report command |
| `!fix_issues` | fix_issues コマンド | fix_issues command |

## インストール / Installation

```bash
cd agents/data-quality-agent
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

- **rules**: id INTEGER PRIMARY KEY, name TEXT, type TEXT, config JSON, enabled INTEGER
- **checks**: id INTEGER PRIMARY KEY, rule_id INTEGER, dataset_id INTEGER, passed INTEGER, failed INTEGER, checked_at TIMESTAMP, FOREIGN KEY (rule_id) REFERENCES rules(id
- **issues**: id INTEGER PRIMARY KEY, check_id INTEGER, row_id INTEGER, column TEXT, description TEXT, FOREIGN KEY (check_id) REFERENCES checks(id

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
