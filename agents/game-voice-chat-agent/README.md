# game-voice-chat-agent

**Category**: ゲームクロスプレイ・マルチプラットフォームエージェント
**Version**: V36 - Agent 9/25
**Status**: Active

## Overview

game-voice-chat-agent is an AI-powered agent for ゲームクロスプレイ・マルチプラットフォームエージェント.

## Features

- Intelligent content processing
- Persistent storage with SQLite
- Discord integration support
- RESTful API ready

## Installation

```bash
cd agents/game-voice-chat-agent
pip install -r requirements.txt
```

## Usage

```python
from agent import GameVoiceChat

agent = GameVoiceChat()
await agent.run()
```

## Database

The agent uses SQLite for persistent storage. Database file: `game-voice-chat-agent.db`

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
