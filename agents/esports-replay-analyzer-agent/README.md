# esports-replay-analyzer-agent

eスポーツリプレイ分析エージェント / Esports Replay Analyzer Agent

リプレイ分析、プレイ解説、戦術図作成を行うエージェント

Analyzes replays, explains plays, and creates tactical diagrams

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
| `!esportsreplayanalyzeragent` | Main menu | メインメニュー |
| `!esportsreplayanalyzeragent status` | Show status | ステータス表示 |
| `!esportsreplayanalyzeragent add <content>` | Add item | アイテム追加 |
| `!esportsreplayanalyzeragent list [limit]` | List items | アイテム一覧 |
| `!esportsreplayanalyzeragent search <query>` | Search items | アイテム検索 |
| `!esportsreplayanalyzeragent remove <id>` | Remove item | アイテム削除 |

## Usage / 使用方法

\`\`\`
!esportsreplayanalyzeragent add Example content
!esportsreplayanalyzeragent list 10
!esportsreplayanalyzeragent search keyword
!esportsreplayanalyzeragent remove 1
\`\`\`

## Database / データベース

SQLite database. Data stored in `data/esports-replay-analyzer-agent.db`.

## License / ライセンス

MIT License
