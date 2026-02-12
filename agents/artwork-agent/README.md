# artwork-agent

イラスト・アートワーク管理エージェント / Illustration and artwork management agent

## 機能 / Features

### 日本語 / Japanese
- イラスト・アートワーク登録・管理
- アーティスト別作品リスト
- 作品URL・SNSリンク保存
- タグ・カテゴリ管理

### English / 英語
- Register and manage illustrations and artwork
- Work lists by artist
- Artwork URL and SNS link storage
- Tag and category management

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
