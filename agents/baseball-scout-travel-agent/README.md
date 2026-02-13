# baseball-scout-travel-agent

野球スカウト移動エージェント / Baseball Scout Travel Agent

スカウト移動スケジュール、試合視聴計画、候補選手追跡を管理するエージェント

Manages scout travel schedules, game viewing plans, and prospect tracking

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
| `!baseballscouttravelagent` | Main menu | メインメニュー |
| `!baseballscouttravelagent status` | Show status | ステータス表示 |
| `!baseballscouttravelagent add <content>` | Add item | アイテム追加 |
| `!baseballscouttravelagent list [limit]` | List items | アイテム一覧 |
| `!baseballscouttravelagent search <query>` | Search items | アイテム検索 |
| `!baseballscouttravelagent remove <id>` | Remove item | アイテム削除 |

## Usage / 使用方法

\`\`\`
!baseballscouttravelagent add Example content
!baseballscouttravelagent list 10
!baseballscouttravelagent search keyword
!baseballscouttravelagent remove 1
\`\`\`

## Database / データベース

SQLite database. Data stored in `data/baseball-scout-travel-agent.db`.

## License / ライセンス

MIT License
