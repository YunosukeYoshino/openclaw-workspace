# esports-play-by-play-agent

eスポーツ実況エージェント / Esports Play-by-Play Agent

リアルタイム実況生成、ハイライト検出、ストーリーテリングを行うエージェント

Generates real-time commentary, detects highlights, and provides storytelling

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
| `!esportsplaybyplayagent` | Main menu | メインメニュー |
| `!esportsplaybyplayagent status` | Show status | ステータス表示 |
| `!esportsplaybyplayagent add <content>` | Add item | アイテム追加 |
| `!esportsplaybyplayagent list [limit]` | List items | アイテム一覧 |
| `!esportsplaybyplayagent search <query>` | Search items | アイテム検索 |
| `!esportsplaybyplayagent remove <id>` | Remove item | アイテム削除 |

## Usage / 使用方法

\`\`\`
!esportsplaybyplayagent add Example content
!esportsplaybyplayagent list 10
!esportsplaybyplayagent search keyword
!esportsplaybyplayagent remove 1
\`\`\`

## Database / データベース

SQLite database. Data stored in `data/esports-play-by-play-agent.db`.

## License / ライセンス

MIT License
