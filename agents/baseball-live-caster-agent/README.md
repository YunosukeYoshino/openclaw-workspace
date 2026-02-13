# baseball-live-caster-agent

**Category**: 野球ライブ中継・コメンタリーエージェント
**Version**: V35 - Agent 1/25
**Status**: Active

## Overview

baseball-live-caster-agent is an AI-powered agent for 野球ライブ中継・コメンタリーエージェント.

## Features

- Intelligent content processing
- Persistent storage with SQLite
- Discord integration support
- RESTful API ready

## Installation

```bash
cd agents/baseball-live-caster-agent
pip install -r requirements.txt
```

## Usage

```python
from agent import BaseballLiveCaster

agent = BaseballLiveCaster()
await agent.run()
```

## Database

The agent uses SQLite for persistent storage. Database file: `baseball-live-caster-agent.db`

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
