# data-ingestor-agent

データインジェスターエージェント / Data Ingestor Agent

各種データソースからデータを収集・取り込むエージェント

Collects and ingests data from various sources

## Features / 機能

- 追加: 新しいアイテムをデータベースに追加
- 表示: アイテム一覧の表示
- 検索: キーワードでアイテムを検索
- 削除: アイテムを削除
- ステータス: データベースの統計情報を表示

## Installation / インストール

\`\`\`bash
pip install -r requirements.txt
export DISCORD_TOKEN="your_discord_bot_token"
python discord.py
\`\`\`

## Requirements / 要件

- Python 3.8+
- discord.py 2.0+

## Commands / コマンド

| Command | Description | 説明 |
|---------|-------------|------|
| `!dataingestoragent` | Main menu | メインメニュー |
| `!dataingestoragent status` | Show status | ステータス表示 |
| `!dataingestoragent add <content>` | Add item | アイテム追加 |
| `!dataingestoragent list [limit]` | List items | アイテム一覧 |
| `!dataingestoragent search <query>` | Search items | アイテム検索 |
| `!dataingestoragent remove <id>` | Remove item | アイテム削除 |

## Usage / 使用方法

\`\`\`
!dataingestoragent add Example content
!dataingestoragent list 10
!dataingestoragent search keyword
!dataingestoragent remove 1
\`\`\`

## Database / データベース

SQLite database. Data stored in `data/data-ingestor-agent.db`.

## License / ライセンス

MIT License
