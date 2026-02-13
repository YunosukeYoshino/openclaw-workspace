# baseball-mental-fitness-agent

**Category**: 野球選手健康管理・フィジカルエージェント
**Version**: V36 - Agent 3/25
**Status**: Active

## Overview

baseball-mental-fitness-agent is an AI-powered agent for 野球選手健康管理・フィジカルエージェント.

## Features

- Intelligent content processing
- Persistent storage with SQLite
- Discord integration support
- RESTful API ready

## Installation

```bash
cd agents/baseball-mental-fitness-agent
pip install -r requirements.txt
```

## Usage

```python
from agent import BaseballMentalFitness

agent = BaseballMentalFitness()
await agent.run()
```

## Database

The agent uses SQLite for persistent storage. Database file: `baseball-mental-fitness-agent.db`

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
