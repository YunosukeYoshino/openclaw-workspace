# helm-chart-manager-agent

**Category**: コンテナオーケストレーション・Kubernetesエージェント
**Version**: V32 - Agent 24/25
**Status**: Active

## Overview

helm-chart-manager-agent is an AI-powered agent for コンテナオーケストレーション・Kubernetesエージェント.

## Features

- Intelligent content processing
- Persistent storage with SQLite
- Discord integration support
- RESTful API ready

## Installation

```bash
cd agents/helm-chart-manager-agent
pip install -r requirements.txt
```

## Usage

```python
from agent import HelmChartManager

agent = HelmChartManager()
await agent.run()
```

## Database

The agent uses SQLite for persistent storage. Database file: `helm-chart-manager-agent.db`

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
