# Automation Agent / 自動化エージェント

A Discord bot agent for task automation, workflow creation, and trigger management.

## Features / 機能

- **Task Automation / タスク自動化**: Create and manage automated tasks
- **Workflow Creation / ワークフロー作成**: Build multi-step workflows
- **Trigger Management / トリガー管理**: Set up triggers to automate execution
- **Execution Tracking / 実行追跡**: Monitor task and workflow executions
- **Statistics / 統計**: View automation metrics and performance

## Installation / インストール

```bash
pip install -r requirements.txt
```

## Usage / 使い方

### Commands / コマンド

#### `!task` - Task Management
```
!task create backup scheduled {"interval": "daily", "time": "02:00"}
!task list
!task info 1
!task enable 1
!task disable 1
```

#### `!workflow` - Workflow Management
```
!workflow create deploy_process [{"step": "build"}, {"step": "test"}, {"step": "deploy"}]
!workflow list
```

#### `!trigger` - Trigger Management
```
!trigger create daily_backup schedule {"time": "02:00", "days": ["mon", "wed", "fri"]} 1
!trigger list
```

#### `!run` - Execute Tasks/Workflows
```
!run task 1
!run workflow 1
```

#### `!stats` - View Statistics
```
!stats
```

## Task Types / タスクタイプ

Common task types:
- `scheduled` - Scheduled tasks with intervals
- `command` - Execute shell commands
- `api_call` - Make HTTP requests
- `script` - Run custom scripts
- `notification` - Send notifications

## Trigger Types / トリガータイプ

- `schedule` - Time-based triggers
- `event` - Event-based triggers
- `webhook` - HTTP webhook triggers
- `manual` - Manual execution

## Running the Bot / ボットの実行

```python
import discord
from discord.ext import commands
from agent import AutomationAgent

bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())
bot.add_cog(AutomationAgent(bot))

# Replace with your token
bot.run('YOUR_BOT_TOKEN')
```

## Database Schema / データベース構造

- `tasks`: Automation tasks
- `workflows`: Multi-step workflows
- `triggers`: Triggers for automation
- `executions`: Execution logs

## Requirements / 要件

- Python 3.8+
- discord.py 2.0+

## License / ライセンス

MIT
