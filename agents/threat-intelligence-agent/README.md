# 脅威インテリジェンスエージェント / Threat Intelligence Agent

外部の脅威インテリジェンスフィードを収集・分析するエージェント。

## Features

- {f}\n- {f}\n- {f}\n- {f}

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
from agent import ThreatIntelligenceAgent
from db import ThreatIntelligenceAgentDB

# Initialize agent
agent = ThreatIntelligenceAgent()

# Initialize database
db = ThreatIntelligenceAgentDB()

# Process data
result = agent.process({"input": "data"})
```

## Discord Commands

- `!threat-intelligence-agent_help` - Show help information
- `!threat-intelligence-agent_status` - Show agent status

## Database Schema

### entries

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| title | TEXT | Entry title |
| content | TEXT | Entry content |
| category | TEXT | Entry category |
| tags | TEXT | Tags (JSON) |
| status | TEXT | Entry status |
| created_at | TIMESTAMP | Creation timestamp |
| updated_at | TIMESTAMP | Last update timestamp |

## API Reference

### ThreatIntelligenceAgent

#### `process(input_data: Dict[str, Any]) -> Dict[str, Any]`

Process input data and return results.

**Parameters:**
- `input_data`: Dictionary containing input data

**Returns:**
- Dictionary containing processing results

**Actions:**
- `add`: Add a new entry
- `get`: Get an entry by ID
- `list`: List entries
- `update`: Update an entry
- `delete`: Delete an entry
- `search`: Search entries

## License

MIT License
