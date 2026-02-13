# event-sourcing-agent

**Category**: サーバーレスイベント駆動アーキテクチャエージェント
**Version**: V35 - Agent 18/25
**Status**: Active

## Overview

event-sourcing-agent is an AI-powered agent for サーバーレスイベント駆動アーキテクチャエージェント.

## Features

- Intelligent content processing
- Persistent storage with SQLite
- Discord integration support
- RESTful API ready

## Installation

```bash
cd agents/event-sourcing-agent
pip install -r requirements.txt
```

## Usage

```python
from agent import EventSourcing

agent = EventSourcing()
await agent.run()
```

## Database

The agent uses SQLite for persistent storage. Database file: `event-sourcing-agent.db`

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
