# baseball-legacy-manager-agent

**Category**: 野球選手キャリア・引退エージェント
**Version**: V32 - Agent 5/25
**Status**: Active

## Overview

baseball-legacy-manager-agent is an AI-powered agent for 野球選手キャリア・引退エージェント.

## Features

- Intelligent content processing
- Persistent storage with SQLite
- Discord integration support
- RESTful API ready

## Installation

```bash
cd agents/baseball-legacy-manager-agent
pip install -r requirements.txt
```

## Usage

```python
from agent import BaseballLegacyManager

agent = BaseballLegacyManager()
await agent.run()
```

## Database

The agent uses SQLite for persistent storage. Database file: `baseball-legacy-manager-agent.db`

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
