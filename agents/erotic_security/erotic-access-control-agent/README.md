# えっちアクセス制御エージェント / Erotic Access Control Agent

年齢認証、アクセス権限管理、コンテンツ保護機能を提供します。

## Features

- 年齢認証システム
- ユーザーレベルに応じたアクセス制御
- 地域別コンテンツ規制対応
- 不正アクセス検知

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Command Line

```bash
python agent.py
python db.py
python discord.py
```

### As Module

```python
from agent import EroticAccessControlAgent
from db import EroticAccessControlAgentDB

# Initialize agent
agent = EroticAccessControlAgent()

# Initialize database
db = EroticAccessControlAgentDB()

# Process data
result = await agent.process({"input": "data"})
```

## Discord Commands

- `!erotic-access-control-agent_help` - Show help information
- `!erotic-access-control-agent_status` - Show agent status

## Database Schema

### entries

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| title | TEXT | Entry title |
| content | TEXT | Entry content |
| metadata | TEXT | Additional metadata (JSON) |
| status | TEXT | Entry status (active/archived/completed) |
| created_at | TIMESTAMP | Creation timestamp |
| updated_at | TIMESTAMP | Last update timestamp |

### tags

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| name | TEXT | Tag name (unique) |

### entry_tags

| Column | Type | Description |
|--------|------|-------------|
| entry_id | INTEGER | Reference to entries.id |
| tag_id | INTEGER | Reference to tags.id |

## API Reference

### EroticAccessControlAgent

#### `process(input_data: Dict[str, Any]) -> Dict[str, Any]`

Process input data and return results.

**Parameters:**
- `input_data`: Dictionary containing input data

**Returns:**
- Dictionary with processing results

#### `get_features() -> List[str]`

Return list of available features.

**Returns:**
- List of feature names

### EroticAccessControlAgentDB

#### `add_entry(title, content, metadata=None, tags=None) -> int`

Add a new entry to the database.

**Parameters:**
- `title`: Entry title
- `content`: Entry content
- `metadata`: Optional metadata (JSON string)
- `tags`: Optional list of tag names

**Returns:**
- ID of the created entry

#### `get_entries(status=None, limit=100) -> List[Dict[str, Any]]`

Retrieve entries from the database.

**Parameters:**
- `status`: Optional filter by status
- `limit`: Maximum number of entries to return

**Returns:**
- List of entry dictionaries

#### `update_entry_status(entry_id, status) -> bool`

Update the status of an entry.

**Parameters:**
- `entry_id`: ID of the entry to update
- `status`: New status value

**Returns:**
- True if update was successful

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - see LICENSE file for details.
