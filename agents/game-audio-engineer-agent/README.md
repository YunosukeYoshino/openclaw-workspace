# game-audio-engineer-agent

ゲームオーディオエンジニアエージェント。ゲームBGM・SE・音声の制作・管理。

## 概要 / Overview

**日本語:**
ゲームオーディオエンジニアエージェント。ゲームBGM・SE・音声の制作・管理。を提供するエージェント。

**English:**
An agent providing ゲームオーディオエンジニアエージェント。ゲームBGM・SE・音声の制作・管理。.

## カテゴリ / Category

- `game`

## 機能 / Features

- Discord Bot 連携による対話型インターフェース
- SQLite データベースによるデータ管理
- コマンドラインからの操作

## コマンド / Commands

| コマンド | 説明 | 説明 (EN) |
|----------|------|-----------|
| `!add_music` | add_music コマンド | add_music command |
| `!add_sfx` | add_sfx コマンド | add_sfx command |
| `!voice_over` | voice_over コマンド | voice_over command |
| `!audio_library` | audio_library コマンド | audio_library command |

## インストール / Installation

```bash
cd agents/game-audio-engineer-agent
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

- **audio_tracks**: id INTEGER PRIMARY KEY, project_id INTEGER, type TEXT, name TEXT, path TEXT, duration REAL, FOREIGN KEY (project_id) REFERENCES projects(id
- **sound_effects**: id INTEGER PRIMARY KEY, project_id INTEGER, name TEXT, trigger TEXT, path TEXT, FOREIGN KEY (project_id) REFERENCES projects(id
- **voice_overs**: id INTEGER PRIMARY KEY, project_id INTEGER, character TEXT, text TEXT, path TEXT, language TEXT

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
