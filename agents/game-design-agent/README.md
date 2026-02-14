# game-design-agent

ゲームデザインエージェント。ゲームのデザイン・コンセプト・メカニクスの管理。

## 概要 / Overview

**日本語:**
ゲームデザインエージェント。ゲームのデザイン・コンセプト・メカニクスの管理。を提供するエージェント。

**English:**
An agent providing ゲームデザインエージェント。ゲームのデザイン・コンセプト・メカニクスの管理。.

## カテゴリ / Category

- `game`

## 機能 / Features

- Discord Bot 連携による対話型インターフェース
- SQLite データベースによるデータ管理
- コマンドラインからの操作

## コマンド / Commands

| コマンド | 説明 | 説明 (EN) |
|----------|------|-----------|
| `!create_design` | create_design コマンド | create_design command |
| `!add_element` | add_element コマンド | add_element command |
| `!prototype` | prototype コマンド | prototype command |
| `!mechanics` | mechanics コマンド | mechanics command |

## インストール / Installation

```bash
cd agents/game-design-agent
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

- **game_designs**: id INTEGER PRIMARY KEY, title TEXT, genre TEXT, concept TEXT, mechanics TEXT
- **prototypes**: id INTEGER PRIMARY KEY, design_id INTEGER, version TEXT, notes TEXT, status TEXT, FOREIGN KEY (design_id) REFERENCES game_designs(id
- **design_elements**: id INTEGER PRIMARY KEY, design_id INTEGER, type TEXT, description TEXT, priority INTEGER, FOREIGN KEY (design_id) REFERENCES game_designs(id

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
