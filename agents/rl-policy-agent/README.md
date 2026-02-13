# rl-policy-agent

RLポリシーエージェント / RL Policy Agent

RLポリシーの評価・比較・最適化を行うエージェント

Evaluates, compares, and optimizes RL policies

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
| `!rlpolicyagent` | Main menu | メインメニュー |
| `!rlpolicyagent status` | Show status | ステータス表示 |
| `!rlpolicyagent add <content>` | Add item | アイテム追加 |
| `!rlpolicyagent list [limit]` | List items | アイテム一覧 |
| `!rlpolicyagent search <query>` | Search items | アイテム検索 |
| `!rlpolicyagent remove <id>` | Remove item | アイテム削除 |

## Usage / 使用方法

\`\`\`
!rlpolicyagent add Example content
!rlpolicyagent list 10
!rlpolicyagent search keyword
!rlpolicyagent remove 1
\`\`\`

## Database / データベース

SQLite database. Data stored in `data/rl-policy-agent.db`.

## License / ライセンス

MIT License
