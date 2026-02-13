# game-user-research-agent

**Category**: ゲームユーザーリサーチ・UXエージェント
**Version**: V33 - Agent 6/25
**Status**: Active

## Overview

game-user-research-agent is an AI-powered agent for ゲームユーザーリサーチ・UXエージェント.

## Features

- Intelligent content processing
- Persistent storage with SQLite
- Discord integration support
- RESTful API ready

## Installation

```bash
cd agents/game-user-research-agent
pip install -r requirements.txt
```

## Usage

```python
from agent import GameUserResearch

agent = GameUserResearch()
await agent.run()
```

## Database

The agent uses SQLite for persistent storage. Database file: `game-user-research-agent.db`

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
