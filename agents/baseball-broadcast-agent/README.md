# 野球中継・解説エージェント

## Baseball Broadcast Agent

試合実況・解説・ハイライト生成エージェント

Game commentary, analysis, and highlight generation agent

## Features

- Professional-level analysis
- Real-time data processing
- Discord Bot integration
- SQLite database storage

## Commands

- `commentary`
- `highlight`
- `analyze`
- `report`

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```python
from agent import BaseballBroadcastAgent

agent = BaseballBroadcastAgent()
await agent.run_command("scout", "Player Name")
```

## Database Tables

- `games`
- `commentary`
- `highlights`

---

Created by Baseball Expert Agent Orchestrator
