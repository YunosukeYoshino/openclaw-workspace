# esports-cast-planner-agent

eスポーツ配信計画エージェント / Esports Cast Planner Agent

配信スケジュール、キャスト担当割り当て、機材管理を行うエージェント

Manages broadcast schedules, caster assignments, and equipment management

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
| `!esportscastplanneragent` | Main menu | メインメニュー |
| `!esportscastplanneragent status` | Show status | ステータス表示 |
| `!esportscastplanneragent add <content>` | Add item | アイテム追加 |
| `!esportscastplanneragent list [limit]` | List items | アイテム一覧 |
| `!esportscastplanneragent search <query>` | Search items | アイテム検索 |
| `!esportscastplanneragent remove <id>` | Remove item | アイテム削除 |

## Usage / 使用方法

\`\`\`
!esportscastplanneragent add Example content
!esportscastplanneragent list 10
!esportscastplanneragent search keyword
!esportscastplanneragent remove 1
\`\`\`

## Database / データベース

SQLite database. Data stored in `data/esports-cast-planner-agent.db`.

## License / ライセンス

MIT License
