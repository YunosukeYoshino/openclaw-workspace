# ai-model-pipeline-agent

AIモデルパイプラインエージェント。MLパイプラインの自動化・管理。

## 概要 / Overview

**日本語:**
AIモデルパイプラインエージェント。MLパイプラインの自動化・管理。を提供するエージェント。

**English:**
An agent providing AIモデルパイプラインエージェント。MLパイプラインの自動化・管理。.

## カテゴリ / Category

- `ai`

## 機能 / Features

- Discord Bot 連携による対話型インターフェース
- SQLite データベースによるデータ管理
- コマンドラインからの操作

## コマンド / Commands

| コマンド | 説明 | 説明 (EN) |
|----------|------|-----------|
| `!create_pipeline` | create_pipeline コマンド | create_pipeline command |
| `!run_pipeline` | run_pipeline コマンド | run_pipeline command |
| `!pipeline_history` | pipeline_history コマンド | pipeline_history command |
| `!stage_logs` | stage_logs コマンド | stage_logs command |

## インストール / Installation

```bash
cd agents/ai-model-pipeline-agent
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

- **pipelines**: id INTEGER PRIMARY KEY, name TEXT, stages JSON, config JSON, status TEXT
- **pipeline_runs**: id INTEGER PRIMARY KEY, pipeline_id INTEGER, start_time TIMESTAMP, end_time TIMESTAMP, status TEXT, metrics JSON, FOREIGN KEY (pipeline_id) REFERENCES pipelines(id
- **stage_runs**: id INTEGER PRIMARY KEY, run_id INTEGER, stage_name TEXT, start_time TIMESTAMP, end_time TIMESTAMP, status TEXT, output_path TEXT, FOREIGN KEY (run_id) REFERENCES pipeline_runs(id

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
