# game-immersive-agent

ゲームイマーシブエージェント。没入型体験の設計・実装。

## 概要 / Overview

**日本語:**
ゲームイマーシブエージェント。没入型体験の設計・実装。を提供するエージェント。

**English:**
An agent providing ゲームイマーシブエージェント。没入型体験の設計・実装。.

## カテゴリ / Category

- `game`

## 機能 / Features

- Discord Bot 連携による対話型インターフェース
- SQLite データベースによるデータ管理
- コマンドラインからの操作

## コマンド / Commands

| コマンド | 説明 | 説明 (EN) |
|----------|------|-----------|
| `!create_experience` | create_experience コマンド | create_experience command |
| `!add_haptics` | add_haptics コマンド | add_haptics command |
| `!configure_audio` | configure_audio コマンド | configure_audio command |
| `!immersion_test` | immersion_test コマンド | immersion_test command |

## インストール / Installation

```bash
cd agents/game-immersive-agent
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

- **experiences**: id INTEGER PRIMARY KEY, name TEXT, type TEXT, immersion_level TEXT, devices JSON
- **haptics**: id INTEGER PRIMARY KEY, experience_id INTEGER, effect_type TEXT, intensity REAL, duration REAL, FOREIGN KEY (experience_id) REFERENCES experiences(id
- **spatial_audio**: id INTEGER PRIMARY KEY, experience_id INTEGER, source TEXT, position JSON, reverb TEXT, FOREIGN KEY (experience_id) REFERENCES experiences(id

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
