# rl-game-agent

RLゲームエージェント / RL Game Agent

ゲームAI用RLモデルのトレーニング・デプロイを行うエージェント

Trains and deploys RL models for game AI

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
| `!rlgameagent` | Main menu | メインメニュー |
| `!rlgameagent status` | Show status | ステータス表示 |
| `!rlgameagent add <content>` | Add item | アイテム追加 |
| `!rlgameagent list [limit]` | List items | アイテム一覧 |
| `!rlgameagent search <query>` | Search items | アイテム検索 |
| `!rlgameagent remove <id>` | Remove item | アイテム削除 |

## Usage / 使用方法

\`\`\`
!rlgameagent add Example content
!rlgameagent list 10
!rlgameagent search keyword
!rlgameagent remove 1
\`\`\`

## Database / データベース

SQLite database. Data stored in `data/rl-game-agent.db`.

## License / ライセンス

MIT License
