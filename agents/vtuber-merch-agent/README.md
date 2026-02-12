# vtuber-merch-agent

VTuberグッズ情報管理エージェント / VTuber merchandise information management agent

## 機能 / Features

### 日本語 / Japanese
- グッズ情報登録・管理
- 販売サイトURL保存
- 購入履歴管理
- 欲しいリスト作成

### English / 英語
- Register and manage merchandise information
- Store sales site URLs
- Purchase history management
- Create wishlist

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
