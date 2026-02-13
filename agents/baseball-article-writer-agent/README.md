# baseball-article-writer-agent

**Category**: 野球メディア・コンテンツ制作エージェント
**Version**: V33 - Agent 4/25
**Status**: Active

## Overview

baseball-article-writer-agent is an AI-powered agent for 野球メディア・コンテンツ制作エージェント.

## Features

- Intelligent content processing
- Persistent storage with SQLite
- Discord integration support
- RESTful API ready

## Installation

```bash
cd agents/baseball-article-writer-agent
pip install -r requirements.txt
```

## Usage

```python
from agent import BaseballArticleWriter

agent = BaseballArticleWriter()
await agent.run()
```

## Database

The agent uses SQLite for persistent storage. Database file: `baseball-article-writer-agent.db`

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
