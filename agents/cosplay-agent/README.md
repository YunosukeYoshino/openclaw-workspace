# cosplay-agent

コスプレ・衣装管理エージェント / Cosplay and costume management agent

## 機能 / Features

### 日本語 / Japanese
- コスプレ・衣装登録・管理
- キャラクター別衣装リスト
- 素材・パーツ管理
- 製作記録・写真管理

### English / 英語
- Register and manage cosplay and costumes
- Costume lists by character
- Material and parts management
- Production records and photo management

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
