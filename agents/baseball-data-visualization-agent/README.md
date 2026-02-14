# baseball-data-visualization-agent

野球データ可視化エージェント。野球データの高度な可視化・ダッシュボード。

## 概要 / Overview

**日本語:**
野球データ可視化エージェント。野球データの高度な可視化・ダッシュボード。を提供するエージェント。

**English:**
An agent providing 野球データ可視化エージェント。野球データの高度な可視化・ダッシュボード。.

## カテゴリ / Category

- `baseball`

## 機能 / Features

- Discord Bot 連携による対話型インターフェース
- SQLite データベースによるデータ管理
- コマンドラインからの操作

## コマンド / Commands

| コマンド | 説明 | 説明 (EN) |
|----------|------|-----------|
| `!create_dashboard` | create_dashboard コマンド | create_dashboard command |
| `!add_chart` | add_chart コマンド | add_chart command |
| `!view_dashboard` | view_dashboard コマンド | view_dashboard command |
| `!schedule_report` | schedule_report コマンド | schedule_report command |

## インストール / Installation

```bash
cd agents/baseball-data-visualization-agent
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

- **dashboards**: id INTEGER PRIMARY KEY, name TEXT, layout JSON, widgets TEXT, created_at TIMESTAMP, updated_at TIMESTAMP
- **charts**: id INTEGER PRIMARY KEY, dashboard_id INTEGER, type TEXT, data_source TEXT, config JSON, FOREIGN KEY (dashboard_id) REFERENCES dashboards(id
- **reports**: id INTEGER PRIMARY KEY, name TEXT, type TEXT, schedule TEXT, recipients TEXT, created_at TIMESTAMP

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
