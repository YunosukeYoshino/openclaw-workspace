# jwt-handler-agent

**Category**: セキュリティ認証・認可管理エージェント
**Version**: V35 - Agent 24/25
**Status**: Active

## Overview

jwt-handler-agent is an AI-powered agent for セキュリティ認証・認可管理エージェント.

## Features

- Intelligent content processing
- Persistent storage with SQLite
- Discord integration support
- RESTful API ready

## Installation

```bash
cd agents/jwt-handler-agent
pip install -r requirements.txt
```

## Usage

```python
from agent import JwtHandler

agent = JwtHandler()
await agent.run()
```

## Database

The agent uses SQLite for persistent storage. Database file: `jwt-handler-agent.db`

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
