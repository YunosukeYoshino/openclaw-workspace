# erotic-ai-video-cutter-agent

えっちAI動画カッターエージェント。動画の切り出し・編集。

## Description

えっちコンテンツAI動画編集拡張エージェント - erotic-ai-video-cutter-agent

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
