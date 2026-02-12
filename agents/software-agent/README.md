# Software Agent

Discord-based software management agent with SQLite database and NLP-based message processing.

## Features

- 🗣️ **Natural Language Processing**: Automatically analyze and respond to messages
- 🌏 **Multilingual Support**: Japanese and English
- 📊 **Software License Management**: Track software licenses and their expiration
- 💾 **SQLite Database**: Persistent storage for software inventory
- 🔧 **Update Management**: Track software updates and versions
- 📦 **Installation Management**: Track software installations

## File Structure

```
software-agent/
├── db.py          # Database management module
├── discord.py     # Discord bot and NLP module
├── requirements.txt
└── README.md
```

## Installation

### 1. Install dependencies

```bash
cd software-agent
pip install -r requirements.txt
```

### 2. Set environment variables

```bash
export DISCORD_TOKEN="your_discord_bot_token"
```

Get Discord Bot Token:
1. Visit [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a new application
3. In the Bot tab, create a bot and copy the token

## Usage

### Starting the bot

```bash
python discord.py
```

### Commands

- `!help` - Show help
- `!software list` - List all software
- `!software add <name> <version> [license] [expiry]` - Add software
- `!software update <id> <version>` - Update software version
- `!software install <id> <date> [location]` - Record installation
- `!software licenses` - List licenses with expiry dates
- `!software updates` - List pending updates
- `!lang [ja|en]` - Switch language

### Natural Language Processing

You can interact with the bot using natural language without commands.

**Examples (Japanese):**
- "ソフトウェア一覧を見て"
- "新しいソフトウェアを追加"
- "ライセンスの期限を確認"

**Examples (English):**
- "Show my software"
- "Add new software"
- "Check license expiry"

The bot automatically detects language and responds accordingly.

## Database Structure

### Tables

#### software
Software inventory
- `id`, `name`, `version`, `vendor`, `license_type`, `license_key`, `expiry_date`, `purchase_date`, `status`, `notes`, `created_at`, `updated_at`

#### installations
Installation records
- `id`, `software_id`, `device_name`, `install_date`, `location`, `user`, `notes`, `created_at`

#### updates
Update records
- `id`, `software_id`, `old_version`, `new_version`, `update_date`, `notes`, `created_at`

#### user_settings
User preferences
- `user_id`, `language`, `timezone`

## API Reference

### db.py

```python
from db import get_database

db = get_database()

# Software management
software_id = db.add_software(user_id, name, version, vendor=None, license_type=None, license_key=None, expiry_date=None)
software = db.get_software(software_id)
softwares = db.get_all_softwares(user_id)

# Installation management
install_id = db.add_installation(software_id, device_name, install_date, location, user)
installations = db.get_installations(software_id)

# Update management
update_id = db.add_update(software_id, old_version, new_version, update_date, notes)
updates = db.get_updates(software_id)

# User settings
db.set_user_language(user_id, language)
settings = db.get_user_settings(user_id)

# Summary
summary = db.get_summary(user_id)
```

### discord.py

`SoftwareAgent` class can be extended with custom commands.

```python
from discord.ext import commands

class MyAgent(SoftwareAgent):
    @commands.command(name='mycommand')
    async def my_command(self, ctx):
        await ctx.send("Custom command!")
```

## Intent Classification

The bot detects the following intents:

- `software_list`: List software
- `software_add`: Add new software
- `software_update`: Update software version
- `software_install`: Record installation
- `license_list`: List licenses
- `help`: Show help

## License

MIT License
