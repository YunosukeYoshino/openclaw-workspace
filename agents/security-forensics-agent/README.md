# security-forensics-agent

**Category**: セキュリティインシデント・脅威対応エージェント
**Version**: V33 - Agent 23/25
**Status**: Active

## Overview

security-forensics-agent is an AI-powered agent for セキュリティインシデント・脅威対応エージェント.

## Features

- Intelligent content processing
- Persistent storage with SQLite
- Discord integration support
- RESTful API ready

## Installation

```bash
cd agents/security-forensics-agent
pip install -r requirements.txt
```

## Usage

```python
from agent import SecurityForensics

agent = SecurityForensics()
await agent.run()
```

## Database

The agent uses SQLite for persistent storage. Database file: `security-forensics-agent.db`

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
