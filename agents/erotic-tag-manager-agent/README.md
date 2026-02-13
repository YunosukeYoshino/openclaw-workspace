# erotic-tag-manager-agent

**Category**: えっちコンテンツコレクション・アーカイブエージェント
**Version**: V36 - Agent 14/25
**Status**: Active

## Overview

erotic-tag-manager-agent is an AI-powered agent for えっちコンテンツコレクション・アーカイブエージェント.

## Features

- Intelligent content processing
- Persistent storage with SQLite
- Discord integration support
- RESTful API ready

## Installation

```bash
cd agents/erotic-tag-manager-agent
pip install -r requirements.txt
```

## Usage

```python
from agent import EroticTagManager

agent = EroticTagManager()
await agent.run()
```

## Database

The agent uses SQLite for persistent storage. Database file: `erotic-tag-manager-agent.db`

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
