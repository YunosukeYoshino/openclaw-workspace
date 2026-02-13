#!/usr/bin/env python3
"""
Baseball Fan Engagement Orchestrator
野球ファンエンゲージメント強化エージェントのオーケストレーター
"""

import json
import os
import subprocess
import sys
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

def load_progress():
    """Load progress status"""
    if PROGRESS_FILE.exists():
        with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return dict(agents={}, last_updated=None)

def save_progress(progress):
    """Save progress status"""
    progress["last_updated"] = datetime.now().isoformat()
    with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
        json.dump(progress, f, indent=2, ensure_ascii=False)

def create_agent_dir(agent):
    """Create agent directory"""
    agent_dir = AGENTS_DIR / agent["name"]
    agent_dir.mkdir(parents=True, exist_ok=True)
    return agent_dir

def generate_agent_py(agent):
    """Generate agent.py"""
    return f'''#!/usr/bin/env python3
"""
{agent['description_ja']} / {agent['description_en']}
{agent['name']}
"""

import sqlite3
from datetime import datetime
from pathlib import Path

class {agent['name'].replace('-', '_').title().replace('_', '')}Agent:
    """{agent['description_ja']}"""

    def __init__(self, db_path=None):
        self.db_path = db_path or Path("data/baseball_fan_engagement.db")
        self.conn = None
        self.init_db()

    def init_db(self):
        """Initialize database"""
        self.conn = sqlite3.connect(self.db_path)
        self.create_tables()

    def create_tables(self):
        """Create database tables"""
        cursor = self.conn.cursor()

        # Fans table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS fans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                discord_id TEXT UNIQUE NOT NULL,
                username TEXT,
                favorite_team TEXT,
                favorite_players TEXT,
                preferred_teams TEXT,
                interests TEXT,
                location TEXT,
                timezone TEXT,
                bio TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Fan profiles/preferences
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS fan_preferences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fan_id INTEGER NOT NULL,
                watch_style TEXT,
                social_level INTEGER DEFAULT 5,
                notification_preferences TEXT,
                language_preference TEXT DEFAULT 'ja',
                FOREIGN KEY (fan_id) REFERENCES fans(id)
            )
        """)

        # Fan connections/friendships
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS fan_connections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fan_id_1 INTEGER NOT NULL,
                fan_id_2 INTEGER NOT NULL,
                compatibility_score REAL,
                connection_type TEXT,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (fan_id_1) REFERENCES fans(id),
                FOREIGN KEY (fan_id_2) REFERENCES fans(id),
                UNIQUE(fan_id_1, fan_id_2)
            )
        """)

        # Watch parties
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS watch_parties (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                host_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                game_id TEXT,
                game_time TIMESTAMP,
                max_participants INTEGER DEFAULT 10,
                status TEXT DEFAULT 'scheduled',
                chat_enabled INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (host_id) REFERENCES fans(id)
            )
        """)

        # Watch party participants
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS party_participants (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                party_id INTEGER NOT NULL,
                fan_id INTEGER NOT NULL,
                joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (party_id) REFERENCES watch_parties(id),
                FOREIGN KEY (fan_id) REFERENCES fans(id),
                UNIQUE(party_id, fan_id)
            )
        """)

        # Fan stories/memories
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS fan_stories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fan_id INTEGER NOT NULL,
                title TEXT,
                content TEXT NOT NULL,
                game_date TEXT,
                team TEXT,
                location TEXT,
                media_urls TEXT,
                tags TEXT,
                is_public INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (fan_id) REFERENCES fans(id)
            )
        """)

        # Challenges and games
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS challenges (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                challenge_type TEXT NOT NULL,
                points_reward INTEGER DEFAULT 10,
                start_date TIMESTAMP,
                end_date TIMESTAMP,
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Challenge completions
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS challenge_completions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fan_id INTEGER NOT NULL,
                challenge_id INTEGER NOT NULL,
                completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                points_awarded INTEGER,
                FOREIGN KEY (fan_id) REFERENCES fans(id),
                FOREIGN KEY (challenge_id) REFERENCES challenges(id),
                UNIQUE(fan_id, challenge_id)
            )
        """)

        # Fan points and achievements
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS fan_points (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fan_id INTEGER NOT NULL,
                total_points INTEGER DEFAULT 0,
                current_rank TEXT,
                badges TEXT,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (fan_id) REFERENCES fans(id),
                UNIQUE(fan_id)
            )
        """)

        # Fan analytics data
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS fan_analytics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fan_id INTEGER NOT NULL,
                metric_name TEXT NOT NULL,
                metric_value REAL,
                recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (fan_id) REFERENCES fans(id)
            )
        """)

        # Engagement events
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS engagement_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT NOT NULL,
                fan_id INTEGER,
                event_data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (fan_id) REFERENCES fans(id)
            )
        """)

        # Fan feedback
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS fan_feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fan_id INTEGER,
                feedback_type TEXT NOT NULL,
                rating INTEGER,
                comments TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (fan_id) REFERENCES fans(id)
            )
        """)

        self.conn.commit()

    def register_fan(self, discord_id, username, favorite_team=None, favorite_players=None):
        """Register a new fan"""
        cursor = self.conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO fans (discord_id, username, favorite_team, favorite_players)
                VALUES (?, ?, ?, ?)
            """, (discord_id, username, favorite_team, favorite_players))
            self.conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            # Fan already exists
            cursor.execute("SELECT id FROM fans WHERE discord_id = ?", (discord_id,))
            return cursor.fetchone()[0]

    def get_fan_by_discord_id(self, discord_id):
        """Get fan by Discord ID"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM fans WHERE discord_id = ?", (discord_id,))
        return cursor.fetchone()

    def calculate_compatibility(self, fan_id_1, fan_id_2):
        """Calculate compatibility score between two fans"""
        cursor = self.conn.cursor()

        # Get fan data
        cursor.execute("SELECT * FROM fans WHERE id = ?", (fan_id_1,))
        fan1 = cursor.fetchone()
        cursor.execute("SELECT * FROM fans WHERE id = ?", (fan_id_2,))
        fan2 = cursor.fetchone()

        if not fan1 or not fan2:
            return 0

        score = 0
        max_score = 100

        # Favorite team match
        if fan1[3] and fan2[3] and fan1[3] == fan2[3]:
            score += 40

        # Location match
        if fan1[6] and fan2[6] and fan1[6] == fan2[6]:
            score += 20

        # Interests overlap
        if fan1[5] and fan2[5]:
            interests1 = set(str(fan1[5]).split(','))
            interests2 = set(str(fan2[5]).split(','))
            if interests1 & interests2:
                overlap = len(interests1 & interests2) / len(interests1 | interests2) * 40
                score += overlap

        return min(score, max_score)

    def find_matching_fans(self, fan_id, limit=5):
        """Find compatible fans for matching"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT id FROM fans WHERE id != ?", (fan_id,))
        other_fans = cursor.fetchall()

        matches = []
        for other in other_fans:
            other_id = other[0]
            score = self.calculate_compatibility(fan_id, other_id)
            if score > 30:  # Minimum threshold
                matches.append((other_id, score))

        # Sort by compatibility score
        matches.sort(key=lambda x: x[1], reverse=True)
        return matches[:limit]

    def create_watch_party(self, host_id, title, description, game_id=None, game_time=None, max_participants=10):
        """Create a watch party"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO watch_parties (host_id, title, description, game_id, game_time, max_participants)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (host_id, title, description, game_id, game_time, max_participants))
        self.conn.commit()
        return cursor.lastrowid

    def join_watch_party(self, party_id, fan_id):
        """Join a watch party"""
        cursor = self.conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO party_participants (party_id, fan_id)
                VALUES (?, ?)
            """, (party_id, fan_id))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def get_watch_parties(self, status='scheduled'):
        """Get watch parties"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM watch_parties WHERE status = ?", (status,))
        return cursor.fetchall()

    def create_fan_story(self, fan_id, title, content, game_date=None, team=None, media_urls=None, is_public=1):
        """Create a fan story"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO fan_stories (fan_id, title, content, game_date, team, media_urls, is_public)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (fan_id, title, content, game_date, team, media_urls, is_public))
        self.conn.commit()
        return cursor.lastrowid

    def get_fan_stories(self, fan_id=None, limit=20):
        """Get fan stories"""
        cursor = self.conn.cursor()
        if fan_id:
            cursor.execute("""
                SELECT * FROM fan_stories WHERE fan_id = ? ORDER BY created_at DESC LIMIT ?
            """, (fan_id, limit))
        else:
            cursor.execute("""
                SELECT * FROM fan_stories WHERE is_public = 1 ORDER BY created_at DESC LIMIT ?
            """, (limit,))
        return cursor.fetchall()

    def create_challenge(self, title, description, challenge_type, points_reward=10, start_date=None, end_date=None):
        """Create a challenge"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO challenges (title, description, challenge_type, points_reward, start_date, end_date)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (title, description, challenge_type, points_reward, start_date, end_date))
        self.conn.commit()
        return cursor.lastrowid

    def complete_challenge(self, fan_id, challenge_id):
        """Complete a challenge and award points"""
        cursor = self.conn.cursor()
        try:
            # Get challenge points
            cursor.execute("SELECT points_reward FROM challenges WHERE id = ?", (challenge_id,))
            challenge = cursor.fetchone()
            if not challenge:
                return False

            points_reward = challenge[0]

            # Record completion
            cursor.execute("""
                INSERT INTO challenge_completions (fan_id, challenge_id, points_awarded)
                VALUES (?, ?, ?)
            """, (fan_id, challenge_id, points_reward))

            # Update fan points
            cursor.execute("""
                INSERT INTO fan_points (fan_id, total_points)
                VALUES (?, ?)
                ON CONFLICT(fan_id) DO UPDATE SET
                    total_points = total_points + ?,
                    last_updated = CURRENT_TIMESTAMP
            """, (fan_id, points_reward, points_reward))

            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            # Already completed
            return False

    def get_fan_rankings(self, limit=10):
        """Get fan rankings by points"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT fp.*, f.username FROM fan_points fp
            JOIN fans f ON fp.fan_id = f.id
            ORDER BY fp.total_points DESC
            LIMIT ?
        """, (limit,))
        return cursor.fetchall()

    def log_engagement_event(self, event_type, fan_id=None, event_data=None):
        """Log engagement event"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO engagement_events (event_type, fan_id, event_data)
            VALUES (?, ?, ?)
        """, (event_type, fan_id, event_data))
        self.conn.commit()
        return cursor.lastrowid

    def submit_feedback(self, fan_id, feedback_type, rating=None, comments=None):
        """Submit fan feedback"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO fan_feedback (fan_id, feedback_type, rating, comments)
            VALUES (?, ?, ?, ?)
        """, (fan_id, feedback_type, rating, comments))
        self.conn.commit()
        return cursor.lastrowid

    def get_analytics_summary(self):
        """Get analytics summary"""
        cursor = self.conn.cursor()

        # Total fans
        cursor.execute("SELECT COUNT(*) FROM fans")
        total_fans = cursor.fetchone()[0]

        # Active watch parties
        cursor.execute("SELECT COUNT(*) FROM watch_parties WHERE status = 'scheduled'")
        active_parties = cursor.fetchone()[0]

        # Total stories
        cursor.execute("SELECT COUNT(*) FROM fan_stories")
        total_stories = cursor.fetchone()[0]

        # Engagement events
        cursor.execute("SELECT COUNT(*) FROM engagement_events")
        total_events = cursor.fetchone()[0]

        return dict(
            total_fans=total_fans,
            active_parties=active_parties,
            total_stories=total_stories,
            total_events=total_events
        )

    def get_close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()


if __name__ == "__main__":
    agent = {agent['name'].replace('-', '_').title().replace('_', '')}Agent()

    # Sample: Register fan
    fan_id = agent.register_fan("123456789", "TestFan", "Giants", "Ohtani,Suzuki")
    print(f"Registered fan ID: {{fan_id}}")

    # Sample: Create challenge
    challenge_id = agent.create_challenge("Home Run Predictor", "Predict today's home runs", "prediction", 50)
    print(f"Created challenge ID: {{challenge_id}}")

    # Sample: Get analytics
    summary = agent.get_analytics_summary()
    print(f"Analytics: {{summary}}")

    agent.get_close()
'''

def generate_db_py(agent):
    """Generate db.py"""
    return f'''#!/usr/bin/env python3
"""
{agent['description_ja']} データベース管理 / {agent['description_en']} Database Management
{agent['name']}
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
                updates.append(f"{{field}} = ?")
                params.append(value)

        if not updates:
            return False

        params.append(fan_id)
        query = f"UPDATE fans SET {{', '.join(updates)}}, updated_at = CURRENT_TIMESTAMP WHERE id = ?"
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
        return {{"event_type": event_type, "count": rows[0]['count']}}

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
        print(f"Created fan ID: {{fan_id}}")

        # Test: Get fan
        fan = db.get_fan_by_discord_id("123456")
        print(f"Fan data: {{json.dumps(fan, indent=2, ensure_ascii=False)}}")

        # Test: Create challenge
        challenge_id = db.create_challenge("Test Challenge", "Description", "quiz", 10)
        print(f"Created challenge ID: {{challenge_id}}")

        # Test: Complete challenge
        success, points = db.complete_challenge(1, challenge_id)
        print(f"Challenge completed: {{success}}, Points: {{points}}")

        # Test: Get leaderboard
        leaderboard = db.get_leaderboard(5)
        print(f"Leaderboard: {{json.dumps(leaderboard, indent=2, ensure_ascii=False)}}")
'''

def generate_discord_py(agent):
    """Generate discord.py"""
    return f'''#!/usr/bin/env python3
"""
{agent['description_ja']} Discord連携 / {agent['description_en']} Discord Integration
{agent['name']}
"""

import os
from datetime import datetime
from pathlib import Path

# Discord Bot Token (from environment)
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN", "")

# Database import
import sys
sys.path.insert(0, str(Path(__file__).parent))
from db import BaseballFanEngagementDB


class {agent['name'].replace('-', '_').title().replace('_', '')}Discord:
    """Discord Bot Interface for Fan Engagement"""

    def __init__(self):
        self.db = BaseballFanEngagementDB()

    def parse_command(self, content: str) -> dict:
        """Parse command"""
        parts = content.strip().split()
        if len(parts) < 2:
            return {{"error": "Invalid command"}}

        command = parts[1].lower()
        args = parts[2:] if len(parts) > 2 else []

        return {{
            "command": command,
            "args": args
        }}

    def handle_register(self, user_id: str, username: str, args: list) -> dict:
        """Handle registration command"""
        team = args[0] if len(args) > 0 else None
        players = args[1] if len(args) > 1 else None
        location = args[2] if len(args) > 2 else None

        fan_id = self.db.create_fan(user_id, username, team, players, location)

        return {{
            "success": True,
            "command": "register",
            "message": f"✅ 登録完了！\\nユーザー: {{username}}\\nチーム: {{team or '未設定'}}\\n場所: {{location or '未設定'}}"
        }}

    def handle_match(self, user_id: str, args: list) -> dict:
        """Handle find match command"""
        fan = self.db.get_fan_by_discord_id(user_id)
        if not fan:
            return {{
                "success": False,
                "error": "先に !bf register で登録してください"
            }}

        limit = int(args[0]) if len(args) > 0 and args[0].isdigit() else 5
        matches = self.db.find_matches(fan['id'], limit=limit, min_score=30.0)

        if not matches:
            return {{
                "success": True,
                "command": "match",
                "message": "🔍 一致するファンが見つかりませんでした"
            }}

        lines = [f"🎯 おすすめのマッチ ({{len(matches)}}件):\\n"]

        for i, match in enumerate(matches[:10], 1):
            lines.append(
                f"{{i}}. {{match['username']}}\\n"
                f"   チーム: {{match.get('favorite_team', '-')}}\\n"
                f"   相性: {{match['compatibility_score']:.1f}}%\\n"
            )

        return {{
            "success": True,
            "command": "match",
            "message": "\\n".join(lines)
        }}

    def handle_party(self, user_id: str, args: list) -> dict:
        """Handle watch party commands"""
        fan = self.db.get_fan_by_discord_id(user_id)
        if not fan:
            return {{"success": False, "error": "登録が必要です"}}

        subcommand = args[0].lower() if len(args) > 0 else "list"

        if subcommand == "create" or subcommand == "new":
            title = " ".join(args[1:])
            party_id = self.db.create_watch_party(
                fan['id'],
                title,
                description=None,
                max_participants=10
            )
            return {{
                "success": True,
                "command": "party",
                "message": f"📺 観戦パーティーを作成しました！\\nID: {{party_id}}\\nタイトル: {{title}}"
            }}

        elif subcommand == "join":
            if len(args) < 2:
                return {{"success": False, "error": "パーティーIDを指定してください"}}

            party_id = int(args[1])
            if self.db.join_watch_party(party_id, fan['id']):
                return {{
                    "success": True,
                    "command": "party",
                    "message": f"✅ パーティー {{party_id}} に参加しました！"
                }}
            else:
                return {{
                    "success": False,
                    "error": "参加に失敗しました（既に参加済み？）"
                }}

        elif subcommand == "list":
            parties = self.db.get_watch_parties(status='scheduled', limit=10)
            if not parties:
                return {{
                    "success": True,
                    "command": "party",
                    "message": "📺 現在開催中のパーティーはありません"
                }}

            lines = ["📺 開催中の観戦パーティー:\\n"]
            for party in parties[:10]:
                lines.append(
                    f"ID: {{party['id']}} - {{party['title']}}\\n"
                    f"  最大参加者: {{party['max_participants']}}\\n"
                )

            return {{
                "success": True,
                "command": "party",
                "message": "\\n".join(lines)
            }}

        else:
            return {{"success": False, "error": "サブコマンド: create, join, list"}}

    def handle_story(self, user_id: str, args: list) -> dict:
        """Handle story commands"""
        fan = self.db.get_fan_by_discord_id(user_id)
        if not fan:
            return {{"success": False, "error": "登録が必要です"}}

        subcommand = args[0].lower() if len(args) > 0 else "list"

        if subcommand == "post":
            content = " ".join(args[1:])
            if not content:
                return {{"success": False, "error": "内容を入力してください"}}

            story_id = self.db.create_fan_story(
                fan['id'],
                None,
                content,
                is_public=True
            )
            return {{
                "success": True,
                "command": "story",
                "message": f"📖 ストーリーを投稿しました！\\nID: {{story_id}}"
            }}

        elif subcommand == "list":
            limit = int(args[1]) if len(args) > 1 and args[1].isdigit() else 10
            stories = self.db.get_fan_stories(is_public=True, limit=limit)

            if not stories:
                return {{
                    "success": True,
                    "command": "story",
                    "message": "📖 ストーリーはまだありません"
                }}

            lines = ["📖 ファンストーリー:\\n"]
            for story in stories[:10]:
                lines.append(
                    f"{{story['username']}}:\\n"
                    f"  {{story['content'][:100]}}...\\n"
                )

            return {{
                "success": True,
                "command": "story",
                "message": "\\n".join(lines)
            }}

        elif subcommand == "mine":
            limit = int(args[1]) if len(args) > 1 and args[1].isdigit() else 10
            stories = self.db.get_fan_stories(fan_id=fan['id'], limit=limit)

            if not stories:
                return {{
                    "success": True,
                    "command": "story",
                    "message": "📖 あなたのストーリーはまだありません"
                }}

            lines = [f"📖 あなたのストーリー ({{len(stories)}}件):\\n"]
            for story in stories[:10]:
                lines.append(f"  {{story['content'][:80]}}...\\n")

            return {{
                "success": True,
                "command": "story",
                "message": "\\n".join(lines)
            }}

        else:
            return {{"success": False, "error": "サブコマンド: post, list, mine"}}

    def handle_challenge(self, user_id: str, args: list) -> dict:
        """Handle challenge commands"""
        fan = self.db.get_fan_by_discord_id(user_id)
        if not fan:
            return {{"success": False, "error": "登録が必要です"}}

        subcommand = args[0].lower() if len(args) > 0 else "list"

        if subcommand == "list":
            challenges = self.db.get_challenges(is_active=True, limit=10)

            if not challenges:
                return {{
                    "success": True,
                    "command": "challenge",
                    "message": "🎮 チャレンジはまだありません"
                }}

            lines = ["🎮 チャレンジ一覧:\\n"]
            for challenge in challenges[:10]:
                lines.append(
                    f"ID: {{challenge['id']}} - {{challenge['title']}}\\n"
                    f"  報酬: {{challenge['points_reward']}} ポイント\\n"
                )

            return {{
                "success": True,
                "command": "challenge",
                "message": "\\n".join(lines)
            }}

        elif subcommand == "complete":
            if len(args) < 2:
                return {{"success": False, "error": "チャレンジIDを指定してください"}}

            challenge_id = int(args[1])
            success, points = self.db.complete_challenge(fan['id'], challenge_id)

            if success:
                return {{
                    "success": True,
                    "command": "challenge",
                    "message": f"🎉 チャレンジ完了！\\n獲得ポイント: {{points}}"
                }}
            else:
                return {{
                    "success": False,
                    "error": "完了に失敗しました（既に完了済み？）"
                }}

        elif subcommand == "points":
            fan_points = self.db.get_fan_points(fan['id'])
            if not fan_points:
                return {{
                    "success": True,
                    "command": "challenge",
                    "message": "まだポイントがありません"
                }}

            return {{
                "success": True,
                "command": "challenge",
                "message": f"🏆 あなたのポイント: {{fan_points['total_points']}}\\nランク: {{fan_points.get('current_rank', '-')}}"
            }}

        elif subcommand == "leaderboard":
            limit = int(args[1]) if len(args) > 1 and args[1].isdigit() else 10
            leaderboard = self.db.get_leaderboard(limit=limit)

            if not leaderboard:
                return {{
                    "success": True,
                    "command": "challenge",
                    "message": "リーダーボードはまだありません"
                }}

            lines = ["🏆 ポイントリーダーボード:\\n"]
            for i, entry in enumerate(leaderboard[:10], 1):
                lines.append(f"{{i}}. {{entry['username']}} - {{entry['total_points']}} ポイント\\n")

            return {{
                "success": True,
                "command": "challenge",
                "message": "\\n".join(lines)
            }}

        else:
            return {{"success": False, "error": "サブコマンド: list, complete, points, leaderboard"}}

    def handle_analytics(self, user_id: str, args: list) -> dict:
        """Handle analytics commands"""
        subcommand = args[0].lower() if len(args) > 0 else "summary"

        if subcommand == "summary":
            fan = self.db.get_fan_by_discord_id(user_id)
            if not fan:
                return {{"success": False, "error": "登録が必要です"}}

            fan_points = self.db.get_fan_points(fan['id'])
            event_stats = self.db.get_event_stats(event_type=None, days=30)

            lines = [f"📊 アクティビティサマリー\\n"]
            lines.append(f"ユーザー: {{fan['username']}}\\n")
            lines.append(f"チーム: {{fan.get('favorite_team', '未設定')}}\\n")
            lines.append(f"ポイント: {{fan_points['total_points'] if fan_points else 0}}\\n")
            lines.append(f"総イベント数: {{event_stats['count']}}\\n")

            return {{
                "success": True,
                "command": "analytics",
                "message": "\\n".join(lines)
            }}

        elif subcommand == "leaderboard":
            limit = int(args[1]) if len(args) > 1 and args[1].isdigit() else 10
            leaderboard = self.db.get_leaderboard(limit=limit)

            if not leaderboard:
                return {{
                    "success": True,
                    "command": "analytics",
                    "message": "リーダーボードはまだありません"
                }}

            lines = ["📊 アクティビティリーダーボード:\\n"]
            for i, entry in enumerate(leaderboard[:10], 1):
                lines.append(f"{{i}}. {{entry['username']}} - {{entry['total_points']}} ポイント\\n")

            return {{
                "success": True,
                "command": "analytics",
                "message": "\\n".join(lines)
            }}

        else:
            return {{"success": False, "error": "サブコマンド: summary, leaderboard"}}

    def handle_feedback(self, user_id: str, args: list) -> dict:
        """Handle feedback command"""
        fan = self.db.get_fan_by_discord_id(user_id)

        if not args:
            return {{
                "success": False,
                "error": "Usage: !bf feedback <feedback_type> <comments>"
            }}

        feedback_type = args[0]
        comments = " ".join(args[1:]) if len(args) > 1 else None

        fan_id = fan['id'] if fan else None
        self.db.submit_feedback(fan_id, feedback_type, None, comments)

        return {{
            "success": True,
            "command": "feedback",
            "message": f"📝 フィードバックありがとうございます！\\nタイプ: {{feedback_type}}"
        }}

    def handle_help(self, user_id: str, args: list) -> dict:
        """Handle help command"""
        help_text = """
🎮 野球ファンエンゲージメント Bot コマンド一覧

👤 **ユーザー管理**
- `!bf register <team> [players] [location]` - ユーザー登録
- `!bf profile` - プロフィール確認

🤝 **マッチング**
- `!bf match [limit]` - おすすめファンを検索

📺 **観戦パーティー**
- `!bf party create <title>` - パーティー作成
- `!bf party join <party_id>` - パーティー参加
- `!bf party list` - パーティー一覧

📖 **ファンストーリー**
- `!bf story post <content>` - ストーリー投稿
- `!bf story list [limit]` - ストーリー一覧
- `!bf story mine` - 自分のストーリー

🎮 **チャレンジ**
- `!bf challenge list` - チャレンジ一覧
- `!bf challenge complete <id>` - チャレンジ完了
- `!bf challenge points` - ポイント確認
- `!bf challenge leaderboard` - リーダーボード

📊 **分析**
- `!bf analytics summary` - アクティビティサマリー
- `!bf analytics leaderboard` - リーダーボード

📝 **フィードバック**
- `!bf feedback <type> <comments>` - フィードバック送信

❓ `!bf help` - このヘルプを表示
"""

        return {{
            "success": True,
            "command": "help",
            "message": help_text.strip()
        }}

    def handle_command(self, user_id: str, username: str, content: str) -> dict:
        """Handle incoming command"""
        parsed = self.parse_command(content)

        if "error" in parsed:
            return {{"error": "Invalid command format"}}

        command = parsed["command"]
        args = parsed["args"]

        # Command router
        handlers = {{
            "register": self.handle_register,
            "match": self.handle_match,
            "party": self.handle_party,
            "story": self.handle_story,
            "challenge": self.handle_challenge,
            "analytics": self.handle_analytics,
            "feedback": self.handle_feedback,
            "help": self.handle_help
        }}

        handler = handlers.get(command)
        if handler:
            return handler(user_id, username, args)
        else:
            return {{
                "error": f"Unknown command: {{command}}\\nUse !bf help for available commands"
            }}

    def format_response(self, response: dict) -> str:
        """Format response for Discord"""
        if "error" in response:
            return f"❌ {{response['error']}}"

        if "message" in response:
            emoji_map = {{
                "register": "👤",
                "match": "🎯",
                "party": "📺",
                "story": "📖",
                "challenge": "🎮",
                "analytics": "📊",
                "feedback": "📝",
                "help": "❓"
            }}
            command = response.get("command", "")
            emoji = emoji_map.get(command, "✅")
            return f"{{emoji}} {{response['message']}}"

        return "✅ コマンドを実行しました"


if __name__ == "__main__":
    bot = {agent['name'].replace('-', '_').title().replace('_', '')}Discord()

    # Test commands
    user_id = "test-user-123"
    username = "TestFan"

    print("=== コマンドテスト ===\\n")

    # Test: help
    result = bot.handle_command(user_id, username, "!bf help")
    print(f"help:\\n{{bot.format_response(result)}}\\n")

    # Test: register
    result = bot.handle_command(user_id, username, "!bf register Giants Ohtani Tokyo")
    print(f"register:\\n{{bot.format_response(result)}}\\n")

    # Test: match
    result = bot.handle_command(user_id, username, "!bf match 3")
    print(f"match:\\n{{bot.format_response(result)}}\\n")

    # Test: challenge list
    result = bot.handle_command(user_id, username, "!bf challenge list")
    print(f"challenge list:\\n{{bot.format_response(result)}}\\n")
'''

def generate_readme(agent):
    """Generate README.md"""
    return f'''# {{agent['name']}}

{{agent['emoji']}} {{agent['description_ja']}} / {{agent['description_en']}}

## 概要 (Overview)

このエージェントは、野球ファン同士の交流を促進し、ライブ視聴体験を強化し、ファンコミュニティを活性化します。マッチメイキング、観戦パーティー、ファンストーリー、チャレンジ、分析機能を提供します。

This agent promotes interaction between baseball fans, enhances live viewing experiences, and activates fan communities. It provides matchmaking, watch parties, fan stories, challenges, and analytics features.

## 機能 (Features)

### 野球ファンマッチメイキング (Baseball Fan Matchmaking)
- 趣味・チーム・観戦スタイルが似ているファンを自動マッチング
- ソーシャルメディア分析による相性スコア計算
- 観戦同行の提案、ファン交流イベントの自動企画
- Find and match fans with similar interests, teams, and viewing styles
- Calculate compatibility scores based on social media analysis
- Suggest game-watching companions and automatically organize fan events

### 野球観戦パーティー (Baseball Watch Party)
- 仮想視聴パーティーの開催・管理
- チャット機能、リアクション、ゲーム連動企画の実装
- ライブ投票、プレディクション、ビンゴゲームの統合
- Host and manage virtual watch parties
- Implement chat features, reactions, and game-interactive activities
- Integrate live voting, predictions, and bingo games

### 野球ファンストーリー (Baseball Fan Stories)
- ファンからの観戦記録、思い出の収集・共有
- 写真、ビデオ、感想の統合管理
- タイムライン形式での表示、検索、アーカイブ機能
- Collect and share fan game records and memories
- Unified management of photos, videos, and impressions
- Timeline display, search, and archive features

### 野球ファンチャレンジ (Baseball Fan Challenges)
- ファン向けゲーム、クイズ、チャレンジタスクの作成・管理
- ポイントシステム、ランク付け、バッジ・報酬の付与
- シーズンごとのイベント、スペシャルチャレンジ企画
- Create and manage fan-facing games, quizzes, and challenge tasks
- Point system, ranking, badges, and rewards
- Seasonal events and special challenge campaigns

### 野球ファン分析 (Baseball Fan Analytics)
- ファン行動パターンの分析、トレンド抽出
- チーム別・選手別ファン人気度の可視化
- ファン満足度アンケート、フィードバック収集・分析
- Analyze fan behavior patterns and extract trends
- Visualize team and player popularity among fans
- Collect and analyze fan satisfaction surveys and feedback

## インストール (Installation)

```bash
pip install -r requirements.txt
```

## 使い方 (Usage)

### Python API

```python
from agent import {{agent['name'].replace('-', '_').title().replace('_', '')}}Agent

# エージェント初期化 / Initialize agent
agent = {{agent['name'].replace('-', '_').title().replace('_', '')}}Agent()

# ファン登録 / Register fan
fan_id = agent.register_fan("discord_id_123", "FanName", favorite_team="Giants")

# マッチング / Find matches
matches = agent.find_matching_fans(fan_id, limit=5)

# 観戦パーティー作成 / Create watch party
party_id = agent.create_watch_party(fan_id, "Opening Day Party", "Let's watch together!")

# ストーリー作成 / Create story
story_id = agent.create_fan_story(fan_id, "Great Game!", "Best game ever...", team="Giants")

# チャレンジ完了 / Complete challenge
agent.complete_challenge(fan_id, challenge_id=1)

# 接続を閉じる / Close connection
agent.get_close()
```

### Discord Bot Commands

**ユーザー管理 / User Management**
```
!bf register <team> [players] [location] - ユーザー登録 / Register user
!bf profile - プロフィール確認 / View profile
```

**マッチング / Matchmaking**
```
!bf match [limit] - おすすめファンを検索 / Find recommended fans
```

**観戦パーティー / Watch Parties**
```
!bf party create <title> - パーティー作成 / Create party
!bf party join <party_id> - パーティー参加 / Join party
!bf party list - パーティー一覧 / List parties
```

**ファンストーリー / Fan Stories**
```
!bf story post <content> - ストーリー投稿 / Post story
!bf story list [limit] - ストーリー一覧 / List stories
!bf story mine - 自分のストーリー / My stories
```

**チャレンジ / Challenges**
```
!bf challenge list - チャレンジ一覧 / List challenges
!bf challenge complete <id> - チャレンジ完了 / Complete challenge
!bf challenge points - ポイント確認 / Check points
!bf challenge leaderboard - リーダーボード / Leaderboard
```

**分析 / Analytics**
```
!bf analytics summary - アクティビティサマリー / Activity summary
!bf analytics leaderboard - リーダーボード / Leaderboard
```

**フィードバック / Feedback**
```
!bf feedback <type> <comments> - フィードバック送信 / Send feedback
```

**ヘルプ / Help**
```
!bf help - コマンド一覧 / Command list
```

## データベース構造 (Database Schema)

### fans (ファン情報 / Fan Information)
- id: ユニークID
- discord_id: DiscordユーザーID
- username: ユーザー名
- favorite_team: 好きなチーム
- favorite_players: 好きな選手
- location: 場所
- interests: 興味

### fan_connections (ファン接続 / Fan Connections)
- compatibility_score: 相性スコア
- connection_type: 接続タイプ
- status: ステータス

### watch_parties (観戦パーティー / Watch Parties)
- host_id: ホストID
- title: タイトル
- game_id: 試合ID
- game_time: 試合時間
- max_participants: 最大参加者数

### fan_stories (ファンストーリー / Fan Stories)
- fan_id: ファンID
- title: タイトル
- content: 内容
- game_date: 試合日
- team: チーム
- media_urls: メディアURL

### challenges (チャレンジ / Challenges)
- title: タイトル
- description: 説明
- challenge_type: タイプ
- points_reward: ポイント報酬

### fan_points (ファンポイント / Fan Points)
- fan_id: ファンID
- total_points: 総ポイント
- current_rank: 現在のランク
- badges: バッジ

### engagement_events (エンゲージメントイベント / Engagement Events)
- event_type: イベントタイプ
- fan_id: ファンID
- event_data: イベントデータ

### fan_feedback (ファンフィードバック / Fan Feedback)
- feedback_type: フィードバックタイプ
- rating: 評価
- comments: コメント

## 環境変数 (Environment Variables)

- `DISCORD_TOKEN`: Discordボットトークン

## ポイントシステム (Point System)

- チャレンジ完了: 各チャレンジの報酬ポイント
- ストーリー投稿: +5 ポイント
- 観戦パーティー参加: +3 ポイント
- マッチング成功: +2 ポイント

## バッジ・ランク (Badges & Ranks)

- **Bronze**: 0-99 ポイント
- **Silver**: 100-499 ポイント
- **Gold**: 500-999 ポイント
- **Platinum**: 1000+ ポイント

特別バッジ:
- 🏆 MVP: トップ10入賞
- 🌟 Super Fan: 100以上のチャレンジ完了
- 🔥 Streak Master: 連続7日チャレンジ完了

## コントリビューション (Contributing)

プルリクエスト、イシュー、フィードバックを歓迎します！
Pull requests, issues, and feedback are welcome!

## ライセンス (License)

MIT License
'''

def generate_requirements_txt(agent):
    """Generate requirements.txt"""
    return '''# Baseball Fan Engagement Agent Requirements

# Core
python-dotenv>=1.0.0

# Discord
discord.py>=2.3.0

# Database
sqlite3  # Python standard library

# Data Analysis
pandas>=2.0.0
numpy>=1.24.0

# Data Visualization
matplotlib>=3.7.0
seaborn>=0.12.0

# Text Processing
nltk>=3.8.0

# Date/Time
python-dateutil>=2.8.2
'''

def create_agent_files(agent_dir, agent):
    """Create agent files"""
    # agent.py
    with open(agent_dir / "agent.py", "w", encoding="utf-8") as f:
        f.write(generate_agent_py(agent))

    # db.py
    with open(agent_dir / "db.py", "w", encoding="utf-8") as f:
        f.write(generate_db_py(agent))

    # discord.py
    with open(agent_dir / "discord.py", "w", encoding="utf-8") as f:
        f.write(generate_discord_py(agent))

    # README.md
    with open(agent_dir / "README.md", "w", encoding="utf-8") as f:
        f.write(generate_readme(agent))

    # requirements.txt
    with open(agent_dir / "requirements.txt", "w", encoding="utf-8") as f:
        f.write(generate_requirements_txt(agent))

def verify_agent(agent_dir, agent):
    """Verify agent files"""
    required_files = ["agent.py", "db.py", "discord.py", "README.md", "requirements.txt"]
    all_exist = True

    for filename in required_files:
        file_path = agent_dir / filename
        if file_path.exists():
            size = file_path.stat().st_size
            print(f"  ✅ {filename} ({size} bytes)")
        else:
            print(f"  ❌ {filename} missing")
            all_exist = False

    return all_exist

def commit_changes(message):
    """Commit changes"""
    try:
        subprocess.run(
            ["git", "add", "-A"],
            cwd=WORKSPACE,
            capture_output=True,
            text=True
        )

        result = subprocess.run(
            ["git", "commit", "-m", message],
            cwd=WORKSPACE,
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            print(f"  ✅ Committed: {message}")
            return True
        else:
            print(f"  ❌ Commit failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"  ❌ Git error: {e}")
        return False

def push_changes():
    """Push changes"""
    try:
        result = subprocess.run(
            ["git", "push"],
            cwd=WORKSPACE,
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            print(f"  ✅ Pushed to remote")
            return True
        else:
            print(f"  ❌ Push failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"  ❌ Git error: {e}")
        return False

def main():
    """Main processing"""
    print("=" * 60)
    print("野球ファンエンゲージメント強化エージェント オーケストレーター")
    print("Baseball Fan Engagement Agent Orchestrator")
    print("=" * 60)

    progress = load_progress()
    existing_agents = progress.get('agents', {})
    print(f"\n既存の進捗: {existing_agents}")

    completed_count = 0
    for agent in AGENTS:
        agent_name = agent["name"]
        agent_dir = AGENTS_DIR / agent_name

        print(f"\n🔧 作成中: {agent_name}")
        print(f"   {agent['description_ja']}")

        # ディレクトリ作成 / Create directory
        create_agent_dir(agent)

        # ファイル作成 / Create files
        print("  ファイル作成中...")
        create_agent_files(agent_dir, agent)

        # 検証 / Verify
        print("  検証中...")
        if verify_agent(agent_dir, agent):
            progress["agents"][agent_name] = {
                "status": "completed",
                "timestamp": datetime.now().isoformat()
            }
            completed_count += 1
        else:
            progress["agents"][agent_name] = {
                "status": "failed",
                "timestamp": datetime.now().isoformat()
            }

    # 進捗保存 / Save progress
    save_progress(progress)

    # 統計 / Statistics
    total = len(AGENTS)
    print(f"\n{'=' * 60}")
    print(f"📊 統計 (Statistics)")
    print(f"   完了: {completed_count}/{total}")
    print(f"   成功率: {completed_count/total*100:.1f}%")
    print(f"{'=' * 60}")

    # Git commit & push
    if completed_count > 0:
        print(f"\n📦 Git commit & push...")
        if commit_changes(f"feat: 野球ファンエンゲージメント強化エージェントプロジェクト完了 ({completed_count}/{total})"):
            push_changes()

    print(f"\n🎉 オーケストレーション完了！")
    print(f"\n作成されたエージェント:")
    for agent in AGENTS:
        status = progress["agents"].get(agent["name"], {}).get("status", "pending")
        emoji = "✅" if status == "completed" else "❌"
        print(f"  {emoji} {agent['name']} - {agent['description_ja']}")

if __name__ == "__main__":
    main()
