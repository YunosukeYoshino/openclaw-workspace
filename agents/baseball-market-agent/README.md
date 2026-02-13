# 野球マーケット分析エージェント

## Baseball Market Analysis Agent

FA市場・トレード・契約分析エージェント

FA market, trade, and contract analysis agent

## Features

- Professional-level analysis
- Real-time data processing
- Discord Bot integration
- SQLite database storage

## Commands

- `analyze_market`
- `track_trade`
- `contract`
- `report`

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```python
from agent import BaseballMarketAgent

agent = BaseballMarketAgent()
await agent.run_command("scout", "Player Name")
```

## Database Tables

- `contracts`
- `trades`
- `market_data`

---

Created by Baseball Expert Agent Orchestrator
