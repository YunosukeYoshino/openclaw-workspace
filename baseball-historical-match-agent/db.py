#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Baseball Historical Match Agent - SQLite Database
野球歴史的名試合エージェント - SQLite データベース
"""

import aiosqlite
from datetime import datetime
from typing import List, Dict, Optional
import os

class BaseballHistoricalMatchDB:
    """Baseball Historical Match Database Handler"""

    def __init__(self, db_path: str = None):
        """Initialize database"""
        if db_path is None:
            db_path = os.path.join(os.path.dirname(__file__), 'baseball_matches.db')
        self.db_path = db_path

    async def get_connection(self):
        """Get async database connection"""
        return await aiosqlite.connect(self.db_path)

    async def init_db(self):
        """Initialize database tables"""
        conn = await self.get_connection()
        cursor = await conn.cursor()

        # Historical Matches table (歴史的名試合)
        await cursor.execute('''
            CREATE TABLE IF NOT EXISTS matches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                match_date DATE NOT NULL,
                league TEXT,
                season INTEGER,
                home_team TEXT NOT NULL,
                away_team TEXT NOT NULL,
                home_score INTEGER,
                away_score INTEGER,
                venue TEXT,
                attendance INTEGER,
                match_type TEXT,  -- world_series, all_star, playoff, regular_season
                importance_level TEXT,  -- legendary, historic, memorable
                duration_innings INTEGER,
                description TEXT,
                key_players TEXT,  -- JSON array
                key_moments TEXT,  -- JSON array
                records_broken TEXT,  -- JSON array
                video_url TEXT,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Key Moments table (重要な局面)
        await cursor.execute('''
            CREATE TABLE IF NOT EXISTS key_moments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                match_id INTEGER,
                inning INTEGER,
                description TEXT NOT NULL,
                player TEXT,
                moment_type TEXT,  -- home_run, strikeout, catch, error, etc.
                impact_level TEXT,  -- game_changer, record_breaker, clutch
                timestamp_offset INTEGER,  -- Minutes into the match
                media_url TEXT,
                FOREIGN KEY (match_id) REFERENCES matches(id)
            )
        ''')

        # Player Performances table (選手パフォーマンス)
        await cursor.execute('''
            CREATE TABLE IF NOT EXISTS player_performances (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                match_id INTEGER,
                player_name TEXT NOT NULL,
                team TEXT,
                position TEXT,
                at_bats INTEGER,
                hits INTEGER,
                home_runs INTEGER,
                rbis INTEGER,
                strikeouts INTEGER,
                pitching_ip REAL,
                pitching_so INTEGER,
                pitching_era REAL,
                highlights TEXT,  -- JSON array
                notes TEXT,
                FOREIGN KEY (match_id) REFERENCES matches(id)
            )
        ''')

        # Anniversaries and Events table (記念日・イベント)
        await cursor.execute('''
            CREATE TABLE IF NOT EXISTS anniversaries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                match_id INTEGER,
                event_date DATE NOT NULL,
                event_type TEXT,  -- anniversary, commemoration, celebration
                description TEXT,
                years_since INTEGER,
                celebration_details TEXT,
                FOREIGN KEY (match_id) REFERENCES matches(id)
            )
        ''')

        await conn.commit()
        await conn.close()

    # Matches Operations
    async def add_match(self, match_date: str, home_team: str, away_team: str,
                       home_score: int, away_score: int, league: str = None,
                       season: int = None, venue: str = None, match_type: str = 'regular_season',
                       importance_level: str = 'memorable', description: str = None,
                       key_players: str = None, key_moments: str = None,
                       records_broken: str = None, video_url: str = None) -> int:
        """Add a historical match"""
        conn = await self.get_connection()
        cursor = await conn.cursor()
        await cursor.execute('''
            INSERT INTO matches
            (match_date, league, season, home_team, away_team, home_score, away_score,
             venue, match_type, importance_level, description, key_players, key_moments,
             records_broken, video_url)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (match_date, league, season, home_team, away_team, home_score, away_score,
              venue, match_type, importance_level, description, key_players, key_moments,
              records_broken, video_url))
        match_id = cursor.lastrowid
        await conn.commit()
        await conn.close()
        return match_id

    async def get_matches(self, league: str = None, season: int = None,
                         match_type: str = None, importance_level: str = None,
                         limit: int = 20) -> List[Dict]:
        """Get historical matches with optional filters"""
        conn = await self.get_connection()
        cursor = await conn.cursor()

        query = 'SELECT * FROM matches WHERE 1=1'
        params = []

        if league:
            query += ' AND league = ?'
            params.append(league)
        if season:
            query += ' AND season = ?'
            params.append(season)
        if match_type:
            query += ' AND match_type = ?'
            params.append(match_type)
        if importance_level:
            query += ' AND importance_level = ?'
            params.append(importance_level)

        query += ' ORDER BY match_date DESC LIMIT ?'
        params.append(limit)

        await cursor.execute(query, params)
        rows = await cursor.fetchall()
        await conn.close()

        columns = [description[0] for description in cursor.description]
        return [dict(zip(columns, row)) for row in rows]

    async def get_match(self, match_id: int) -> Optional[Dict]:
        """Get a specific match by ID"""
        conn = await self.get_connection()
        cursor = await conn.cursor()
        await cursor.execute('SELECT * FROM matches WHERE id = ?', (match_id,))
        row = await cursor.fetchone()
        await conn.close()

        if row:
            columns = [description[0] for description in cursor.description]
            return dict(zip(columns, row))
        return None

    # Key Moments Operations
    async def add_key_moment(self, match_id: int, inning: int, description: str,
                           player: str = None, moment_type: str = None,
                           impact_level: str = 'clutch', timestamp_offset: int = None,
                           media_url: str = None) -> int:
        """Add a key moment to a match"""
        conn = await self.get_connection()
        cursor = await conn.cursor()
        await cursor.execute('''
            INSERT INTO key_moments
            (match_id, inning, description, player, moment_type, impact_level,
             timestamp_offset, media_url)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (match_id, inning, description, player, moment_type,
              impact_level, timestamp_offset, media_url))
        moment_id = cursor.lastrowid
        await conn.commit()
        await conn.close()
        return moment_id

    async def get_key_moments(self, match_id: int) -> List[Dict]:
        """Get all key moments for a match"""
        conn = await self.get_connection()
        cursor = await conn.cursor()
        await cursor.execute('''
            SELECT * FROM key_moments WHERE match_id = ? ORDER BY inning ASC
        ''', (match_id,))
        rows = await cursor.fetchall()
        await conn.close()

        columns = [description[0] for description in cursor.description]
        return [dict(zip(columns, row)) for row in rows]

    # Player Performances Operations
    async def add_player_performance(self, match_id: int, player_name: str, team: str,
                                   position: str = None, at_bats: int = None,
                                   hits: int = None, home_runs: int = None,
                                   rbis: int = None, strikeouts: int = None,
                                   pitching_ip: float = None, pitching_so: int = None,
                                   pitching_era: float = None, highlights: str = None) -> int:
        """Add player performance for a match"""
        conn = await self.get_connection()
        cursor = await conn.cursor()
        await cursor.execute('''
            INSERT INTO player_performances
            (match_id, player_name, team, position, at_bats, hits, home_runs,
             rbis, strikeouts, pitching_ip, pitching_so, pitching_era, highlights)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (match_id, player_name, team, position, at_bats, hits, home_runs,
              rbis, strikeouts, pitching_ip, pitching_so, pitching_era, highlights))
        perf_id = cursor.lastrowid
        await conn.commit()
        await conn.close()
        return perf_id

    async def get_player_performances(self, match_id: int) -> List[Dict]:
        """Get all player performances for a match"""
        conn = await self.get_connection()
        cursor = await conn.cursor()
        await cursor.execute('''
            SELECT * FROM player_performances WHERE match_id = ? ORDER BY team, player_name
        ''', (match_id,))
        rows = await cursor.fetchall()
        await conn.close()

        columns = [description[0] for description in cursor.description]
        return [dict(zip(columns, row)) for row in rows]

    # Anniversaries Operations
    async def add_anniversary(self, match_id: int, event_date: str, event_type: str,
                            description: str, years_since: int = None,
                            celebration_details: str = None) -> int:
        """Add an anniversary or commemorative event"""
        conn = await self.get_connection()
        cursor = await conn.cursor()
        await cursor.execute('''
            INSERT INTO anniversaries
            (match_id, event_date, event_type, description, years_since, celebration_details)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (match_id, event_date, event_type, description, years_since, celebration_details))
        anniversary_id = cursor.lastrowid
        await conn.commit()
        await conn.close()
        return anniversary_id

    async def get_upcoming_anniversaries(self, days: int = 90) -> List[Dict]:
        """Get upcoming anniversaries within specified days"""
        conn = await self.get_connection()
        cursor = await conn.cursor()
        await cursor.execute('''
            SELECT a.*, m.home_team, m.away_team, m.match_date as original_date
            FROM anniversaries a
            JOIN matches m ON a.match_id = m.id
            WHERE a.event_date >= date('now')
            AND a.event_date <= date('now', '+' || ? || ' days')
            ORDER BY a.event_date ASC
        ''', (days,))
        rows = await cursor.fetchall()
        await conn.close()

        columns = [description[0] for description in cursor.description]
        return [dict(zip(columns, row)) for row in rows]

    async def get_summary(self) -> Dict:
        """Get database summary"""
        conn = await self.get_connection()
        cursor = await conn.cursor()

        await cursor.execute("SELECT COUNT(*) FROM matches")
        total_matches = (await cursor.fetchone())[0]

        await cursor.execute("SELECT COUNT(*) FROM matches WHERE importance_level = 'legendary'")
        legendary_matches = (await cursor.fetchone())[0]

        await cursor.execute("SELECT COUNT(*) FROM key_moments")
        total_moments = (await cursor.fetchone())[0]

        await cursor.execute("SELECT COUNT(*) FROM anniversaries WHERE event_date >= date('now')")
        upcoming_anniversaries = (await cursor.fetchone())[0]

        await conn.close()

        return {
            'total_matches': total_matches,
            'legendary_matches': legendary_matches,
            'total_moments': total_moments,
            'upcoming_anniversaries': upcoming_anniversaries
        }


if __name__ == '__main__':
    import asyncio
    async def test():
        db = BaseballHistoricalMatchDB()
        await db.init_db()
        print("Database initialized successfully!")
        summary = await db.get_summary()
        print("\nSummary:", summary)

    asyncio.run(test())
