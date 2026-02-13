# pipeline-orchestrator-agent

パイプラインオーケストレーターエージェント / Pipeline Orchestrator Agent

データパイプラインの実行管理・スケジューリングを行うエージェント

Manages and schedules data pipeline executions

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
| `!pipelineorchestratoragent` | Main menu | メインメニュー |
| `!pipelineorchestratoragent status` | Show status | ステータス表示 |
| `!pipelineorchestratoragent add <content>` | Add item | アイテム追加 |
| `!pipelineorchestratoragent list [limit]` | List items | アイテム一覧 |
| `!pipelineorchestratoragent search <query>` | Search items | アイテム検索 |
| `!pipelineorchestratoragent remove <id>` | Remove item | アイテム削除 |

## Usage / 使用方法

\`\`\`
!pipelineorchestratoragent add Example content
!pipelineorchestratoragent list 10
!pipelineorchestratoragent search keyword
!pipelineorchestratoragent remove 1
\`\`\`

## Database / データベース

SQLite database. Data stored in `data/pipeline-orchestrator-agent.db`.

## License / ライセンス

MIT License
