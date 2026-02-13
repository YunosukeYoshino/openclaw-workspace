# rl-baseball-strategy-agent

RL野球戦略エージェント / RL Baseball Strategy Agent

野球戦略決定用RLモデルのトレーニング・応用を行うエージェント

Trains and applies RL models for baseball strategy decisions

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
| `!rlbaseballstrategyagent` | Main menu | メインメニュー |
| `!rlbaseballstrategyagent status` | Show status | ステータス表示 |
| `!rlbaseballstrategyagent add <content>` | Add item | アイテム追加 |
| `!rlbaseballstrategyagent list [limit]` | List items | アイテム一覧 |
| `!rlbaseballstrategyagent search <query>` | Search items | アイテム検索 |
| `!rlbaseballstrategyagent remove <id>` | Remove item | アイテム削除 |

## Usage / 使用方法

\`\`\`
!rlbaseballstrategyagent add Example content
!rlbaseballstrategyagent list 10
!rlbaseballstrategyagent search keyword
!rlbaseballstrategyagent remove 1
\`\`\`

## Database / データベース

SQLite database. Data stored in `data/rl-baseball-strategy-agent.db`.

## License / ライセンス

MIT License
