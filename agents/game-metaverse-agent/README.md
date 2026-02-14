# game-metaverse-agent

ゲームメタバースエージェント。メタバース空間の作成・管理・運営。

## 概要 / Overview

**日本語:**
ゲームメタバースエージェント。メタバース空間の作成・管理・運営。を提供するエージェント。

**English:**
An agent providing ゲームメタバースエージェント。メタバース空間の作成・管理・運営。.

## カテゴリ / Category

- `game`

## 機能 / Features

- Discord Bot 連携による対話型インターフェース
- SQLite データベースによるデータ管理
- コマンドラインからの操作

## コマンド / Commands

| コマンド | 説明 | 説明 (EN) |
|----------|------|-----------|
| `!create_world` | create_world コマンド | create_world command |
| `!manage_avatar` | manage_avatar コマンド | manage_avatar command |
| `!world_events` | world_events コマンド | world_events command |
| `!metaverse_stats` | metaverse_stats コマンド | metaverse_stats command |

## インストール / Installation

```bash
cd agents/game-metaverse-agent
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

- **worlds**: id INTEGER PRIMARY KEY, name TEXT, description TEXT, capacity INTEGER, settings JSON
- **avatars**: id INTEGER PRIMARY KEY, user_id INTEGER, world_id INTEGER, appearance JSON, position JSON, FOREIGN KEY (world_id) REFERENCES worlds(id
- **metaverse_events**: id INTEGER PRIMARY KEY, world_id INTEGER, event_type TEXT, data JSON, timestamp TIMESTAMP, FOREIGN KEY (world_id) REFERENCES worlds(id

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
