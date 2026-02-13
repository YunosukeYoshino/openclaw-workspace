#!/usr/bin/env python3
"""
野球ファンマッチメイキングエージェント データベース管理 / Baseball Fan Matchmaker Agent Database Management
"""

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Tuple

class BaseballFanEngagementDB:
    """野球ファンエンゲージメント データベース管理クラス"""

    def __init__(self, db_path: str = "data/baseball_fan_engagement.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = None
        self.connect()

    def connect(self):
        """Connect to database"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row

    def close(self):
        """Close connection"""
        if self.conn:
            self.conn.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def execute_query(self, query: str, params: tuple = None) -> List[sqlite3.Row]:
        """Execute SELECT query"""
        cursor = self.conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        return cursor.fetchall()

    def execute_update(self, query: str, params: tuple = None) -> int:
        """Execute INSERT/UPDATE/DELETE query"""
        cursor = self.conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        self.conn.commit()
        return cursor.lastrowid

    def create_fan(self, discord_id: str, username: str, favorite_team: Optional[str] = None, location: Optional[str] = None) -> int:
        """Create a new fan"""
        query = """
            INSERT INTO fans (discord_id, username, favorite_team, location)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(discord_id) DO UPDATE SET
                username = excluded.username,
                favorite_team = excluded.favorite_team,
                location = excluded.location,
                updated_at = CURRENT_TIMESTAMP
        """
        return self.execute_update(query, (discord_id, username, favorite_team, location))

    def get_fan_by_discord_id(self, discord_id: str) -> Optional[Dict]:
        """Get fan by Discord ID"""
        rows = self.execute_query("SELECT * FROM fans WHERE discord_id = ?", (discord_id,))
        return dict(rows[0]) if rows else None

    def create_watch_party(self, host_id: int, title: str, description: Optional[str] = None, game_id: Optional[str] = None, max_participants: int = 10) -> int:
        """Create a watch party"""
        query = """
            INSERT INTO watch_parties (host_id, title, description, game_id, max_participants)
            VALUES (?, ?, ?, ?, ?)
        """
        return self.execute_update(query, (host_id, title, description, game_id, max_participants))

    def get_watch_parties(self, status: str = 'scheduled', limit: int = 50) -> List[Dict]:
        """Get watch parties"""
        rows = self.execute_query("SELECT * FROM watch_parties WHERE status = ? ORDER BY game_time ASC LIMIT ?", (status, limit))
        return [dict(row) for row in rows]

    def create_fan_story(self, fan_id: int, title: Optional[str], content: str, game_date: Optional[str] = None, team: Optional[str] = None, is_public: bool = True) -> int:
        """Create a fan story"""
        query = """
            INSERT INTO fan_stories (fan_id, title, content, game_date, team, is_public)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        return self.execute_update(query, (fan_id, title, content, game_date, team, int(is_public)))

    def get_fan_stories(self, fan_id: Optional[int] = None, limit: int = 20) -> List[Dict]:
        """Get fan stories"""
        if fan_id:
            rows = self.execute_query("SELECT * FROM fan_stories WHERE fan_id = ? ORDER BY created_at DESC LIMIT ?", (fan_id, limit))
        else:
            rows = self.execute_query("SELECT * FROM fan_stories WHERE is_public = 1 ORDER BY created_at DESC LIMIT ?", (limit,))
        return [dict(row) for row in rows]

    def create_challenge(self, title: str, description: Optional[str], challenge_type: str, points_reward: int = 10) -> int:
        """Create a challenge"""
        query = """
            INSERT INTO challenges (title, description, challenge_type, points_reward)
            VALUES (?, ?, ?, ?)
        """
        return self.execute_update(query, (title, description, challenge_type, points_reward))

    def get_challenges(self, is_active: bool = True, limit: int = 20) -> List[Dict]:
        """Get challenges"""
        rows = self.execute_query("SELECT * FROM challenges WHERE is_active = ? ORDER BY created_at DESC LIMIT ?", (int(is_active), limit))
        return [dict(row) for row in rows]

    def complete_challenge(self, fan_id: int, challenge_id: int) -> Tuple[bool, Optional[int]]:
        """Complete a challenge and award points"""
        try:
            challenge = self.execute_query("SELECT points_reward FROM challenges WHERE id = ?", (challenge_id,))

            if not challenge:
                return False, None

            points_reward = challenge[0]['points_reward']

            self.execute_update("INSERT INTO challenge_completions (fan_id, challenge_id, points_awarded) VALUES (?, ?, ?)", (fan_id, challenge_id, points_reward))

            self.execute_update(
                """
                INSERT INTO fan_points (fan_id, total_points)
                VALUES (?, ?)
                ON CONFLICT(fan_id) DO UPDATE SET
                    total_points = total_points + ?,
                    last_updated = CURRENT_TIMESTAMP
                """,
                (fan_id, points_reward, points_reward)
            )

            return True, points_reward
        except sqlite3.IntegrityError:
            return False, None

    def get_fan_points(self, fan_id: int) -> Optional[Dict]:
        """Get fan points"""
        rows = self.execute_query("SELECT * FROM fan_points WHERE fan_id = ?", (fan_id,))
        return dict(rows[0]) if rows else None

    def get_leaderboard(self, limit: int = 10) -> List[Dict]:
        """Get points leaderboard"""
        query = """
            SELECT fp.*, f.username
            FROM fan_points fp
            JOIN fans f ON fp.fan_id = f.id
            ORDER BY fp.total_points DESC
            LIMIT ?
        """
        rows = self.execute_query(query, (limit,))
        return [dict(row) for row in rows]


if __name__ == "__main__":
    import json
    with BaseballFanEngagementDB() as db:
        fan_id = db.create_fan("123456", "TestFan", "Giants", "Tokyo")
        print(f"Created fan ID: {fan_id}")

        fan = db.get_fan_by_discord_id("123456")
        print(f"Fan data: {json.dumps(fan, indent=2, ensure_ascii=False)}")
