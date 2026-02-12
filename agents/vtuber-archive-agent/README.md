# vtuber-archive-agent

VTuberアーカイブ管理エージェント / VTuber archive management agent

## 機能 / Features

### 日本語 / Japanese
- アーカイブ動画URL管理
- お気に入りアーカイブ登録
- タグ・カテゴリ管理
- 視聴履歴・メモ

### English / 英語
- Archive video URL management
- Register favorite archives
- Tag and category management
- Watch history and notes

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
| `!add <name> [description]` | VTuberを追加 / Add VTuber |
| `!list` | VTuberリスト表示 / List VTubers |
| `!search <query>` | VTuber検索 / Search VTubers |
| `!upcoming [days]` | 近日の配信表示 / Show upcoming streams |

## ライセンス / License

MIT License
