# erotic-patreon-manager-agent

えっちPatreon管理エージェント / Erotic Patreon Manager Agent

Patreon運営、報酬ティア管理、限定コンテンツ配信を行うエージェント

Manages Patreon operations, reward tiers, and exclusive content distribution

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
| `!eroticpatreonmanageragent` | Main menu | メインメニュー |
| `!eroticpatreonmanageragent status` | Show status | ステータス表示 |
| `!eroticpatreonmanageragent add <content>` | Add item | アイテム追加 |
| `!eroticpatreonmanageragent list [limit]` | List items | アイテム一覧 |
| `!eroticpatreonmanageragent search <query>` | Search items | アイテム検索 |
| `!eroticpatreonmanageragent remove <id>` | Remove item | アイテム削除 |

## Usage / 使用方法

\`\`\`
!eroticpatreonmanageragent add Example content
!eroticpatreonmanageragent list 10
!eroticpatreonmanageragent search keyword
!eroticpatreonmanageragent remove 1
\`\`\`

## Database / データベース

SQLite database. Data stored in `data/erotic-patreon-manager-agent.db`.

## License / ライセンス

MIT License
