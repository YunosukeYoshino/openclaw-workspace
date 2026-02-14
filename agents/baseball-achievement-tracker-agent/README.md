# baseball-achievement-tracker-agent

野球達成トラッカーエージェント。実績の追跡・記録。

## Description

野球プレイヤー・パフォーマンス追跡エージェント - baseball-achievement-tracker-agent

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
