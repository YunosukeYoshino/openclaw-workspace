# baseball-metrics-dashboard-agent

**Category**: 野球統計・分析レポートエージェント
**Version**: V34 - Agent 5/25
**Status**: Active

## Overview

baseball-metrics-dashboard-agent is an AI-powered agent for 野球統計・分析レポートエージェント.

## Features

- Intelligent content processing
- Persistent storage with SQLite
- Discord integration support
- RESTful API ready

## Installation

```bash
cd agents/baseball-metrics-dashboard-agent
pip install -r requirements.txt
```

## Usage

```python
from agent import BaseballMetricsDashboard

agent = BaseballMetricsDashboard()
await agent.run()
```

## Database

The agent uses SQLite for persistent storage. Database file: `baseball-metrics-dashboard-agent.db`

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
