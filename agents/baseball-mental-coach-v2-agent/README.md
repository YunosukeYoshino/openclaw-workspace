# baseball-mental-coach-v2-agent

野球メンタルコーチV2エージェント。高度メンタルトレーニング。

## Description

野球フィジカル・メンタルコーチングエージェント - baseball-mental-coach-v2-agent

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
