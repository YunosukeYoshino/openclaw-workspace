# game-3d-content-agent

ゲーム3Dコンテンツエージェント。3Dモデル・アセットの作成・管理。

## 概要 / Overview

**日本語:**
ゲーム3Dコンテンツエージェント。3Dモデル・アセットの作成・管理。を提供するエージェント。

**English:**
An agent providing ゲーム3Dコンテンツエージェント。3Dモデル・アセットの作成・管理。.

## カテゴリ / Category

- `game`

## 機能 / Features

- Discord Bot 連携による対話型インターフェース
- SQLite データベースによるデータ管理
- コマンドラインからの操作

## コマンド / Commands

| コマンド | 説明 | 説明 (EN) |
|----------|------|-----------|
| `!add_model` | add_model コマンド | add_model command |
| `!add_material` | add_material コマンド | add_material command |
| `!add_animation` | add_animation コマンド | add_animation command |
| `!3d_library` | 3d_library コマンド | 3d_library command |

## インストール / Installation

```bash
cd agents/game-3d-content-agent
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

- **models**: id INTEGER PRIMARY KEY, name TEXT, format TEXT, polygon_count INTEGER, texture_count INTEGER, path TEXT
- **materials**: id INTEGER PRIMARY KEY, model_id INTEGER, name TEXT, type TEXT, properties JSON, FOREIGN KEY (model_id) REFERENCES models(id
- **animations**: id INTEGER PRIMARY KEY, model_id INTEGER, name TEXT, duration REAL, frame_rate INTEGER, FOREIGN KEY (model_id) REFERENCES models(id

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
