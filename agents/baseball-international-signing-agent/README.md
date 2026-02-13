# baseball-international-signing-agent

野球国際契約エージェント / Baseball International Signing Agent

外国人選手の契約管理、国際スカウティング、規則適合チェックを行うエージェント

Manages foreign player contracts, international scouting, and compliance checks

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
| `!baseballinternationalsigningagent` | Main menu | メインメニュー |
| `!baseballinternationalsigningagent status` | Show status | ステータス表示 |
| `!baseballinternationalsigningagent add <content>` | Add item | アイテム追加 |
| `!baseballinternationalsigningagent list [limit]` | List items | アイテム一覧 |
| `!baseballinternationalsigningagent search <query>` | Search items | アイテム検索 |
| `!baseballinternationalsigningagent remove <id>` | Remove item | アイテム削除 |

## Usage / 使用方法

\`\`\`
!baseballinternationalsigningagent add Example content
!baseballinternationalsigningagent list 10
!baseballinternationalsigningagent search keyword
!baseballinternationalsigningagent remove 1
\`\`\`

## Database / データベース

SQLite database. Data stored in `data/baseball-international-signing-agent.db`.

## License / ライセンス

MIT License
