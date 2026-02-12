# Reading Agent / 読書記録エージェント

## Description

Reading Agent helps you track your reading progress, manage books, and keep notes about what you've read.
読書記録エージェントは読書の進捗を追跡し、本の管理とメモを保存します。

## Features

- Book management (add, edit, delete books)
- Reading progress tracking (page numbers, percentage)
- Notes and quotes recording
- Book categorization
- Reading statistics
- 日本語と英語対応

## Commands

- `!book add [title] [author]` - Add a new book / 新しい本を追加
- `!book list` - List all books / すべての本を表示
- `!book progress [id] [page]` - Update reading progress / 読書進捗を更新
- `!book note [id] [note]` - Add a note / メモを追加
- `!book stats` - Show reading statistics / 読書統計を表示
- `!book delete [id]` - Delete a book / 本を削除

## Files

- `db.py` - SQLite database management
- `discord.py` - Discord bot integration
- `README.md` - This file
- `requirements.txt` - Python dependencies

## Usage Example

```
!book add "The Great Gatsby" "F. Scott Fitzgerald"
!book progress 1 50
!book note 1 "This book is amazing!"
!book stats
```

## Database Schema

- `books` - Book information
- `reading_progress` - Progress tracking
- `notes` - Reading notes
