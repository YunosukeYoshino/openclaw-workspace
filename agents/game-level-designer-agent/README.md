# game-level-designer-agent

ゲームレベルデザイナーエージェント。ゲームレベル・ステージのデザイン・管理。

## 概要 / Overview

**日本語:**
ゲームレベルデザイナーエージェント。ゲームレベル・ステージのデザイン・管理。を提供するエージェント。

**English:**
An agent providing ゲームレベルデザイナーエージェント。ゲームレベル・ステージのデザイン・管理。.

## カテゴリ / Category

- `game`

## 機能 / Features

- Discord Bot 連携による対話型インターフェース
- SQLite データベースによるデータ管理
- コマンドラインからの操作

## コマンド / Commands

| コマンド | 説明 | 説明 (EN) |
|----------|------|-----------|
| `!create_level` | create_level コマンド | create_level command |
| `!add_object` | add_object コマンド | add_object command |
| `!level_flow` | level_flow コマンド | level_flow command |
| `!playtest` | playtest コマンド | playtest command |

## インストール / Installation

```bash
cd agents/game-level-designer-agent
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

- **levels**: id INTEGER PRIMARY KEY, project_id INTEGER, name TEXT, difficulty INTEGER, length REAL, FOREIGN KEY (project_id) REFERENCES projects(id
- **level_objects**: id INTEGER PRIMARY KEY, level_id INTEGER, type TEXT, position JSON, properties JSON, FOREIGN KEY (level_id) REFERENCES levels(id
- **level_flows**: id INTEGER PRIMARY KEY, level_id INTEGER, sequence JSON, pacing TEXT, FOREIGN KEY (level_id) REFERENCES levels(id

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
