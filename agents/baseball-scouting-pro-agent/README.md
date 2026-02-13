# 野球スカウティングプロエージェント

## Baseball Scouting Pro Agent

プロレベルの選手スカウティング・評価分析エージェント

Professional-level player scouting and evaluation analysis agent

## Features

- Professional-level analysis
- Real-time data processing
- Discord Bot integration
- SQLite database storage

## Commands

- `scout`
- `eval`
- `compare`
- `report`

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```python
from agent import BaseballScoutingProAgent

agent = BaseballScoutingProAgent()
await agent.run_command("scout", "Player Name")
```

## Database Tables

- `players`
- `scouting_reports`
- `evaluations`

---

Created by Baseball Expert Agent Orchestrator
