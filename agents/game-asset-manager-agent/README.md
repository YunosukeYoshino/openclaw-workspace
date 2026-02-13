# game-asset-manager-agent

**Category**: ゲームアセット・リソース管理エージェント
**Version**: V32 - Agent 6/25
**Status**: Active

## Overview

game-asset-manager-agent is an AI-powered agent for ゲームアセット・リソース管理エージェント.

## Features

- Intelligent content processing
- Persistent storage with SQLite
- Discord integration support
- RESTful API ready

## Installation

```bash
cd agents/game-asset-manager-agent
pip install -r requirements.txt
```

## Usage

```python
from agent import GameAssetManager

agent = GameAssetManager()
await agent.run()
```

## Database

The agent uses SQLite for persistent storage. Database file: `game-asset-manager-agent.db`

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
