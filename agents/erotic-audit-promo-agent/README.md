# erotic-audit-promo-agent

**Category**: えっちコンテンツコンテンツマーケティングエージェント
**Version**: V34 - Agent 15/25
**Status**: Active

## Overview

erotic-audit-promo-agent is an AI-powered agent for えっちコンテンツコンテンツマーケティングエージェント.

## Features

- Intelligent content processing
- Persistent storage with SQLite
- Discord integration support
- RESTful API ready

## Installation

```bash
cd agents/erotic-audit-promo-agent
pip install -r requirements.txt
```

## Usage

```python
from agent import EroticAuditPromo

agent = EroticAuditPromo()
await agent.run()
```

## Database

The agent uses SQLite for persistent storage. Database file: `erotic-audit-promo-agent.db`

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
