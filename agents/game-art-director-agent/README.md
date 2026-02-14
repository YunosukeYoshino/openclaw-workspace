# game-art-director-agent

ゲームアートディレクターエージェント。ゲームアート・ビジュアルスタイルの管理。

## 概要 / Overview

**日本語:**
ゲームアートディレクターエージェント。ゲームアート・ビジュアルスタイルの管理。を提供するエージェント。

**English:**
An agent providing ゲームアートディレクターエージェント。ゲームアート・ビジュアルスタイルの管理。.

## カテゴリ / Category

- `game`

## 機能 / Features

- Discord Bot 連携による対話型インターフェース
- SQLite データベースによるデータ管理
- コマンドラインからの操作

## コマンド / Commands

| コマンド | 説明 | 説明 (EN) |
|----------|------|-----------|
| `!art_style` | art_style コマンド | art_style command |
| `!add_asset` | add_asset コマンド | add_asset command |
| `!review_art` | review_art コマンド | review_art command |
| `!visual_guide` | visual_guide コマンド | visual_guide command |

## インストール / Installation

```bash
cd agents/game-art-director-agent
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

- **art_styles**: id INTEGER PRIMARY KEY, project_id INTEGER, style TEXT, palette JSON, references TEXT, FOREIGN KEY (project_id) REFERENCES projects(id
- **assets**: id INTEGER PRIMARY KEY, project_id INTEGER, type TEXT, name TEXT, path TEXT, status TEXT
- **reviews**: id INTEGER PRIMARY KEY, asset_id INTEGER, reviewer TEXT, rating INTEGER, feedback TEXT, FOREIGN KEY (asset_id) REFERENCES assets(id

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
