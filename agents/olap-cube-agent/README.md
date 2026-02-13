# olap-cube-agent

**Category**: データウェアハウス・BIエージェント
**Version**: V36 - Agent 23/25
**Status**: Active

## Overview

olap-cube-agent is an AI-powered agent for データウェアハウス・BIエージェント.

## Features

- Intelligent content processing
- Persistent storage with SQLite
- Discord integration support
- RESTful API ready

## Installation

```bash
cd agents/olap-cube-agent
pip install -r requirements.txt
```

## Usage

```python
from agent import OlapCube

agent = OlapCube()
await agent.run()
```

## Database

The agent uses SQLite for persistent storage. Database file: `olap-cube-agent.db`

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
