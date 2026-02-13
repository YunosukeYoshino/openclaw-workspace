# baseball-athlete-health-agent

**Category**: 野球選手健康管理・フィジカルエージェント
**Version**: V36 - Agent 1/25
**Status**: Active

## Overview

baseball-athlete-health-agent is an AI-powered agent for 野球選手健康管理・フィジカルエージェント.

## Features

- Intelligent content processing
- Persistent storage with SQLite
- Discord integration support
- RESTful API ready

## Installation

```bash
cd agents/baseball-athlete-health-agent
pip install -r requirements.txt
```

## Usage

```python
from agent import BaseballAthleteHealth

agent = BaseballAthleteHealth()
await agent.run()
```

## Database

The agent uses SQLite for persistent storage. Database file: `baseball-athlete-health-agent.db`

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
