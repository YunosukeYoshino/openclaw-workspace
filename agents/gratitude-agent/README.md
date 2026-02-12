# Gratitude Agent / 感謝日記エージェント

## Description

Gratitude Agent helps you maintain a daily gratitude journal and track things you're thankful for.
感謝日記エージェントは日々の感謝日記を維持し、感謝していることを記録します。

## Features

- Daily gratitude logging
- Multiple entries per day
- Category-based gratitude
- Gratitude statistics
- Reflective journaling
- 日本語と英語対応

## Commands

- `!gratitude [content]` - Add a gratitude entry / 感謝エントリーを追加
- `!gratitude list` - View all gratitudes / すべての感謝を表示
- `!gratitude today` - View today's gratitudes / 今日の感謝を表示
- `!gratitude stats` - Show statistics / 統計を表示
- `!gratitude delete [id]` - Delete an entry / エントリーを削除

## Files

- `db.py` - SQLite database management
- `discord.py` - Discord bot integration
- `README.md` - This file
- `requirements.txt` - Python dependencies

## Usage Example

```
!gratitude "Grateful for my family's support"
!gratitude "Beautiful sunset today"
!gratitude today
!gratitude stats
```

## Database Schema

- `gratitude_entries` - Gratitude records
