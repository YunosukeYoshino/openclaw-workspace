# Meditation Agent / 瞑想記録エージェント

## Description

Meditation Agent helps you track your meditation sessions, techniques, and progress.
瞑想記録エージェントは瞑想セッション、テクニック、進捗を追跡します。

## Features

- Meditation session logging
- Technique tracking
- Duration recording
- Session notes and insights
- Statistics and streaks
- 日本語と英語対応

## Commands

- `!meditate [minutes] [technique]` - Log meditation session / 瞑想セッションを記録
- `!meditate list` - View meditation history / 瞑想履歴を表示
- `!meditate stats` - Show statistics / 統計を表示
- `!meditate note [note]` - Add a note / メモを追加
- `!meditate delete [id]` - Delete an entry / 記録を削除

## Files

- `db.py` - SQLite database management
- `discord.py` - Discord bot integration
- `README.md` - This file
- `requirements.txt` - Python dependencies

## Usage Example

```
!meditate 15 mindfulness
!meditate note "Very peaceful session"
!meditate 20 breathing
!meditate stats
```

## Database Schema

- `meditation_sessions` - Session records
- `meditation_notes` - Notes and insights
