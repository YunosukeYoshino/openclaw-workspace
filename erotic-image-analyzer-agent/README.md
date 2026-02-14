# えっち画像アナライザーエージェント (erotic-image-analyzer-agent)

画像の分析・分類

## 機能 / Features

- 画像の分析・分類の管理・運用
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

データはSQLiteに保存されます。`erotic-image-analyzer-agent.db`ファイルが作成されます。

Data is stored in SQLite. A `erotic-image-analyzer-agent.db` file will be created.

## ライセンス / License

MIT License
