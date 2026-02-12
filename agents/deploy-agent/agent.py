#!/usr/bin/env python3
"""
Deploy Agent - Main Entry Point
デプロイとロールバック管理のためのDiscordボット
"""

import os
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Import Discord bot from discord.py
from discord import bot

# Import database initialization
from db import init_db

# Database path
DB_PATH = Path(__file__).parent / "deploy.db"

# Initialize database
if not DB_PATH.exists():
    init_db()


def run_bot():
    """Discord Botを実行"""
    token = os.environ.get('DISCORD_TOKEN')
    if not token:
        print('❌ DISCORD_TOKEN 環境変数が設定されていません')
        print('Please set DISCORD_TOKEN environment variable')
        print('Example: export DISCORD_TOKEN="your-bot-token"')
        return

    print('🚀 Deploy Agent starting...')
    bot.run(token)


if __name__ == '__main__':
    init_db()
    run_bot()
