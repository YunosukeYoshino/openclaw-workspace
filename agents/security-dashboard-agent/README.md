# security-dashboard-agent

**Category**: セキュリティインシデント・脅威対応エージェント
**Version**: V33 - Agent 25/25
**Status**: Active

## Overview

security-dashboard-agent is an AI-powered agent for セキュリティインシデント・脅威対応エージェント.

## Features

- Intelligent content processing
- Persistent storage with SQLite
- Discord integration support
- RESTful API ready

## Installation

```bash
cd agents/security-dashboard-agent
pip install -r requirements.txt
```

## Usage

```python
from agent import SecurityDashboard

agent = SecurityDashboard()
await agent.run()
```

## Database

The agent uses SQLite for persistent storage. Database file: `security-dashboard-agent.db`

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
