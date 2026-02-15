#!/usr/bin/env python3
"""
Helper script to create the complete orchestrator
"""

import json
import subprocess
from datetime import datetime
from pathlib import Path

# Configuration
WORKSPACE = Path("/workspace")
AGENTS_DIR = WORKSPACE / "agents"
PROGRESS_FILE = WORKSPACE / "baseball_fan_engagement_progress.json"

# Agent Definitions
AGENTS = [
    {
        "name": "baseball-fan-matchmaker-agent",
        "description_ja": "野球ファンマッチメイキングエージェント",
        "description_en": "Baseball Fan Matchmaker Agent",
        "type": "social",
        "emoji": "🤝"
    },
    {
        "name": "baseball-watch-party-agent",
        "description_ja": "野球観戦パーティーエージェント",
        "description_en": "Baseball Watch Party Agent",
        "type": "live",
        "emoji": "📺"
    },
    {
        "name": "baseball-fan-stories-agent",
        "description_ja": "野球ファンストーリーエージェント",
        "description_en": "Baseball Fan Stories Agent",
        "type": "content",
        "emoji": "📖"
    },
    {
        "name": "baseball-fan-challenges-agent",
        "description_ja": "野球ファンチャレンジエージェント",
        "description_en": "Baseball Fan Challenges Agent",
        "type": "gaming",
        "emoji": "🎮"
    },
    {
        "name": "baseball-fan-analytics-agent",
        "description_ja": "野球ファン分析エージェント",
        "description_en": "Baseball Fan Analytics Agent",
        "type": "analytics",
        "emoji": "📊"
    }
]

# Read the existing orchestrator v2 for the structure
with open("/workspace/baseball_fan_engagement_orchestrator_v2.py", "r") as f:
    orchestrator_content = f.read()

# Now add the remaining functions
db_py_template = '''
def generate_db_py(agent):
    """Generate db.py"""
    class_name = agent["name"].replace("-", "_").title().replace("_", "")

    template = """#!/usr/bin/env python3
"""
{description_ja} データベース管理 / {description_en} Database Management
{name}
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

    def create_fan(self, discord_id: str, username: str, favorite_team: Optional[str] = None, favorite_players: Optional[str] = None, location: Optional[str] = None) -> int:
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

    def get_fans_by_team(self, team: str, limit: int = 50) -> List[Dict]:
        """Get fans who support a specific team"""
        rows = self.execute_query("SELECT * FROM fans WHERE favorite_team = ? LIMIT ?", (team, limit))
        return [dict(row) for row in rows]

    def create_connection(self, fan_id_1: int, fan_id_2: int, connection_type: str = "friend", status: str = "pending") -> int:
        """Create a fan connection"""
        compatibility = self._calculate_compatibility(fan_id_1, fan_id_2)
        query = """
            INSERT INTO fan_connections (fan_id_1, fan_id_2, compatibility_score, connection_type, status)
            VALUES (?, ?, ?, ?, ?)
        """
        return self.execute_update(query, (fan_id_1, fan_id_2, compatibility, connection_type, status))

    def _calculate_compatibility(self, fan_id_1: int, fan_id_2: int) -> float:
        """Calculate compatibility score between two fans"""
        fan1 = self.execute_query("SELECT * FROM fans WHERE id = ?", (fan_id_1,))
        fan2 = self.execute_query("SELECT * FROM fans WHERE id = ?", (fan_id_2,))

        if not fan1 or not fan2:
            return 0.0

        f1 = dict(fan1[0])
        f2 = dict(fan2[0])

        score = 0.0

        if f1.get('favorite_team') and f2.get('favorite_team'):
            if f1['favorite_team'] == f2['favorite_team']:
                score += 40

        if f1.get('location') and f2.get('location'):
            if f1['location'] == f2['location']:
                score += 20

        interests1 = set(str(f1.get('interests', '')).split(','))
        interests2 = set(str(f2.get('interests', '')).split(','))
        if interests1 and interests2:
            overlap = len(interests1 & interests2) / len(interests1 | interests2) * 40
            score += overlap

        return min(score, 100.0)

    def find_matches(self, fan_id: int, limit: int = 10, min_score: float = 30.0) -> List[Dict]:
        """Find compatible fans"""
        fan = self.execute_query("SELECT * FROM fans WHERE id = ?", (fan_id,))
        if not fan:
            return []

        query = """
            SELECT id, username, favorite_team, location, interests
            FROM fans
            WHERE id != ?
        """
        rows = self.execute_query(query, (fan_id,))

        matches = []
        for row in rows:
            other_fan = dict(row)
            score = self._calculate_compatibility(fan_id, other_fan['id'])
            if score >= min_score:
                other_fan['compatibility_score'] = score
                matches.append(other_fan)

        matches.sort(key=lambda x: x['compatibility_score'], reverse=True)
        return matches[:limit]

    def create_watch_party(self, host_id: int, title: str, description: Optional[str] = None, game_id: Optional[str] = None, game_time: Optional[str] = None, max_participants: int = 10) -> int:
        """Create a watch party"""
        query = """
            INSERT INTO watch_parties (host_id, title, description, game_id, game_time, max_participants)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        return self.execute_update(query, (host_id, title, description, game_id, game_time, max_participants))

    def get_watch_parties(self, status: str = 'scheduled', limit: int = 50) -> List[Dict]:
        """Get watch parties"""
        rows = self.execute_query("SELECT * FROM watch_parties WHERE status = ? ORDER BY game_time ASC LIMIT ?", (status, limit))
        return [dict(row) for row in rows]

    def join_watch_party(self, party_id: int, fan_id: int) -> bool:
        """Join a watch party"""
        try:
            query = "INSERT INTO party_participants (party_id, fan_id) VALUES (?, ?)"
            self.execute_update(query, (party_id, fan_id))
            return True
        except sqlite3.IntegrityError:
            return False

    def create_fan_story(self, fan_id: int, title: Optional[str], content: str, game_date: Optional[str] = None, team: Optional[str] = None, media_urls: Optional[str] = None, tags: Optional[str] = None, is_public: bool = True) -> int:
        """Create a fan story"""
        query = """
            INSERT INTO fan_stories (fan_id, title, content, game_date, team, media_urls, tags, is_public)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        return self.execute_update(query, (fan_id, title, content, game_date, team, media_urls, tags, int(is_public)))

    def get_fan_stories(self, fan_id: Optional[int] = None, is_public: Optional[bool] = True, limit: int = 20) -> List[Dict]:
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

    def create_challenge(self, title: str, description: Optional[str], challenge_type: str, points_reward: int = 10, start_date: Optional[str] = None, end_date: Optional[str] = None) -> int:
        """Create a challenge"""
        query = """
            INSERT INTO challenges (title, description, challenge_type, points_reward, start_date, end_date)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        return self.execute_update(query, (title, description, challenge_type, points_reward, start_date, end_date))

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
            SELECT fp.*, f.username, f.discord_id
            FROM fan_points fp
            JOIN fans f ON fp.fan_id = f.id
            ORDER BY fp.total_points DESC
            LIMIT ?
        """
        rows = self.execute_query(query, (limit,))
        return [dict(row) for row in rows]

    def log_event(self, event_type: str, fan_id: Optional[int] = None, event_data: Optional[str] = None) -> int:
        """Log engagement event"""
        query = "INSERT INTO engagement_events (event_type, fan_id, event_data) VALUES (?, ?, ?)"
        return self.execute_update(query, (event_type, fan_id, event_data))

    def submit_feedback(self, fan_id: Optional[int], feedback_type: str, rating: Optional[int] = None, comments: Optional[str] = None) -> int:
        """Submit fan feedback"""
        query = "INSERT INTO fan_feedback (fan_id, feedback_type, rating, comments) VALUES (?, ?, ?, ?)"
        return self.execute_update(query, (fan_id, feedback_type, rating, comments))

    def get_feedback_stats(self) -> List[Dict]:
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
        fan_id = db.create_fan("123456", "TestFan", "Giants", "Ohtani", "Tokyo")
        print("Created fan ID:", fan_id)

        fan = db.get_fan_by_discord_id("123456")
        print("Fan data:", json.dumps(fan, indent=2, ensure_ascii=False))

        challenge_id = db.create_challenge("Test Challenge", "Description", "quiz", 10)
        print("Created challenge ID:", challenge_id)

        success, points = db.complete_challenge(1, challenge_id)
        print("Challenge completed:", success, "Points:", points)

        leaderboard = db.get_leaderboard(5)
        print("Leaderboard:", json.dumps(leaderboard, indent=2, ensure_ascii=False))
"""

    return template.format(
        name=agent["name"],
        description_ja=agent["description_ja"],
        description_en=agent["description_en"]
    )
'''

# Write this to a file
with open("/workspace/generate_orchestrator_helpers.py", "w") as f:
    f.write(db_py_template)

print("Created helper file with db_py_template")
