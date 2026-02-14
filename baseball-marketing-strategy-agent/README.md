# 野球マーケティング戦略エージェント (baseball-marketing-strategy-agent)

マーケティング戦略の策定・実行

## 機能 / Features

- マーケティング戦略の策定・実行の管理・運用
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

データはSQLiteに保存されます。`baseball-marketing-strategy-agent.db`ファイルが作成されます。

Data is stored in SQLite. A `baseball-marketing-strategy-agent.db` file will be created.

## ライセンス / License

MIT License
