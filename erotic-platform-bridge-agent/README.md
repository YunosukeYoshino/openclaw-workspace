# erotic-platform-bridge-agent

えっちプラットフォームブリッジエージェント。プラットフォーム間の機能ブリッジ。

Erotic platform bridge agent. Bridge features between platforms.

## Description

このエージェントは以下のスキルを持っています：
- bridge
- platform
- integration

カテゴリー: erotic

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

```python
from agent import EroticPlatformBridgeAgentAgent

agent = EroticPlatformBridgeAgentAgent()

# タスクを追加
task_id = agent.add_task(
    title="Example task",
    description="This is an example task",
    priority=1
)

# タスクを取得
tasks = agent.get_tasks()
print(tasks)

# 統計情報を取得
stats = agent.get_stats()
print(stats)
```

### Discord Integration

```python
from discord import DiscordBot

bot = DiscordBot(token="YOUR_TOKEN", channel_id="YOUR_CHANNEL_ID")
await bot.connect()
await bot.send_message("Hello from erotic-platform-bridge-agent")
```

## API Reference

### Agent Methods

- `__init__(db_path: str = None)` - エージェントを初期化
- `add_task(title: str, description: str = None, priority: int = 0)` - タスクを追加
- `get_tasks(status: str = None)` - タスクを取得
- `update_task_status(task_id: int, status: str)` - タスクのステータスを更新
- `log_event(event_type: str, data: Dict[str, Any] = None)` - イベントをログ
- `get_stats()` - 統計情報を取得

### Database Methods

- `__init__(db_path: str = None)` - データベース接続を初期化
- `init_database()` - データベースを初期化
- `execute_query(query: str, params: tuple = ())` - クエリを実行
- `execute_update(query: str, params: tuple = ())` - 更新クエリを実行

### Discord Methods

- `__init__(token: str = None, channel_id: str = None)` - ボットを初期化
- `connect()` - Discordに接続
- `send_message(message: str, embed: Dict[str, Any] = None)` - メッセージを送信
- `send_embed(title: str, description: str, fields: List[Dict[str, Any]] = None)` - 埋め込みメッセージを送信
- `notify_task_created(task_id: int, title: str)` - タスク作成を通知
- `notify_task_completed(task_id: int, title: str)` - タスク完了を通知
- `notify_error(error: str)` - エラーを通知

## Database Schema

### tasks table

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary Key |
| title | TEXT | Task title |
| description | TEXT | Task description |
| status | TEXT | Task status (pending/completed) |
| priority | INTEGER | Task priority |
| created_at | TIMESTAMP | Creation timestamp |
| updated_at | TIMESTAMP | Update timestamp |

### events table

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary Key |
| event_type | TEXT | Event type |
| data | TEXT | Event data (JSON) |
| created_at | TIMESTAMP | Creation timestamp |

## License

MIT License
