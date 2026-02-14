# game-asset-manager-agent

ゲームアセットマネージャーエージェント。ゲームアセットの整理・管理・バージョン管理。

## 概要 / Overview

**日本語:**
ゲームアセットマネージャーエージェント。ゲームアセットの整理・管理・バージョン管理。を提供するエージェント。

**English:**
An agent providing ゲームアセットマネージャーエージェント。ゲームアセットの整理・管理・バージョン管理。.

## カテゴリ / Category

- `game`

## 機能 / Features

- Discord Bot 連携による対話型インターフェース
- SQLite データベースによるデータ管理
- コマンドラインからの操作

## コマンド / Commands

| コマンド | 説明 | 説明 (EN) |
|----------|------|-----------|
| `!add_asset` | add_asset コマンド | add_asset command |
| `!find_asset` | find_asset コマンド | find_asset command |
| `!asset_tags` | asset_tags コマンド | asset_tags command |
| `!check_dependencies` | check_dependencies コマンド | check_dependencies command |

## インストール / Installation

```bash
cd agents/game-asset-manager-agent
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

- **assets**: id INTEGER PRIMARY KEY, name TEXT, type TEXT, path TEXT, version INTEGER, project_id INTEGER
- **tags**: id INTEGER PRIMARY KEY, asset_id INTEGER, tag TEXT, FOREIGN KEY (asset_id) REFERENCES assets(id
- **dependencies**: id INTEGER PRIMARY KEY, asset_id INTEGER, depends_on INTEGER, FOREIGN KEY (asset_id) REFERENCES assets(id), FOREIGN KEY (depends_on) REFERENCES assets(id

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
