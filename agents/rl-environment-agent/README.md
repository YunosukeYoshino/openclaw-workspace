# rl-environment-agent

RL環境エージェント / RL Environment Agent

RLシミュレーション環境の構築・管理を行うエージェント

Builds and manages RL simulation environments

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
| `!rlenvironmentagent` | Main menu | メインメニュー |
| `!rlenvironmentagent status` | Show status | ステータス表示 |
| `!rlenvironmentagent add <content>` | Add item | アイテム追加 |
| `!rlenvironmentagent list [limit]` | List items | アイテム一覧 |
| `!rlenvironmentagent search <query>` | Search items | アイテム検索 |
| `!rlenvironmentagent remove <id>` | Remove item | アイテム削除 |

## Usage / 使用方法

\`\`\`
!rlenvironmentagent add Example content
!rlenvironmentagent list 10
!rlenvironmentagent search keyword
!rlenvironmentagent remove 1
\`\`\`

## Database / データベース

SQLite database. Data stored in `data/rl-environment-agent.db`.

## License / ライセンス

MIT License
