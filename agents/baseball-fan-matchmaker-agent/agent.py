#!/usr/bin/env python3
"""
野球ファンマッチメイキングエージェント / Baseball Fan Matchmaker Agent
baseball-fan-matchmaker-agent
"""

import sqlite3
from datetime import datetime
from pathlib import Path

class BaseballFanMatchmakerAgentAgent:
    """野球ファンマッチメイキングエージェント"""

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
    agent = BaseballFanMatchmakerAgentAgent()

    # Sample: Register fan
    fan_id = agent.register_fan("123456789", "TestFan", "Giants", "Ohtani,Suzuki")
    print(f"Registered fan ID: {fan_id}")

    # Sample: Create challenge
    challenge_id = agent.create_challenge("Home Run Predictor", "Predict today's home runs", "prediction", 50)
    print(f"Created challenge ID: {challenge_id}")

    # Sample: Get analytics
    summary = agent.get_analytics_summary()
    print(f"Analytics: {summary}")

    agent.get_close()
