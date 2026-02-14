# game-ar-engine-agent

ゲームARエンジンエージェント。ARゲーム開発エンジンの管理・最適化。

## 概要 / Overview

**日本語:**
ゲームARエンジンエージェント。ARゲーム開発エンジンの管理・最適化。を提供するエージェント。

**English:**
An agent providing ゲームARエンジンエージェント。ARゲーム開発エンジンの管理・最適化。.

## カテゴリ / Category

- `game`

## 機能 / Features

- Discord Bot 連携による対話型インターフェース
- SQLite データベースによるデータ管理
- コマンドラインからの操作

## コマンド / Commands

| コマンド | 説明 | 説明 (EN) |
|----------|------|-----------|
| `!ar_engine` | ar_engine コマンド | ar_engine command |
| `!create_experience` | create_experience コマンド | create_experience command |
| `!add_marker` | add_marker コマンド | add_marker command |
| `!ar_analytics` | ar_analytics コマンド | ar_analytics command |

## インストール / Installation

```bash
cd agents/game-ar-engine-agent
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

- **ar_engines**: id INTEGER PRIMARY KEY, name TEXT, version TEXT, capabilities JSON, tracking_type TEXT
- **ar_experiences**: id INTEGER PRIMARY KEY, project_id INTEGER, name TEXT, markers JSON, content JSON, FOREIGN KEY (project_id) REFERENCES projects(id
- **ar_analytics**: id INTEGER PRIMARY KEY, experience_id INTEGER, user_id INTEGER, interaction_type TEXT, timestamp TIMESTAMP, FOREIGN KEY (experience_id) REFERENCES ar_experiences(id

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
