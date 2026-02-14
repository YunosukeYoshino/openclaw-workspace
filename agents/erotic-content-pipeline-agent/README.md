# erotic-content-pipeline-agent

えっちコンテンツパイプラインエージェント。コンテンツ制作〜配信のパイプライン管理。

## 概要 / Overview

**日本語:**
えっちコンテンツパイプラインエージェント。コンテンツ制作〜配信のパイプライン管理。を提供するエージェント。

**English:**
An agent providing えっちコンテンツパイプラインエージェント。コンテンツ制作〜配信のパイプライン管理。.

## カテゴリ / Category

- `erotic`

## 機能 / Features

- Discord Bot 連携による対話型インターフェース
- SQLite データベースによるデータ管理
- コマンドラインからの操作

## コマンド / Commands

| コマンド | 説明 | 説明 (EN) |
|----------|------|-----------|
| `!create_pipeline` | create_pipeline コマンド | create_pipeline command |
| `!run_pipeline` | run_pipeline コマンド | run_pipeline command |
| `!pipeline_status` | pipeline_status コマンド | pipeline_status command |
| `!pipeline_logs` | pipeline_logs コマンド | pipeline_logs command |

## インストール / Installation

```bash
cd agents/erotic-content-pipeline-agent
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

- **content_pipelines**: id INTEGER PRIMARY KEY, name TEXT, stages JSON, status TEXT, config JSON
- **pipeline_runs**: id INTEGER PRIMARY KEY, pipeline_id INTEGER, start_time TIMESTAMP, end_time TIMESTAMP, status TEXT, output TEXT, FOREIGN KEY (pipeline_id) REFERENCES content_pipelines(id
- **stage_logs**: id INTEGER PRIMARY KEY, run_id INTEGER, stage TEXT, status TEXT, log TEXT, FOREIGN KEY (run_id) REFERENCES pipeline_runs(id

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
