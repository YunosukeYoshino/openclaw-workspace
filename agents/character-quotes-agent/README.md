# character-quotes-agent

キャラクター名言・セリフ収集エージェント / Character quotes and dialogue collection agent

## 機能 / Features

### 日本語 / Japanese
- キャラクター名言・セリフ収集
- セリフ検索・タグ付け
- シーン・状況メモ
- お気に入りセリフ登録

### English / 英語
- Character quotes and dialogue collection
- Quote search and tagging
- Scene and situation notes
- Register favorite quotes

## インストール / Installation

```bash
pip install -r requirements.txt
```

## 使用方法 / Usage

### エージェント実行 / Running the Agent

```bash
python3 agent.py
```

### Discord Bot / Discord Bot

```bash
export DISCORD_TOKEN="your_bot_token"
python3 discord.py
```

## データベース / Database

SQLiteデータベースを使用しています。初回実行時に自動的に作成されます。

## コマンド / Commands

| コマンド / Command | 説明 / Description |
|-------------------|-------------------|
| `!add <name> <source> [description]` | キャラクターを追加 / Add character |
| `!list [source]` | キャラクターリスト表示 / List characters |
| `!search <query>` | キャラクター検索 / Search characters |
| `!stats` | 統計情報表示 / Show statistics |

## ライセンス / License

MIT License
