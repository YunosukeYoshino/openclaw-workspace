# esports-viewer-engagement-agent

eスポーツ視聴者エンゲージメントエージェント / Esports Viewer Engagement Agent

チャット分析、視聴者投票、リアクション追跡を行うエージェント

Analyzes chats, manages viewer polls, and tracks reactions

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
| `!esportsviewerengagementagent` | Main menu | メインメニュー |
| `!esportsviewerengagementagent status` | Show status | ステータス表示 |
| `!esportsviewerengagementagent add <content>` | Add item | アイテム追加 |
| `!esportsviewerengagementagent list [limit]` | List items | アイテム一覧 |
| `!esportsviewerengagementagent search <query>` | Search items | アイテム検索 |
| `!esportsviewerengagementagent remove <id>` | Remove item | アイテム削除 |

## Usage / 使用方法

\`\`\`
!esportsviewerengagementagent add Example content
!esportsviewerengagementagent list 10
!esportsviewerengagementagent search keyword
!esportsviewerengagementagent remove 1
\`\`\`

## Database / データベース

SQLite database. Data stored in `data/esports-viewer-engagement-agent.db`.

## License / ライセンス

MIT License
