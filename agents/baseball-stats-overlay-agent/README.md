# baseball-stats-overlay-agent

**Category**: 野球ライブ中継・コメンタリーエージェント
**Version**: V35 - Agent 3/25
**Status**: Active

## Overview

baseball-stats-overlay-agent is an AI-powered agent for 野球ライブ中継・コメンタリーエージェント.

## Features

- Intelligent content processing
- Persistent storage with SQLite
- Discord integration support
- RESTful API ready

## Installation

```bash
cd agents/baseball-stats-overlay-agent
pip install -r requirements.txt
```

## Usage

```python
from agent import BaseballStatsOverlay

agent = BaseballStatsOverlay()
await agent.run()
```

## Database

The agent uses SQLite for persistent storage. Database file: `baseball-stats-overlay-agent.db`

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
