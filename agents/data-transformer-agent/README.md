# data-transformer-agent

データトランスフォーマーエージェント / Data Transformer Agent

データの変換・正規化・検証を行うエージェント

Transforms, normalizes, and validates data

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
| `!datatransformeragent` | Main menu | メインメニュー |
| `!datatransformeragent status` | Show status | ステータス表示 |
| `!datatransformeragent add <content>` | Add item | アイテム追加 |
| `!datatransformeragent list [limit]` | List items | アイテム一覧 |
| `!datatransformeragent search <query>` | Search items | アイテム検索 |
| `!datatransformeragent remove <id>` | Remove item | アイテム削除 |

## Usage / 使用方法

\`\`\`
!datatransformeragent add Example content
!datatransformeragent list 10
!datatransformeragent search keyword
!datatransformeragent remove 1
\`\`\`

## Database / データベース

SQLite database. Data stored in `data/data-transformer-agent.db`.

## License / ライセンス

MIT License
