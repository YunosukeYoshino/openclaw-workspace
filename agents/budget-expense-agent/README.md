# budget-expense-agent

budget expense agentは、budgetexpenseの管理と追跡を行うAIエージェントです。

## Features

- budget expenseの記録
- 統計情報の表示
- 履歴管理
- 検索・フィルタ機能

## Installation

```bash
cd agents/budget-expense-agent
pip install -r requirements.txt
```

## Usage

### Discord Botとして実行

```bash
python discord.py
```

### データベース操作

```python
from db import budget_expense_agentDB

db = budget_expense_agentDB()
db.add_record({'field1': 'value1', 'field2': 'value2'})
records = db.get_all_records()
```

## Database Schema

The agent uses SQLite with the following schema:

```sql
CREATE TABLE budget_expense_agent (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Natural Language Commands

The agent supports the following natural language commands (via Discord):

- "Add budget expense record"
- "Show my budget expense history"
- "List recent budget expense entries"

## Configuration

Configuration is stored in `config.json`:

```json
{
    "database_path": "budget-expense-agent.db",
    "log_level": "INFO"
}
```

## Requirements

See `requirements.txt` for dependencies.

## License

MIT License
