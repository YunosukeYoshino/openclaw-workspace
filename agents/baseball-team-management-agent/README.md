# baseball-team-management-agent

野球チームマネジメントエージェント。チーム全体の管理・運営・戦略。

## 概要 / Overview

**日本語:**
野球チームマネジメントエージェント。チーム全体の管理・運営・戦略。を提供するエージェント。

**English:**
An agent providing 野球チームマネジメントエージェント。チーム全体の管理・運営・戦略。.

## カテゴリ / Category

- `baseball`

## 機能 / Features

- Discord Bot 連携による対話型インターフェース
- SQLite データベースによるデータ管理
- コマンドラインからの操作

## コマンド / Commands

| コマンド | 説明 | 説明 (EN) |
|----------|------|-----------|
| `!team_info` | team_info コマンド | team_info command |
| `!roster` | roster コマンド | roster command |
| `!staff` | staff コマンド | staff command |
| `!contracts` | contracts コマンド | contracts command |
| `!manage_team` | manage_team コマンド | manage_team command |

## インストール / Installation

```bash
cd agents/baseball-team-management-agent
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

- **teams**: id INTEGER PRIMARY KEY, name TEXT, league TEXT, division TEXT, city TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
- **rosters**: id INTEGER PRIMARY KEY, team_id INTEGER, player_id INTEGER, position TEXT, number INTEGER, FOREIGN KEY (team_id) REFERENCES teams(id
- **staff**: id INTEGER PRIMARY KEY, team_id INTEGER, name TEXT, role TEXT, FOREIGN KEY (team_id) REFERENCES teams(id
- **contracts**: id INTEGER PRIMARY KEY, team_id INTEGER, player_id INTEGER, salary INTEGER, years INTEGER, FOREIGN KEY (team_id) REFERENCES teams(id

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
