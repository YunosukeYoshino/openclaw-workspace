# game-perf-analyzer-agent

**Category**: ゲームパフォーマンス・最適化エージェント
**Version**: V34 - Agent 6/25
**Status**: Active

## Overview

game-perf-analyzer-agent is an AI-powered agent for ゲームパフォーマンス・最適化エージェント.

## Features

- Intelligent content processing
- Persistent storage with SQLite
- Discord integration support
- RESTful API ready

## Installation

```bash
cd agents/game-perf-analyzer-agent
pip install -r requirements.txt
```

## Usage

```python
from agent import GamePerfAnalyzer

agent = GamePerfAnalyzer()
await agent.run()
```

## Database

The agent uses SQLite for persistent storage. Database file: `game-perf-analyzer-agent.db`

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
