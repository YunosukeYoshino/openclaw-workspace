# baseball-farm-system-agent

野球ファームシステムエージェント。マイナーリーグ・育成選手の管理。

## 概要 / Overview

**日本語:**
野球ファームシステムエージェント。マイナーリーグ・育成選手の管理。を提供するエージェント。

**English:**
An agent providing 野球ファームシステムエージェント。マイナーリーグ・育成選手の管理。.

## カテゴリ / Category

- `baseball`

## 機能 / Features

- Discord Bot 連携による対話型インターフェース
- SQLite データベースによるデータ管理
- コマンドラインからの操作

## コマンド / Commands

| コマンド | 説明 | 説明 (EN) |
|----------|------|-----------|
| `!farm_teams` | farm_teams コマンド | farm_teams command |
| `!farm_players` | farm_players コマンド | farm_players command |
| `!development_plan` | development_plan コマンド | development_plan command |
| `!track_progress` | track_progress コマンド | track_progress command |

## インストール / Installation

```bash
cd agents/baseball-farm-system-agent
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

- **farm_teams**: id INTEGER PRIMARY KEY, name TEXT, level TEXT, parent_team_id INTEGER
- **farm_players**: id INTEGER PRIMARY KEY, player_id INTEGER, team_id INTEGER, stats JSON, progress TEXT, FOREIGN KEY (team_id) REFERENCES farm_teams(id
- **development_plans**: id INTEGER PRIMARY KEY, player_id INTEGER, goals TEXT, milestones JSON, status TEXT

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
