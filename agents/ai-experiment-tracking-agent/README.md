# ai-experiment-tracking-agent

AI実験追跡エージェント。ML実験の記録・管理。

## 概要 / Overview

**日本語:**
AI実験追跡エージェント。ML実験の記録・管理。を提供するエージェント。

**English:**
An agent providing AI実験追跡エージェント。ML実験の記録・管理。.

## カテゴリ / Category

- `ai`

## 機能 / Features

- Discord Bot 連携による対話型インターフェース
- SQLite データベースによるデータ管理
- コマンドラインからの操作

## コマンド / Commands

| コマンド | 説明 | 説明 (EN) |
|----------|------|-----------|
| `!create_experiment` | create_experiment コマンド | create_experiment command |
| `!log_run` | log_run コマンド | log_run command |
| `!compare_runs` | compare_runs コマンド | compare_runs command |
| `!experiment_history` | experiment_history コマンド | experiment_history command |

## インストール / Installation

```bash
cd agents/ai-experiment-tracking-agent
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

- **experiments**: id INTEGER PRIMARY KEY, name TEXT, project_id INTEGER, parameters TEXT, metrics TEXT, status TEXT, created_at TIMESTAMP
- **runs**: id INTEGER PRIMARY KEY, experiment_id INTEGER, run_id TEXT, start_time TIMESTAMP, end_time TIMESTAMP, metrics TEXT, artifacts TEXT, FOREIGN KEY (experiment_id) REFERENCES experiments(id
- **comparisons**: id INTEGER PRIMARY KEY, experiment_ids TEXT, comparison_metrics JSON, conclusion TEXT, created_at TIMESTAMP

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
