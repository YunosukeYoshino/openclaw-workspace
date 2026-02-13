# game-data-migration-agent

Game Data Migration Agent

## 概要 / Overview

このエージェントは、Game Data MigrationのためのAIエージェントです。

## インストール / Installation

```bash
cd agents/game-data-migration-agent
pip install -r requirements.txt
```

## 使用方法 / Usage

### Discord Botとして実行 / Run as Discord Bot

```bash
python agent.py
```

### データベース初期化 / Initialize Database

```bash
python db.py
```

## 設定 / Configuration

Configuration is loaded from environment variables:
- `DISCORD_BOT_TOKEN`: Discordボットトークン / Discord bot token

## 依存パッケージ / Requirements

See `requirements.txt` for dependencies.

## ライセンス / License

MIT License
