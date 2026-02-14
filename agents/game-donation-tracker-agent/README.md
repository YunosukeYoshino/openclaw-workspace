# game-donation-tracker-agent

ゲーム寄付追跡エージェント。投げ銭・寄付の追跡。

## Description

ゲームライブストリーミング・インタラクションエージェント - game-donation-tracker-agent

## Installation

```bash
pip install -r requirements.txt
python3 db.py  # Initialize database
```

## Usage

```bash
python3 agent.py
```

## Files

- `agent.py` - Main agent logic
- `db.py` - Database initialization
- `discord.py` - Discord integration
- `requirements.txt` - Dependencies

## API

### Actions

- `create` - Create new entry
- `get` - Get entry by ID
- `update` - Update entry
- `delete` - Delete entry
- `list` - List entries

## Environment Variables

- `DISCORD_TOKEN` - Discord bot token (optional)
