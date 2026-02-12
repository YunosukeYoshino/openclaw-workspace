# character-media-agent

キャラクターメディア（画像・動画）管理エージェント / Character media (image/video) management agent

## 機能 / Features

### 日本語 / Japanese
- キャラクター画像・動画管理
- メディアURL保存
- メディアタグ付け
- コレクションギャラリー

### English / 英語
- Character image and video management
- Media URL storage
- Media tagging
- Collection gallery

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
