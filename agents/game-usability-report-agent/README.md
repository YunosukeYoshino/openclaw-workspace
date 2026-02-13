# game-usability-report-agent

**Category**: ゲームユーザーリサーチ・UXエージェント
**Version**: V33 - Agent 10/25
**Status**: Active

## Overview

game-usability-report-agent is an AI-powered agent for ゲームユーザーリサーチ・UXエージェント.

## Features

- Intelligent content processing
- Persistent storage with SQLite
- Discord integration support
- RESTful API ready

## Installation

```bash
cd agents/game-usability-report-agent
pip install -r requirements.txt
```

## Usage

```python
from agent import GameUsabilityReport

agent = GameUsabilityReport()
await agent.run()
```

## Database

The agent uses SQLite for persistent storage. Database file: `game-usability-report-agent.db`

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
