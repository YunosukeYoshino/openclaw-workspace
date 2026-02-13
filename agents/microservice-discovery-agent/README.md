# microservice-discovery-agent

**Category**: マイクロサービス・サービスメッシュエージェント
**Version**: V36 - Agent 16/25
**Status**: Active

## Overview

microservice-discovery-agent is an AI-powered agent for マイクロサービス・サービスメッシュエージェント.

## Features

- Intelligent content processing
- Persistent storage with SQLite
- Discord integration support
- RESTful API ready

## Installation

```bash
cd agents/microservice-discovery-agent
pip install -r requirements.txt
```

## Usage

```python
from agent import MicroserviceDiscovery

agent = MicroserviceDiscovery()
await agent.run()
```

## Database

The agent uses SQLite for persistent storage. Database file: `microservice-discovery-agent.db`

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
