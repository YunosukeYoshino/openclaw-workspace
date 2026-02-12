# calendar-integration-agent

calendar integration agentは、calendarintegrationの管理と追跡を行うAIエージェントです。

## Features

- calendar integrationの記録
- 統計情報の表示
- 履歴管理
- 検索・フィルタ機能

## Installation

```bash
cd agents/calendar-integration-agent
pip install -r requirements.txt
```

## Usage

### Discord Botとして実行

```bash
python discord.py
```

### データベース操作

```python
from db import calendar_integration_agentDB

db = calendar_integration_agentDB()
db.add_record({'field1': 'value1', 'field2': 'value2'})
records = db.get_all_records()
```

## Database Schema

The agent uses SQLite with the following schema:

```sql
CREATE TABLE calendar_integration_agent (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Natural Language Commands

The agent supports the following natural language commands (via Discord):

- "Add calendar integration record"
- "Show my calendar integration history"
- "List recent calendar integration entries"

## Configuration

Configuration is stored in `config.json`:

```json
{
    "database_path": "calendar-integration-agent.db",
    "log_level": "INFO"
}
```

## Requirements

See `requirements.txt` for dependencies.

## License

MIT License
