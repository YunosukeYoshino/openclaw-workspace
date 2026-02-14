# baseball-strategy-agent

野球戦略エージェント。チーム戦略の立案・分析・最適化。

## 概要 / Overview

**日本語:**
野球戦略エージェント。チーム戦略の立案・分析・最適化。を提供するエージェント。

**English:**
An agent providing 野球戦略エージェント。チーム戦略の立案・分析・最適化。.

## カテゴリ / Category

- `baseball`

## 機能 / Features

- Discord Bot 連携による対話型インターフェース
- SQLite データベースによるデータ管理
- コマンドラインからの操作

## コマンド / Commands

| コマンド | 説明 | 説明 (EN) |
|----------|------|-----------|
| `!create_strategy` | create_strategy コマンド | create_strategy command |
| `!lineup` | lineup コマンド | lineup command |
| `!gameplan` | gameplan コマンド | gameplan command |
| `!analyze_strategy` | analyze_strategy コマンド | analyze_strategy command |

## インストール / Installation

```bash
cd agents/baseball-strategy-agent
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

- **strategies**: id INTEGER PRIMARY KEY, team_id INTEGER, type TEXT, description TEXT, effectiveness REAL, FOREIGN KEY (team_id) REFERENCES teams(id
- **lineups**: id INTEGER PRIMARY KEY, team_id INTEGER, date TEXT, formation JSON, FOREIGN KEY (team_id) REFERENCES teams(id
- **gameplans**: id INTEGER PRIMARY KEY, opponent_id TEXT, strategy TEXT, tactics TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

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
