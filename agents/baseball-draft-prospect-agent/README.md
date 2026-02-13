# baseball-draft-prospect-agent

野球ドラフト候補エージェント / Baseball Draft Prospect Agent

ドラフト候補選手の評価、レポート作成、順位予想を行うエージェント

Evaluates draft prospects, creates reports, and predicts draft order

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
| `!baseballdraftprospectagent` | Main menu | メインメニュー |
| `!baseballdraftprospectagent status` | Show status | ステータス表示 |
| `!baseballdraftprospectagent add <content>` | Add item | アイテム追加 |
| `!baseballdraftprospectagent list [limit]` | List items | アイテム一覧 |
| `!baseballdraftprospectagent search <query>` | Search items | アイテム検索 |
| `!baseballdraftprospectagent remove <id>` | Remove item | アイテム削除 |

## Usage / 使用方法

\`\`\`
!baseballdraftprospectagent add Example content
!baseballdraftprospectagent list 10
!baseballdraftprospectagent search keyword
!baseballdraftprospectagent remove 1
\`\`\`

## Database / データベース

SQLite database. Data stored in `data/baseball-draft-prospect-agent.db`.

## License / ライセンス

MIT License
