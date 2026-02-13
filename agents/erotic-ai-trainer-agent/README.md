# erotic-ai-trainer-agent

**Category**: えっちコンテンツAIトレーニング・モデル管理エージェント
**Version**: V33 - Agent 11/25
**Status**: Active

## Overview

erotic-ai-trainer-agent is an AI-powered agent for えっちコンテンツAIトレーニング・モデル管理エージェント.

## Features

- Intelligent content processing
- Persistent storage with SQLite
- Discord integration support
- RESTful API ready

## Installation

```bash
cd agents/erotic-ai-trainer-agent
pip install -r requirements.txt
```

## Usage

```python
from agent import EroticAiTrainer

agent = EroticAiTrainer()
await agent.run()
```

## Database

The agent uses SQLite for persistent storage. Database file: `erotic-ai-trainer-agent.db`

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
