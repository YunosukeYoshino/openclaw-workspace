# baseball-schedule-optimizer-agent

野球スケジュール最適化エージェント。試合スケジュールの最適化・調整。

## 概要 / Overview

**日本語:**
野球スケジュール最適化エージェント。試合スケジュールの最適化・調整。を提供するエージェント。

**English:**
An agent providing 野球スケジュール最適化エージェント。試合スケジュールの最適化・調整。.

## カテゴリ / Category

- `baseball`

## 機能 / Features

- Discord Bot 連携による対話型インターフェース
- SQLite データベースによるデータ管理
- コマンドラインからの操作

## コマンド / Commands

| コマンド | 説明 | 説明 (EN) |
|----------|------|-----------|
| `!schedule` | schedule コマンド | schedule command |
| `!travel_plan` | travel_plan コマンド | travel_plan command |
| `!rest_days` | rest_days コマンド | rest_days command |
| `!optimize_schedule` | optimize_schedule コマンド | optimize_schedule command |

## インストール / Installation

```bash
cd agents/baseball-schedule-optimizer-agent
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

- **schedules**: id INTEGER PRIMARY KEY, team_id INTEGER, opponent TEXT, date TEXT, venue TEXT, time TEXT
- **travel_plans**: id INTEGER PRIMARY KEY, team_id INTEGER, from_city TEXT, to_city TEXT, travel_time REAL, mode TEXT
- **rest_days**: id INTEGER PRIMARY KEY, team_id INTEGER, date TEXT, type TEXT, notes TEXT

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
