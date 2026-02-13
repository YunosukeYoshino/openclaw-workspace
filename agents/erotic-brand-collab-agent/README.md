# erotic-brand-collab-agent

えっちブランドコラボエージェント / Erotic Brand Collaboration Agent

ブランドコラボ企画、スポンサーシップ管理、PRキャンペーンを行うエージェント

Plans brand collaborations, manages sponsorships, and runs PR campaigns

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
| `!eroticbrandcollabagent` | Main menu | メインメニュー |
| `!eroticbrandcollabagent status` | Show status | ステータス表示 |
| `!eroticbrandcollabagent add <content>` | Add item | アイテム追加 |
| `!eroticbrandcollabagent list [limit]` | List items | アイテム一覧 |
| `!eroticbrandcollabagent search <query>` | Search items | アイテム検索 |
| `!eroticbrandcollabagent remove <id>` | Remove item | アイテム削除 |

## Usage / 使用方法

\`\`\`
!eroticbrandcollabagent add Example content
!eroticbrandcollabagent list 10
!eroticbrandcollabagent search keyword
!eroticbrandcollabagent remove 1
\`\`\`

## Database / データベース

SQLite database. Data stored in `data/erotic-brand-collab-agent.db`.

## License / ライセンス

MIT License
