# erotic-distribution-agent

えっちコンテンツ配信エージェント。コンテンツの多チャネル配信・管理。

## 概要 / Overview

**日本語:**
えっちコンテンツ配信エージェント。コンテンツの多チャネル配信・管理。を提供するエージェント。

**English:**
An agent providing えっちコンテンツ配信エージェント。コンテンツの多チャネル配信・管理。.

## カテゴリ / Category

- `erotic`

## 機能 / Features

- Discord Bot 連携による対話型インターフェース
- SQLite データベースによるデータ管理
- コマンドラインからの操作

## コマンド / Commands

| コマンド | 説明 | 説明 (EN) |
|----------|------|-----------|
| `!add_channel` | add_channel コマンド | add_channel command |
| `!distribute` | distribute コマンド | distribute command |
| `!schedule_publish` | schedule_publish コマンド | schedule_publish command |
| `!distribution_status` | distribution_status コマンド | distribution_status command |

## インストール / Installation

```bash
cd agents/erotic-distribution-agent
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

- **channels**: id INTEGER PRIMARY KEY, name TEXT, type TEXT, config JSON, status TEXT
- **distributions**: id INTEGER PRIMARY KEY, content_id INTEGER, channel_id INTEGER, status TEXT, publish_time TIMESTAMP, FOREIGN KEY (channel_id) REFERENCES channels(id
- **schedules**: id INTEGER PRIMARY KEY, content_id INTEGER, channel_id INTEGER, scheduled_time TIMESTAMP, status TEXT

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
