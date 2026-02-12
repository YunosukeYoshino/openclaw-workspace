# Sleep Agent / 睡眠記録エージェント

## Description

Sleep Agent helps you track your sleep patterns, sleep quality, and maintain a sleep journal.
睡眠記録エージェントは睡眠パターン、睡眠品質を追跡し、睡眠日記を維持します。

## Features

- Sleep duration tracking
- Sleep quality recording
- Bedtime and wake-up time logging
- Sleep notes and dreams
- Sleep statistics and trends
- 日本語と英語対応

## Commands

- `!sleep log [hours] [quality]` - Log sleep / 睡眠を記録
- `!sleep list` - View sleep history / 睡眠履歴を表示
- `!sleep stats` - Show sleep statistics / 睡眠統計を表示
- `!sleep note [note]` - Add a sleep note / 睡眠メモを追加
- `!sleep dream [dream]` - Record a dream / 夢を記録
- `!sleep delete [id]` - Delete a sleep entry / 睡眠記録を削除

## Files

- `db.py` - SQLite database management
- `discord.py` - Discord bot integration
- `README.md` - This file
- `requirements.txt` - Python dependencies

## Usage Example

```
!sleep log 7.5 good
!sleep note "Woke up feeling refreshed"
!sleep dream "Flying over mountains"
!sleep stats
```

## Database Schema

- `sleep_records` - Sleep duration and quality
- `sleep_notes` - Sleep notes and dreams
