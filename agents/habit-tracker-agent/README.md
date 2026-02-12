# habit-tracker-agent

habit tracker トラッカーは、habit-trackerの記録と追跡を管理するAIエージェントです。

## Features

- habit trackerの記録
- 統計情報の表示
- 履歴管理
- 検索・フィルタ機能

## Installation

```bash
cd agents/habit-tracker-agent
pip install -r requirements.txt
```

## Usage

### Discord Botとして実行

```bash
python discord.py
```

### データベース操作

```python
from db import habit_tracker_agentDB

db = habit_tracker_agentDB()
db.add_record({'field1': 'value1', 'field2': 'value2'})
records = db.get_all_records()
```

## Database Schema

The agent uses SQLite with the following schema:

```sql
CREATE TABLE habit_tracker_agent (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Natural Language Commands

The agent supports the following natural language commands (via Discord):

- "Add habit tracker record"
- "Show my habit tracker history"
- "List recent habit tracker entries"

## Configuration

Configuration is stored in `config.json`:

```json
{
    "database_path": "habit-tracker-agent.db",
    "log_level": "INFO"
}
```

## Requirements

See `requirements.txt` for dependencies.

## License

MIT License
