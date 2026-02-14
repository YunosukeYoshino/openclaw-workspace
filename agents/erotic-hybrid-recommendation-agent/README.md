# erotic-hybrid-recommendation-agent

えっちハイブリッド推薦エージェント。複数のアルゴリズムを組み合わせた推薦。

## 概要 / Overview

**日本語:**
えっちハイブリッド推薦エージェント。複数のアルゴリズムを組み合わせた推薦。を提供するエージェント。

**English:**
An agent providing えっちハイブリッド推薦エージェント。複数のアルゴリズムを組み合わせた推薦。.

## カテゴリ / Category

- `erotic`

## 機能 / Features

- Discord Bot 連携による対話型インターフェース
- SQLite データベースによるデータ管理
- コマンドラインからの操作

## コマンド / Commands

| コマンド | 説明 | 説明 (EN) |
|----------|------|-----------|
| `!create_hybrid_model` | create_hybrid_model コマンド | create_hybrid_model command |
| `!add_strategy` | add_strategy コマンド | add_strategy command |
| `!hybrid_recommend` | hybrid_recommend コマンド | hybrid_recommend command |
| `!tune_weights` | tune_weights コマンド | tune_weights command |

## インストール / Installation

```bash
cd agents/erotic-hybrid-recommendation-agent
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

- **strategies**: id INTEGER PRIMARY KEY, name TEXT, type TEXT, weight REAL, parameters JSON
- **hybrid_models**: id INTEGER PRIMARY KEY, name TEXT, strategies JSON, ensemble_method TEXT, performance_metrics JSON
- **recommendations**: id INTEGER PRIMARY KEY, user_id INTEGER, content_id INTEGER, hybrid_score REAL, strategy_scores JSON, created_at TIMESTAMP

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
