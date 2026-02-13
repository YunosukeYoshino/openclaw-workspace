# baseball-career-tracker-agent

**Category**: 野球選手キャリア・引退エージェント
**Version**: V32 - Agent 1/25
**Status**: Active

## Overview

baseball-career-tracker-agent is an AI-powered agent for 野球選手キャリア・引退エージェント.

## Features

- Intelligent content processing
- Persistent storage with SQLite
- Discord integration support
- RESTful API ready

## Installation

```bash
cd agents/baseball-career-tracker-agent
pip install -r requirements.txt
```

## Usage

```python
from agent import BaseballCareerTracker

agent = BaseballCareerTracker()
await agent.run()
```

## Database

The agent uses SQLite for persistent storage. Database file: `baseball-career-tracker-agent.db`

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
