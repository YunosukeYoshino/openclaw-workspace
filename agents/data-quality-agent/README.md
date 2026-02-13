# data-quality-agent

データ品質エージェント / Data Quality Agent

データ品質チェック、異常検知、自動修正を行うエージェント

Checks data quality, detects anomalies, and performs automatic fixes

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
| `!dataqualityagent` | Main menu | メインメニュー |
| `!dataqualityagent status` | Show status | ステータス表示 |
| `!dataqualityagent add <content>` | Add item | アイテム追加 |
| `!dataqualityagent list [limit]` | List items | アイテム一覧 |
| `!dataqualityagent search <query>` | Search items | アイテム検索 |
| `!dataqualityagent remove <id>` | Remove item | アイテム削除 |

## Usage / 使用方法

\`\`\`
!dataqualityagent add Example content
!dataqualityagent list 10
!dataqualityagent search keyword
!dataqualityagent remove 1
\`\`\`

## Database / データベース

SQLite database. Data stored in `data/data-quality-agent.db`.

## License / ライセンス

MIT License
