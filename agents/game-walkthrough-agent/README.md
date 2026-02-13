# ゲーム攻略・Walkthroughエージェント

ゲームの攻略情報・walkthroughを管理するエージェント

## Overview

This agent helps manage game-walkthrough-agent.

## Features

- Track game information
- Search and filter data
- Discord bot integration
- Custom content management

## Database

The agent uses SQLite with the following tables:

- Various game-related tables for game-walkthrough-agent

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
from agent import GameWalkthroughAgent

agent = GameWalkthroughAgent()
info = agent.get_all()
print(info)
```

### Discord Commands

- `!search <query>` - 情報を検索
- `!add <game_id> [data...]` - 情報を追加
- `!list <game_title>` - 情報を一覧表示
- `!update <entry_id> [data...]` - 情報を更新
- `!delete <entry_id>` - 情報を削除

## Requirements

See `requirements.txt`.

## License

MIT

---

# ゲーム攻略・Walkthroughエージェント（game-walkthrough-agent）

ゲームの攻略情報・walkthroughを管理するエージェント

## 概要

このエージェントはgame-walkthrough-agentを管理するのに役立ちます。

## 機能

- ゲーム情報を追跡
- データの検索とフィルタリング
- Discordボットとの統合
- カスタムコンテンツ管理

## データベース

このエージェントはSQLiteを使用し、game-walkthrough-agent関連のテーブルを持ちます。

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
from agent import GameWalkthroughAgent

agent = GameWalkthroughAgent()
info = agent.get_all()
print(info)
```

### Discordコマンド

- `!search <query>` - 情報を検索
- `!add <game_id> [data...]` - 情報を追加
- `!list <game_title>` - 情報を一覧表示
- `!update <entry_id> [data...]` - 情報を更新
- `!delete <entry_id>` - 情報を削除

## 依存パッケージ

`requirements.txt` を参照してください。

## ライセンス

MIT
