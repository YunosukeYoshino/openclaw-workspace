# erotic-commission-tracker-agent

えっちコミッショントラッカーエージェント / Erotic Commission Tracker Agent

コミッション受注、進捗管理、支払い追跡を行うエージェント

Tracks commission orders, manages progress, and handles payments

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
| `!eroticcommissiontrackeragent` | Main menu | メインメニュー |
| `!eroticcommissiontrackeragent status` | Show status | ステータス表示 |
| `!eroticcommissiontrackeragent add <content>` | Add item | アイテム追加 |
| `!eroticcommissiontrackeragent list [limit]` | List items | アイテム一覧 |
| `!eroticcommissiontrackeragent search <query>` | Search items | アイテム検索 |
| `!eroticcommissiontrackeragent remove <id>` | Remove item | アイテム削除 |

## Usage / 使用方法

\`\`\`
!eroticcommissiontrackeragent add Example content
!eroticcommissiontrackeragent list 10
!eroticcommissiontrackeragent search keyword
!eroticcommissiontrackeragent remove 1
\`\`\`

## Database / データベース

SQLite database. Data stored in `data/erotic-commission-tracker-agent.db`.

## License / ライセンス

MIT License
