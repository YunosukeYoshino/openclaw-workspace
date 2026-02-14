# baseball-scouting-v2-agent

野球スカウティングV2エージェント。選手スカウティングの高度な分析・評価。

## 概要 / Overview

**日本語:**
野球スカウティングV2エージェント。選手スカウティングの高度な分析・評価。を提供するエージェント。

**English:**
An agent providing 野球スカウティングV2エージェント。選手スカウティングの高度な分析・評価。.

## カテゴリ / Category

- `baseball`

## 機能 / Features

- Discord Bot 連携による対話型インターフェース
- SQLite データベースによるデータ管理
- コマンドラインからの操作

## コマンド / Commands

| コマンド | 説明 | 説明 (EN) |
|----------|------|-----------|
| `!scout_player` | scout_player コマンド | scout_player command |
| `!draft_targets` | draft_targets コマンド | draft_targets command |
| `!combine_data` | combine_data コマンド | combine_data command |
| `!evaluate_player` | evaluate_player コマンド | evaluate_player command |

## インストール / Installation

```bash
cd agents/baseball-scouting-v2-agent
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

- **scouts**: id INTEGER PRIMARY KEY, agent_id INTEGER, player_id INTEGER, rating INTEGER, notes TEXT, date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
- **draft_targets**: id INTEGER PRIMARY KEY, player_id INTEGER, priority INTEGER, position TEXT, estimated_pick INTEGER
- **combine_data**: id INTEGER PRIMARY KEY, player_id INTEGER, run_time REAL, throw_speed REAL, bat_speed REAL, FOREIGN KEY (player_id) REFERENCES players(id

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
