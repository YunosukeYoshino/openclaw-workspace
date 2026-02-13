# erotic-content-marketplace-agent

えっちコンテンツマーケットプレイスエージェント / Erotic Content Marketplace Agent

コンテンツ販売、ライセンス管理、販売分析を行うエージェント

Manages content sales, licensing, and sales analytics

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
| `!eroticcontentmarketplaceagent` | Main menu | メインメニュー |
| `!eroticcontentmarketplaceagent status` | Show status | ステータス表示 |
| `!eroticcontentmarketplaceagent add <content>` | Add item | アイテム追加 |
| `!eroticcontentmarketplaceagent list [limit]` | List items | アイテム一覧 |
| `!eroticcontentmarketplaceagent search <query>` | Search items | アイテム検索 |
| `!eroticcontentmarketplaceagent remove <id>` | Remove item | アイテム削除 |

## Usage / 使用方法

\`\`\`
!eroticcontentmarketplaceagent add Example content
!eroticcontentmarketplaceagent list 10
!eroticcontentmarketplaceagent search keyword
!eroticcontentmarketplaceagent remove 1
\`\`\`

## Database / データベース

SQLite database. Data stored in `data/erotic-content-marketplace-agent.db`.

## License / ライセンス

MIT License
