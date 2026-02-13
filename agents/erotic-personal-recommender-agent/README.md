# erotic-personal-recommender-agent

**Category**: えっちコンテンツパーソナライズ・推薦エージェント
**Version**: V32 - Agent 11/25
**Status**: Active

## Overview

erotic-personal-recommender-agent is an AI-powered agent for えっちコンテンツパーソナライズ・推薦エージェント.

## Features

- Intelligent content processing
- Persistent storage with SQLite
- Discord integration support
- RESTful API ready

## Installation

```bash
cd agents/erotic-personal-recommender-agent
pip install -r requirements.txt
```

## Usage

```python
from agent import EroticPersonalRecommender

agent = EroticPersonalRecommender()
await agent.run()
```

## Database

The agent uses SQLite for persistent storage. Database file: `erotic-personal-recommender-agent.db`

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
