# data-lineage-agent

**Category**: データガバナンス・コンプライアンスエージェント
**Version**: V34 - Agent 23/25
**Status**: Active

## Overview

data-lineage-agent is an AI-powered agent for データガバナンス・コンプライアンスエージェント.

## Features

- Intelligent content processing
- Persistent storage with SQLite
- Discord integration support
- RESTful API ready

## Installation

```bash
cd agents/data-lineage-agent
pip install -r requirements.txt
```

## Usage

```python
from agent import DataLineage

agent = DataLineage()
await agent.run()
```

## Database

The agent uses SQLite for persistent storage. Database file: `data-lineage-agent.db`

### Schema

- `entries`: Main content storage
  - `id`: Primary key
  - `content`: Text content
  - `created_at`: Timestamp
  - `updated_at`: Timestamp

## Discord Integration

Set `DISCORD_TOKEN` environment variable to enable Discord features.

## License

MIT
