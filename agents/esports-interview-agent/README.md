# esports-interview-agent

eスポーツインタビューエージェント / Esports Interview Agent

選手インタビュー準備、質問生成、翻訳サポートを行うエージェント

Prepares player interviews, generates questions, and provides translation support

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
| `!esportsinterviewagent` | Main menu | メインメニュー |
| `!esportsinterviewagent status` | Show status | ステータス表示 |
| `!esportsinterviewagent add <content>` | Add item | アイテム追加 |
| `!esportsinterviewagent list [limit]` | List items | アイテム一覧 |
| `!esportsinterviewagent search <query>` | Search items | アイテム検索 |
| `!esportsinterviewagent remove <id>` | Remove item | アイテム削除 |

## Usage / 使用方法

\`\`\`
!esportsinterviewagent add Example content
!esportsinterviewagent list 10
!esportsinterviewagent search keyword
!esportsinterviewagent remove 1
\`\`\`

## Database / データベース

SQLite database. Data stored in `data/esports-interview-agent.db`.

## License / ライセンス

MIT License
