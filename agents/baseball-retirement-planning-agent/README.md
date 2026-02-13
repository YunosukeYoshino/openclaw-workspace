# baseball-retirement-planning-agent

**Category**: 野球選手キャリア・引退エージェント
**Version**: V32 - Agent 2/25
**Status**: Active

## Overview

baseball-retirement-planning-agent is an AI-powered agent for 野球選手キャリア・引退エージェント.

## Features

- Intelligent content processing
- Persistent storage with SQLite
- Discord integration support
- RESTful API ready

## Installation

```bash
cd agents/baseball-retirement-planning-agent
pip install -r requirements.txt
```

## Usage

```python
from agent import BaseballRetirementPlanning

agent = BaseballRetirementPlanning()
await agent.run()
```

## Database

The agent uses SQLite for persistent storage. Database file: `baseball-retirement-planning-agent.db`

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
