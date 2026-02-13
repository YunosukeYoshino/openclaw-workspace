# rl-training-agent

強化学習トレーニングエージェント / RL Training Agent

RLモデルのトレーニング、ハイパーパラメータ最適化を行うエージェント

Trains RL models and optimizes hyperparameters

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
| `!rltrainingagent` | Main menu | メインメニュー |
| `!rltrainingagent status` | Show status | ステータス表示 |
| `!rltrainingagent add <content>` | Add item | アイテム追加 |
| `!rltrainingagent list [limit]` | List items | アイテム一覧 |
| `!rltrainingagent search <query>` | Search items | アイテム検索 |
| `!rltrainingagent remove <id>` | Remove item | アイテム削除 |

## Usage / 使用方法

\`\`\`
!rltrainingagent add Example content
!rltrainingagent list 10
!rltrainingagent search keyword
!rltrainingagent remove 1
\`\`\`

## Database / データベース

SQLite database. Data stored in `data/rl-training-agent.db`.

## License / ライセンス

MIT License
