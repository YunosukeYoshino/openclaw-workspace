# ai-model-registry-agent

AIモデルレジストリエージェント。モデルのバージョン管理・デプロイ。

## 概要 / Overview

**日本語:**
AIモデルレジストリエージェント。モデルのバージョン管理・デプロイ。を提供するエージェント。

**English:**
An agent providing AIモデルレジストリエージェント。モデルのバージョン管理・デプロイ。.

## カテゴリ / Category

- `ai`

## 機能 / Features

- Discord Bot 連携による対話型インターフェース
- SQLite データベースによるデータ管理
- コマンドラインからの操作

## コマンド / Commands

| コマンド | 説明 | 説明 (EN) |
|----------|------|-----------|
| `!register_model` | register_model コマンド | register_model command |
| `!add_version` | add_version コマンド | add_version command |
| `!deploy_model` | deploy_model コマンド | deploy_model command |
| `!model_metadata` | model_metadata コマンド | model_metadata command |

## インストール / Installation

```bash
cd agents/ai-model-registry-agent
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

- **registered_models**: id INTEGER PRIMARY KEY, name TEXT, description TEXT, project_id INTEGER
- **model_versions**: id INTEGER PRIMARY KEY, model_id INTEGER, version TEXT, artifact_path TEXT, framework TEXT, metrics JSON, created_at TIMESTAMP, FOREIGN KEY (model_id) REFERENCES registered_models(id
- **deployments**: id INTEGER PRIMARY KEY, version_id INTEGER, environment TEXT, endpoint TEXT, deployed_at TIMESTAMP, status TEXT, FOREIGN KEY (version_id) REFERENCES model_versions(id

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
