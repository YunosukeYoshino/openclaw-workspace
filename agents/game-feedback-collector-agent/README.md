# game-feedback-collector-agent

**Category**: ゲームユーザーリサーチ・UXエージェント
**Version**: V33 - Agent 8/25
**Status**: Active

## Overview

game-feedback-collector-agent is an AI-powered agent for ゲームユーザーリサーチ・UXエージェント.

## Features

- Intelligent content processing
- Persistent storage with SQLite
- Discord integration support
- RESTful API ready

## Installation

```bash
cd agents/game-feedback-collector-agent
pip install -r requirements.txt
```

## Usage

```python
from agent import GameFeedbackCollector

agent = GameFeedbackCollector()
await agent.run()
```

## Database

The agent uses SQLite for persistent storage. Database file: `game-feedback-collector-agent.db`

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
