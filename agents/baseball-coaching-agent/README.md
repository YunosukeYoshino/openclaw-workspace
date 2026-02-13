# 野球コーチングエージェント

## Baseball Coaching Agent

戦略立案・指導アドバイスエージェント

Strategy planning and coaching advice agent

## Features

- Professional-level analysis
- Real-time data processing
- Discord Bot integration
- SQLite database storage

## Commands

- `plan`
- `advise`
- `drill`
- `feedback`

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```python
from agent import BaseballCoachingAgent

agent = BaseballCoachingAgent()
await agent.run_command("scout", "Player Name")
```

## Database Tables

- `strategies`
- `drills`
- `feedback`

---

Created by Baseball Expert Agent Orchestrator
