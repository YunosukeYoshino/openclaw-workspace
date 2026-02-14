# erotic-ai-img-style-v2-agent

えっちAI画像スタイルV2エージェント。スタイル変換機能の強化。

## Description

えっちコンテンツAI画像生成・スタイライズエージェント - erotic-ai-img-style-v2-agent

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
