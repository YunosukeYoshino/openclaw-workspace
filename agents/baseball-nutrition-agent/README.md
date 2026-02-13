# baseball-nutrition-agent

**Category**: 野球選手健康管理・フィジカルエージェント
**Version**: V36 - Agent 2/25
**Status**: Active

## Overview

baseball-nutrition-agent is an AI-powered agent for 野球選手健康管理・フィジカルエージェント.

## Features

- Intelligent content processing
- Persistent storage with SQLite
- Discord integration support
- RESTful API ready

## Installation

```bash
cd agents/baseball-nutrition-agent
pip install -r requirements.txt
```

## Usage

```python
from agent import BaseballNutrition

agent = BaseballNutrition()
await agent.run()
```

## Database

The agent uses SQLite for persistent storage. Database file: `baseball-nutrition-agent.db`

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
