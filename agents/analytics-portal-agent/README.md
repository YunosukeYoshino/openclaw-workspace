# analytics-portal-agent

**Category**: データウェアハウス・BIエージェント
**Version**: V36 - Agent 25/25
**Status**: Active

## Overview

analytics-portal-agent is an AI-powered agent for データウェアハウス・BIエージェント.

## Features

- Intelligent content processing
- Persistent storage with SQLite
- Discord integration support
- RESTful API ready

## Installation

```bash
cd agents/analytics-portal-agent
pip install -r requirements.txt
```

## Usage

```python
from agent import AnalyticsPortal

agent = AnalyticsPortal()
await agent.run()
```

## Database

The agent uses SQLite for persistent storage. Database file: `analytics-portal-agent.db`

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
