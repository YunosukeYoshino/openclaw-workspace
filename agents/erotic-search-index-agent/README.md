# erotic-search-index-agent

**Category**: えっちコンテンツコレクション・アーカイブエージェント
**Version**: V36 - Agent 15/25
**Status**: Active

## Overview

erotic-search-index-agent is an AI-powered agent for えっちコンテンツコレクション・アーカイブエージェント.

## Features

- Intelligent content processing
- Persistent storage with SQLite
- Discord integration support
- RESTful API ready

## Installation

```bash
cd agents/erotic-search-index-agent
pip install -r requirements.txt
```

## Usage

```python
from agent import EroticSearchIndex

agent = EroticSearchIndex()
await agent.run()
```

## Database

The agent uses SQLite for persistent storage. Database file: `erotic-search-index-agent.db`

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
