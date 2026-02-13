# baseball-social-media-agent

**Category**: 野球メディア・コンテンツ制作エージェント
**Version**: V33 - Agent 5/25
**Status**: Active

## Overview

baseball-social-media-agent is an AI-powered agent for 野球メディア・コンテンツ制作エージェント.

## Features

- Intelligent content processing
- Persistent storage with SQLite
- Discord integration support
- RESTful API ready

## Installation

```bash
cd agents/baseball-social-media-agent
pip install -r requirements.txt
```

## Usage

```python
from agent import BaseballSocialMedia

agent = BaseballSocialMedia()
await agent.run()
```

## Database

The agent uses SQLite for persistent storage. Database file: `baseball-social-media-agent.db`

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
