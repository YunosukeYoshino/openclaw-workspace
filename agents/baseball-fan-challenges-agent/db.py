#!/usr/bin/env python3
"""
野球ファンチャレンジエージェント データベース管理 / Baseball Fan Challenges Agent Database Management
baseball-fan-challenges-agent
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

    # Fan Operations
    def create_fan(
        self,
        discord_id: str,
        username: str,
        favorite_team: Optional[str] = None,
        favorite_players: Optional[str] = None,
        location: Optional[str] = None
    ) -> int:
        """Create a new fan"""
        query = """
            INSERT INTO fans (discord_id, username, favorite_team, favorite_players, location)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(discord_id) DO UPDATE SET
                username = excluded.username,
                favorite_team = excluded.favorite_team,
                favorite_players = excluded.favorite_players,
                location = excluded.location,
                updated_at = CURRENT_TIMESTAMP
        """
        return self.execute_update(query, (discord_id, username, favorite_team, favorite_players, location))

    def get_fan_by_discord_id(self, discord_id: str) -> Optional[Dict]:
        """Get fan by Discord ID"""
        rows = self.execute_query("SELECT * FROM fans WHERE discord_id = ?", (discord_id,))
        return dict(rows[0]) if rows else None

    def get_fan(self, fan_id: int) -> Optional[Dict]:
        """Get fan by ID"""
        rows = self.execute_query("SELECT * FROM fans WHERE id = ?", (fan_id,))
        return dict(rows[0]) if rows else None

    def get_fans_by_team(self, team: str, limit: int = 50) -> List[Dict]:
        """Get fans who support a specific team"""
        rows = self.execute_query(
            "SELECT * FROM fans WHERE favorite_team = ? LIMIT ?",
            (team, limit)
        )
        return [dict(row) for row in rows]

    def update_fan(
        self,
        fan_id: int,
        **kwargs
    ) -> bool:
        """Update fan information"""
        allowed_fields = [
            'username', 'favorite_team', 'favorite_players', 'preferred_teams',
            'interests', 'location', 'timezone', 'bio'
        ]
        updates = []
        params = []

        for field, value in kwargs.items():
            if field in allowed_fields:
                updates.append(f"{field} = ?")
                params.append(value)

        if not updates:
            return False

        params.append(fan_id)
        query = f"UPDATE fans SET {', '.join(updates)}, updated_at = CURRENT_TIMESTAMP WHERE id = ?"
        self.execute_update(query, tuple(params))
        return True

    # Matchmaking Operations
    def create_connection(
        self,
        fan_id_1: int,
        fan_id_2: int,
        connection_type: str = "friend",
        status: str = "pending"
    ) -> int:
        """Create a fan connection"""
        compatibility = self._calculate_compatibility(fan_id_1, fan_id_2)
        query = """
            INSERT INTO fan_connections (fan_id_1, fan_id_2, compatibility_score, connection_type, status)
            VALUES (?, ?, ?, ?, ?)
        """
        return self.execute_update(query, (fan_id_1, fan_id_2, compatibility, connection_type, status))

    def _calculate_compatibility(self, fan_id_1: int, fan_id_2: int) -> float:
        """Calculate compatibility score between two fans"""
        fan1 = self.get_fan(fan_id_1)
        fan2 = self.get_fan(fan_id_2)

        if not fan1 or not fan2:
            return 0.0

        score = 0.0

        # Team preference
        if fan1.get('favorite_team') and fan2.get('favorite_team'):
            if fan1['favorite_team'] == fan2['favorite_team']:
                score += 40

        # Location
        if fan1.get('location') and fan2.get('location'):
            if fan1['location'] == fan2['location']:
                score += 20

        # Interests overlap
        interests1 = set(str(fan1.get('interests', '')).split(','))
        interests2 = set(str(fan2.get('interests', '')).split(','))
        if interests1 and interests2:
            overlap = len(interests1 & interests2) / len(interests1 | interests2) * 40
            score += overlap

        return min(score, 100.0)

    def get_fan_connections(self, fan_id: int, status: Optional[str] = None) -> List[Dict]:
        """Get fan connections"""
        query = """
            SELECT fc.*, f1.username as username1, f2.username as username2
            FROM fan_connections fc
            JOIN fans f1 ON fc.fan_id_1 = f1.id
            JOIN fans f2 ON fc.fan_id_2 = f2.id
            WHERE fc.fan_id_1 = ? OR fc.fan_id_2 = ?
        """
        params = [fan_id, fan_id]

        if status:
            query += " AND fc.status = ?"
            params.append(status)

        rows = self.execute_query(query, tuple(params))
        return [dict(row) for row in rows]

    def find_matches(self, fan_id: int, limit: int = 10, min_score: float = 30.0) -> List[Dict]:
        """Find compatible fans"""
        fan = self.get_fan(fan_id)
        if not fan:
            return []

        query = """
            SELECT id, username, favorite_team, location, interests
            FROM fans
            WHERE id != ?
            AND id NOT IN (
                SELECT CASE WHEN fan_id_1 = ? THEN fan_id_2 ELSE fan_id_1 END
                FROM fan_connections
                WHERE fan_id_1 = ? OR fan_id_2 = ?
            )
        """
        params = [fan_id, fan_id, fan_id, fan_id]
        rows = self.execute_query(query, tuple(params))

        matches = []
        for row in rows:
            other_fan = dict(row)
            score = self._calculate_compatibility(fan_id, other_fan['id'])
            if score >= min_score:
                other_fan['compatibility_score'] = score
                matches.append(other_fan)

        matches.sort(key=lambda x: x['compatibility_score'], reverse=True)
        return matches[:limit]

    # Watch Party Operations
    def create_watch_party(
        self,
        host_id: int,
        title: str,
        description: Optional[str] = None,
        game_id: Optional[str] = None,
        game_time: Optional[str] = None,
        max_participants: int = 10
    ) -> int:
        """Create a watch party"""
        query = """
            INSERT INTO watch_parties (host_id, title, description, game_id, game_time, max_participants)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        return self.execute_update(query, (host_id, title, description, game_id, game_time, max_participants))

    def get_watch_party(self, party_id: int) -> Optional[Dict]:
        """Get watch party details"""
        rows = self.execute_query("SELECT * FROM watch_parties WHERE id = ?", (party_id,))
        return dict(rows[0]) if rows else None

    def get_watch_parties(self, status: str = 'scheduled', limit: int = 50) -> List[Dict]:
        """Get watch parties"""
        rows = self.execute_query(
            "SELECT * FROM watch_parties WHERE status = ? ORDER BY game_time ASC LIMIT ?",
            (status, limit)
        )
        return [dict(row) for row in rows]

    def join_watch_party(self, party_id: int, fan_id: int) -> bool:
        """Join a watch party"""
        try:
            query = "INSERT INTO party_participants (party_id, fan_id) VALUES (?, ?)"
            self.execute_update(query, (party_id, fan_id))
            return True
        except sqlite3.IntegrityError:
            return False

    def get_party_participants(self, party_id: int) -> List[Dict]:
        """Get watch party participants"""
        query = """
            SELECT pp.*, f.username, f.discord_id
            FROM party_participants pp
            JOIN fans f ON pp.fan_id = f.id
            WHERE pp.party_id = ?
        """
        rows = self.execute_query(query, (party_id,))
        return [dict(row) for row in rows]

    # Fan Stories Operations
    def create_fan_story(
        self,
        fan_id: int,
        title: Optional[str],
        content: str,
        game_date: Optional[str] = None,
        team: Optional[str] = None,
        media_urls: Optional[str] = None,
        tags: Optional[str] = None,
        is_public: bool = True
    ) -> int:
        """Create a fan story"""
        query = """
            INSERT INTO fan_stories (fan_id, title, content, game_date, team, media_urls, tags, is_public)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        return self.execute_update(query, (fan_id, title, content, game_date, team, media_urls, tags, int(is_public)))

    def get_fan_stories(
        self,
        fan_id: Optional[int] = None,
        is_public: Optional[bool] = True,
        limit: int = 20
    ) -> List[Dict]:
        """Get fan stories"""
        query = """
            SELECT fs.*, f.username
            FROM fan_stories fs
            JOIN fans f ON fs.fan_id = f.id
            WHERE 1=1
        """
        params = []

        if fan_id:
            query += " AND fs.fan_id = ?"
            params.append(fan_id)

        if is_public is not None:
            query += " AND fs.is_public = ?"
            params.append(int(is_public))

        query += " ORDER BY fs.created_at DESC LIMIT ?"
        params.append(limit)

        rows = self.execute_query(query, tuple(params))
        return [dict(row) for row in rows]

    # Challenges Operations
    def create_challenge(
        self,
        title: str,
        description: Optional[str],
        challenge_type: str,
        points_reward: int = 10,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> int:
        """Create a challenge"""
        query = """
            INSERT INTO challenges (title, description, challenge_type, points_reward, start_date, end_date)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        return self.execute_update(query, (title, description, challenge_type, points_reward, start_date, end_date))

    def get_challenges(self, is_active: bool = True, limit: int = 20) -> List[Dict]:
        """Get challenges"""
        rows = self.execute_query(
            "SELECT * FROM challenges WHERE is_active = ? ORDER BY created_at DESC LIMIT ?",
            (int(is_active), limit)
        )
        return [dict(row) for row in rows]

    def complete_challenge(self, fan_id: int, challenge_id: int) -> Tuple[bool, Optional[int]]:
        """Complete a challenge and award points"""
        try:
            # Get challenge points
            challenge = self.execute_query(
                "SELECT points_reward FROM challenges WHERE id = ?",
                (challenge_id,)
            )

            if not challenge:
                return False, None

            points_reward = challenge[0]['points_reward']

            # Record completion
            self.execute_update(
                "INSERT INTO challenge_completions (fan_id, challenge_id, points_awarded) VALUES (?, ?, ?)",
                (fan_id, challenge_id, points_reward)
            )

            # Update fan points
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
            # Already completed
            return False, None

    def get_fan_points(self, fan_id: int) -> Optional[Dict]:
        """Get fan points"""
        rows = self.execute_query("SELECT * FROM fan_points WHERE fan_id = ?", (fan_id,))
        return dict(rows[0]) if rows else None

    def get_leaderboard(self, limit: int = 10) -> List[Dict]:
        """Get points leaderboard"""
        query = """
            SELECT fp.*, f.username, f.discord_id
            FROM fan_points fp
            JOIN fans f ON fp.fan_id = f.id
            ORDER BY fp.total_points DESC
            LIMIT ?
        """
        rows = self.execute_query(query, (limit,))
        return [dict(row) for row in rows]

    # Analytics Operations
    def log_event(self, event_type: str, fan_id: Optional[int] = None, event_data: Optional[str] = None) -> int:
        """Log engagement event"""
        query = "INSERT INTO engagement_events (event_type, fan_id, event_data) VALUES (?, ?, ?)"
        return self.execute_update(query, (event_type, fan_id, event_data))

    def get_event_stats(self, event_type: Optional[str] = None, days: int = 30) -> Dict:
        """Get event statistics"""
        query = "SELECT COUNT(*) as count FROM engagement_events"
        params = []

        if event_type:
            query += " WHERE event_type = ?"
            params.append(event_type)

        rows = self.execute_query(query, tuple(params))
        return {"event_type": event_type, "count": rows[0]['count']}

    def submit_feedback(
        self,
        fan_id: Optional[int],
        feedback_type: str,
        rating: Optional[int] = None,
        comments: Optional[str] = None
    ) -> int:
        """Submit fan feedback"""
        query = "INSERT INTO fan_feedback (fan_id, feedback_type, rating, comments) VALUES (?, ?, ?, ?)"
        return self.execute_update(query, (fan_id, feedback_type, rating, comments))

    def get_feedback_stats(self) -> Dict:
        """Get feedback statistics"""
        query = """
            SELECT
                feedback_type,
                COUNT(*) as count,
                AVG(rating) as avg_rating
            FROM fan_feedback
            WHERE rating IS NOT NULL
            GROUP BY feedback_type
        """
        rows = self.execute_query(query)
        return [dict(row) for row in rows]


if __name__ == "__main__":
    import json
    with BaseballFanEngagementDB() as db:
        # Test: Create fan
        fan_id = db.create_fan("123456", "TestFan", "Giants", "Ohtani", "Tokyo")
        print(f"Created fan ID: {fan_id}")

        # Test: Get fan
        fan = db.get_fan_by_discord_id("123456")
        print(f"Fan data: {json.dumps(fan, indent=2, ensure_ascii=False)}")

        # Test: Create challenge
        challenge_id = db.create_challenge("Test Challenge", "Description", "quiz", 10)
        print(f"Created challenge ID: {challenge_id}")

        # Test: Complete challenge
        success, points = db.complete_challenge(1, challenge_id)
        print(f"Challenge completed: {success}, Points: {points}")

        # Test: Get leaderboard
        leaderboard = db.get_leaderboard(5)
        print(f"Leaderboard: {json.dumps(leaderboard, indent=2, ensure_ascii=False)}")
