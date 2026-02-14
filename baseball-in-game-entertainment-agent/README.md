# 野球インゲームエンターテインメントエージェント (baseball-in-game-entertainment-agent)

試合中エンターテインメントの管理

## 機能 / Features

- 試合中エンターテインメントの管理の管理・運用
- Discordボットによる対話型インターフェース
- SQLiteによるデータ永続化

## インストール / Installation

```bash
pip install -r requirements.txt
```

## 設定 / Configuration

環境変数 `DISCORD_TOKEN` を設定してください。

Set the `DISCORD_TOKEN` environment variable.

```bash
export DISCORD_TOKEN="your_bot_token"
```

## 使い方 / Usage

```bash
python agent.py
```

または / Or:

```bash
python discord.py
```

## データベース / Database

データはSQLiteに保存されます。`baseball-in-game-entertainment-agent.db`ファイルが作成されます。

Data is stored in SQLite. A `baseball-in-game-entertainment-agent.db` file will be created.

## ライセンス / License

MIT License
