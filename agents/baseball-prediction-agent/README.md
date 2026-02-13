# 試合結果予測エージェント

野球の試合結果を予測するエージェント

## Overview

This agent helps manage baseball-prediction-agent.

## Features

- Track baseball statistics
- Analyze player performance
- Search and filter data
- Discord bot integration

## Database

The agent uses SQLite with the following tables:

- `baseball_stats` - Baseball statistics data
- `stat_entries` - Individual stat entries

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Initialize the database:
```bash
python db.py
```

3. Run the agent:
```bash
python agent.py
```

4. Run the Discord bot (optional):
```bash
export DISCORD_TOKEN=your_token_here
python discord.py
```

## Usage

### As a Module

```python
from agent import BaseballPredictionAgent

agent = BaseballPredictionAgent()
stats = agent.get_all()
print(stats)
```

### Discord Commands

- `!stats <player_name>` - 選手の統計を表示
- `!add <player_id> <player_name> [stats...]` - 統計を追加
- `!update <player_id> [stats...]` - 統計を更新
- `!search <query>` - 統計を検索
- `!summary` - サマリーを表示

## Requirements

See `requirements.txt`.

## License

MIT

---

# 試合結果予測エージェント（詳細野球統計分析エージェント）

野球の試合結果を予測するエージェント

## 概要

このエージェントはbaseball-prediction-agentを管理するのに役立ちます。

## 機能

- 野球の統計を追跡
- 選手の成績を分析
- データの検索とフィルタリング
- Discordボットとの統合

## データベース

このエージェントはSQLiteを使用し、以下のテーブルを持ちます：

- `baseball_stats` - 野球統計データ
- `stat_entries` - 個別の統計エントリー

## セットアップ

1. 依存パッケージをインストール：
```bash
pip install -r requirements.txt
```

2. データベースを初期化：
```bash
python db.py
```

3. エージェントを実行：
```bash
python agent.py
```

4. Discordボットを実行（オプション）：
```bash
export DISCORD_TOKEN=your_token_here
python discord.py
```

## 使用方法

### モジュールとして使用

```python
from agent import BaseballPredictionAgent

agent = BaseballPredictionAgent()
stats = agent.get_all()
print(stats)
```

### Discordコマンド

- `!stats <player_name>` - 選手の統計を表示
- `!add <player_id> <player_name> [stats...]` - 統計を追加
- `!update <player_id> [stats...]` - 統計を更新
- `!search <query>` - 統計を検索
- `!summary` - サマリーを表示

## 依存パッケージ

`requirements.txt` を参照してください。

## ライセンス

MIT
