# Cleanup Agent / クリーンアップエージェント

A Discord bot agent for managing scheduled cleanup tasks, file retention policies, and automated disk maintenance.

## Features / 機能

- **Cleanup Task Management / クリーンアップタスク管理**: Create and schedule cleanup tasks for files, folders, logs, cache, and custom patterns
- **Flexible Scheduling / 柔軟なスケジュール**: Set up daily, weekly, monthly, or interval-based schedules
- **Retention Policies / 保持ポリシー**: Define retention periods (days) for automated cleanup
- **Exclusion Rules / 除外ルール**: Configure patterns to exclude specific files or directories
- **Execution History / 実行履歴**: Track cleanup runs with statistics on processed and deleted items
- **Space Tracking / 空間追跡**: Monitor total space freed over time

## Installation / インストール

```bash
pip install -r requirements.txt
```

## Usage / 使い方

### Commands / コマンド

#### `!cleanup` - Add Cleanup Task
```
!cleanup temp_files, パス: /tmp, タイプ: temp, 保持期間: 7日
!cleanup log_cleanup, パス: /var/log, タイプ: logs, 保持期間: 30日, スケジュール: 毎日 02:00
!cleanup cache_cleanup, タイプ: cache, スケジュール: 毎週 日曜日 03:00
!cleanup custom_cleanup, パターン: *.tmp, スケジュール: 毎月 1日 00:00
```

#### `!list_cleanup` - List All Tasks
```
!list_cleanup
```
Display all cleanup tasks with their status.

#### `!active_cleanup` - List Enabled Tasks
```
!active_cleanup
```
Show only enabled cleanup tasks.

#### `!detail` - View Task Details
```
!detail 1
```
View detailed information about a specific task including exclusion rules.

#### `!toggle` - Enable/Disable Task
```
!toggle 1
```
Toggle the enabled/disabled status of a task.

#### `!history` - View Execution History
```
!history
!history 20
```
Display cleanup execution history (default: 10 entries).

#### `!exclude` - Add Exclusion Rule
```
!exclude 1, *.important
!exclude 2, /preserve/
```
Add an exclusion rule to a task to skip matching files.

#### `!list_exclusion` - List Exclusion Rules
```
!list_exclusion 1
```
View exclusion rules for a specific task.

#### `!delete` - Delete Task
```
!delete 1
```
Delete a cleanup task and all its history.

#### `!stats` - View Statistics
```
!stats
```
Display overall cleanup statistics including tasks, runs, and space freed.

## Cleanup Types / クリーンアップタイプ

- `files` - Generic file cleanup
- `folders` - Remove entire directories
- `temp` - Temporary file cleanup
- `logs` - Log file rotation/cleanup
- `cache` - Cache directory cleanup
- `custom` - Custom pattern matching

## Schedule Formats / スケジュール形式

- `毎日 02:00` - Daily at 2 AM
- `毎週 日曜日 03:00` - Weekly on Sunday at 3 AM
- `毎月 1日 00:00` - Monthly on the 1st at midnight
- `1時間` - Every 1 hour
- `30分` - Every 30 minutes

## Running the Bot / ボットの実行

```python
import discord
from discord.ext import commands
from agent import CleanupAgent

bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())
bot.add_cog(CleanupAgent(bot))

# Replace with your token
bot.run('YOUR_BOT_TOKEN')
```

## Database Schema / データベース構造

- `cleanup_tasks`: Stores cleanup task definitions
- `cleanup_history`: Execution history with statistics
- `exclusion_rules`: Exclusion patterns for each task

## Requirements / 要件

- Python 3.8+
- discord.py 2.0+

## License / ライセンス

MIT
