# erotic-monetization-agent

えっちコンテンツマネタイズエージェント / Erotic Content Monetization Agent

収益管理、広告連携、ファンサイト運営を支援するエージェント

Manages revenue, ad partnerships, and fan site operations

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
| `!eroticmonetizationagent` | Main menu | メインメニュー |
| `!eroticmonetizationagent status` | Show status | ステータス表示 |
| `!eroticmonetizationagent add <content>` | Add item | アイテム追加 |
| `!eroticmonetizationagent list [limit]` | List items | アイテム一覧 |
| `!eroticmonetizationagent search <query>` | Search items | アイテム検索 |
| `!eroticmonetizationagent remove <id>` | Remove item | アイテム削除 |

## Usage / 使用方法

\`\`\`
!eroticmonetizationagent add Example content
!eroticmonetizationagent list 10
!eroticmonetizationagent search keyword
!eroticmonetizationagent remove 1
\`\`\`

## Database / データベース

SQLite database. Data stored in `data/erotic-monetization-agent.db`.

## License / ライセンス

MIT License
