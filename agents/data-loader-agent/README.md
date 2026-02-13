# data-loader-agent

データローダーエージェント / Data Loader Agent

変換済みデータをデータストアにロードするエージェント

Loads transformed data into data stores

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
| `!dataloaderagent` | Main menu | メインメニュー |
| `!dataloaderagent status` | Show status | ステータス表示 |
| `!dataloaderagent add <content>` | Add item | アイテム追加 |
| `!dataloaderagent list [limit]` | List items | アイテム一覧 |
| `!dataloaderagent search <query>` | Search items | アイテム検索 |
| `!dataloaderagent remove <id>` | Remove item | アイテム削除 |

## Usage / 使用方法

\`\`\`
!dataloaderagent add Example content
!dataloaderagent list 10
!dataloaderagent search keyword
!dataloaderagent remove 1
\`\`\`

## Database / データベース

SQLite database. Data stored in `data/data-loader-agent.db`.

## License / ライセンス

MIT License
