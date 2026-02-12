# figure-agent

フィギュア・グッズコレクション管理エージェント / Figure and merchandise collection management agent

## 機能 / Features

### 日本語 / Japanese
- フィギュア・グッズ登録・管理
- メーカー・シリーズ別管理
- 購入価格・販売価格管理
- 所持・欲しいリスト

### English / 英語
- Register and manage figures and merchandise
- Management by manufacturer and series
- Purchase price and selling price management
- Owned and wishlist

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
| `!add <title> <creator> [url]` | コンテンツを追加 / Add content |
| `!list [creator]` | コンテンツリスト表示 / List content |
| `!search <query>` | コンテンツ検索 / Search content |
| `!gallery` | ギャラリー表示 / Show gallery |

## ライセンス / License

MIT License
