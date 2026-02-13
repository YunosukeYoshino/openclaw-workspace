# baseball-draft-history-agent

野球ドラフト歴史エージェント / Baseball Draft History Agent

過去のドラフトデータ、選手追跡、ドラフト成功率分析を行うエージェント

Tracks past draft data, player careers, and analyzes draft success rates

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
| `!baseballdrafthistoryagent` | Main menu | メインメニュー |
| `!baseballdrafthistoryagent status` | Show status | ステータス表示 |
| `!baseballdrafthistoryagent add <content>` | Add item | アイテム追加 |
| `!baseballdrafthistoryagent list [limit]` | List items | アイテム一覧 |
| `!baseballdrafthistoryagent search <query>` | Search items | アイテム検索 |
| `!baseballdrafthistoryagent remove <id>` | Remove item | アイテム削除 |

## Usage / 使用方法

\`\`\`
!baseballdrafthistoryagent add Example content
!baseballdrafthistoryagent list 10
!baseballdrafthistoryagent search keyword
!baseballdrafthistoryagent remove 1
\`\`\`

## Database / データベース

SQLite database. Data stored in `data/baseball-draft-history-agent.db`.

## License / ライセンス

MIT License
