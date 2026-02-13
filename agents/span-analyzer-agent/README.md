# span-analyzer-agent

**Category**: 分散トレーシング・オブザーバビリティエージェント
**Version**: V32 - Agent 18/25
**Status**: Active

## Overview

span-analyzer-agent is an AI-powered agent for 分散トレーシング・オブザーバビリティエージェント.

## Features

- Intelligent content processing
- Persistent storage with SQLite
- Discord integration support
- RESTful API ready

## Installation

```bash
cd agents/span-analyzer-agent
pip install -r requirements.txt
```

## Usage

```python
from agent import SpanAnalyzer

agent = SpanAnalyzer()
await agent.run()
```

## Database

The agent uses SQLite for persistent storage. Database file: `span-analyzer-agent.db`

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
