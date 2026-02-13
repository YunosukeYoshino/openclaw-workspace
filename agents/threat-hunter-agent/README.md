# threat-hunter-agent

**Category**: セキュリティインシデント・脅威対応エージェント
**Version**: V33 - Agent 22/25
**Status**: Active

## Overview

threat-hunter-agent is an AI-powered agent for セキュリティインシデント・脅威対応エージェント.

## Features

- Intelligent content processing
- Persistent storage with SQLite
- Discord integration support
- RESTful API ready

## Installation

```bash
cd agents/threat-hunter-agent
pip install -r requirements.txt
```

## Usage

```python
from agent import ThreatHunter

agent = ThreatHunter()
await agent.run()
```

## Database

The agent uses SQLite for persistent storage. Database file: `threat-hunter-agent.db`

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
