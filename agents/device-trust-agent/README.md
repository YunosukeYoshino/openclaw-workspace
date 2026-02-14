# device-trust-agent

デバイストラストエージェント。デバイスの信頼性評価・管理。

## 概要 / Overview

**日本語:**
デバイストラストエージェント。デバイスの信頼性評価・管理。を提供するエージェント。

**English:**
An agent providing デバイストラストエージェント。デバイスの信頼性評価・管理。.

## カテゴリ / Category

- `security`

## 機能 / Features

- Discord Bot 連携による対話型インターフェース
- SQLite データベースによるデータ管理
- コマンドラインからの操作

## コマンド / Commands

| コマンド | 説明 | 説明 (EN) |
|----------|------|-----------|
| `!device_status` | device_status コマンド | device_status command |
| `!device_checks` | device_checks コマンド | device_checks command |
| `!quarantine_device` | quarantine_device コマンド | quarantine_device command |
| `!approve_device` | approve_device コマンド | approve_device command |

## インストール / Installation

```bash
cd agents/device-trust-agent
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

- **devices**: id INTEGER PRIMARY KEY, device_id TEXT, user_id INTEGER, os TEXT, browser TEXT, last_seen TIMESTAMP, trust_score REAL
- **device_checks**: id INTEGER PRIMARY KEY, device_id TEXT, check_type TEXT, result INTEGER, details JSON, checked_at TIMESTAMP, FOREIGN KEY (device_id) REFERENCES devices(device_id
- **quarantined_devices**: id INTEGER PRIMARY KEY, device_id TEXT, reason TEXT, quarantined_at TIMESTAMP

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
