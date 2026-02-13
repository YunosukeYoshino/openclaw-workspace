#!/usr/bin/env python3
"""
野球ライブ統計エージェント - Database Module

Provides real-time statistics during live baseball games
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Any

class Baseball_Live_Stats_AgentDB:
    """野球ライブ統計エージェント Database"""

    def __init__(self, db_path: Optional[Path] = None):
        if db_path is None:
            db_path = Path(__file__).parent / "data" / "baseball-live-stats-agent.db"
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.init_db()

    def get_connection(self) -> sqlite3.Connection:
        """DB接続を取得"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        """データベースを初期化"""
        with self.get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    type TEXT DEFAULT 'note',
                    tags TEXT,
                    status TEXT DEFAULT 'active',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS notifications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_id TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    message TEXT NOT NULL,
                    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'pending'
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    game_id TEXT NOT NULL,
                    stat_type TEXT NOT NULL,
                    stat_value TEXT NOT NULL,
                    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS highlights (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    game_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT,
                    timestamp INTEGER NOT NULL,
                    video_url TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()

    def add_entry(self, title: str, content: str, entry_type: str = "note",
                  tags: Optional[List[str]] = None) -> int:
        """エントリーを追加"""
        tags_json = json.dumps(tags) if tags else None
        with self.get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO entries (title, content, type, tags)
                VALUES (?, ?, ?, ?)
            """, (title, content, entry_type, tags_json))
            conn.commit()
            return cursor.lastrowid

    def get_entry(self, entry_id: int) -> Optional[Dict[str, Any]]:
        """エントリーを取得"""
        with self.get_connection() as conn:
            row = conn.execute("SELECT * FROM entries WHERE id = ?", (entry_id,)).fetchone()
            if row:
                return dict(row)
            return None

    def list_entries(self, entry_type: Optional[str] = None,
                     status: str = "active", limit: int = 100) -> List[Dict[str, Any]]:
        """エントリーを一覧表示"""
        with self.get_connection() as conn:
            if entry_type:
                rows = conn.execute("""
                    SELECT * FROM entries WHERE type = ? AND status = ?
                    ORDER BY created_at DESC LIMIT ?
                """, (entry_type, status, limit)).fetchall()
            else:
                rows = conn.execute("""
                    SELECT * FROM entries WHERE status = ?
                    ORDER BY created_at DESC LIMIT ?
                """, (status, limit)).fetchall()
            return [dict(row) for row in rows]

    def update_entry(self, entry_id: int, **kwargs) -> bool:
        """エントリーを更新"""
        if not kwargs:
            return False
        set_clause = ", ".join([f"{key} = ?" for key in kwargs.keys()])
        values = list(kwargs.values()) + [entry_id]
        with self.get_connection() as conn:
            conn.execute(f"UPDATE entries SET {set_clause}, updated_at = CURRENT_TIMESTAMP WHERE id = ?", values)
            conn.commit()
            return True

    def delete_entry(self, entry_id: int) -> bool:
        """エントリーを削除"""
        with self.get_connection() as conn:
            conn.execute("UPDATE entries SET status = ? WHERE id = ?", ('archived', entry_id))
            conn.commit()
            return True

    def add_notification(self, event_id: str, event_type: str, message: str) -> int:
        """通知を追加"""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO notifications (event_id, event_type, message)
                VALUES (?, ?, ?)
            """, (event_id, event_type, message))
            conn.commit()
            return cursor.lastrowid

    def get_pending_notifications(self) -> List[Dict[str, Any]]:
        """未送信の通知を取得"""
        with self.get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM notifications WHERE status = ?
                ORDER BY created_at ASC
            """, ('pending',)).fetchall()
            return [dict(row) for row in rows]

    def mark_notification_sent(self, notification_id: int) -> bool:
        """通知を送信済みにマーク"""
        with self.get_connection() as conn:
            conn.execute("UPDATE notifications SET status = ? WHERE id = ?", ('sent', notification_id))
            conn.commit()
            return True

    def add_stat(self, game_id: str, stat_type: str, stat_value: str) -> int:
        """統計を追加"""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO stats (game_id, stat_type, stat_value)
                VALUES (?, ?, ?)
            """, (game_id, stat_type, stat_value))
            conn.commit()
            return cursor.lastrowid

    def get_game_stats(self, game_id: str) -> List[Dict[str, Any]]:
        """ゲーム統計を取得"""
        with self.get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM stats WHERE game_id = ?
                ORDER BY recorded_at DESC
            """, (game_id,)).fetchall()
            return [dict(row) for row in rows]

    def add_highlight(self, game_id: str, title: str, description: str,
                     timestamp: int, video_url: Optional[str] = None) -> int:
        """ハイライトを追加"""
        with self.get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO highlights (game_id, title, description, timestamp, video_url)
                VALUES (?, ?, ?, ?, ?)
            """, (game_id, title, description, timestamp, video_url))
            conn.commit()
            return cursor.lastrowid

    def get_game_highlights(self, game_id: str) -> List[Dict[str, Any]]:
        """ゲームハイライトを取得"""
        with self.get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM highlights WHERE game_id = ?
                ORDER BY timestamp ASC
            """, (game_id,)).fetchall()
            return [dict(row) for row in rows]

    def get_setting(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """設定を取得"""
        with self.get_connection() as conn:
            row = conn.execute("SELECT value FROM settings WHERE key = ?", (key,)).fetchone()
            if row:
                return row['value']
            return default

    def set_setting(self, key: str, value: str) -> bool:
        """設定を保存"""
        with self.get_connection() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO settings (key, value, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
            """, (key, value))
            conn.commit()
            return True

    def get_stats(self) -> Dict[str, int]:
        """統計情報を取得"""
        with self.get_connection() as conn:
            entries_count = conn.execute('SELECT COUNT(*) FROM entries WHERE status = "active"').fetchone()[0]
            notifications_count = conn.execute("SELECT COUNT(*) FROM notifications").fetchone()[0]
            stats_count = conn.execute("SELECT COUNT(*) FROM stats").fetchone()[0]
            highlights_count = conn.execute("SELECT COUNT(*) FROM highlights").fetchone()[0]
            return {
                "entries": entries_count,
                "notifications": notifications_count,
                "stats": stats_count,
                "highlights": highlights_count
            }

def main():
    """メイン関数"""
    db = Baseball_Live_Stats_AgentDB()
    stats = db.get_stats()
    print("📊 データベース統計:")
    for key, value in stats.items():
        print(f"  {key}: {value}")

if __name__ == "__main__":
    main()
