#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Baseball Legend Profile Agent - SQLite Database
野球伝説選手プロフィールエージェント - SQLite データベース
"""

import aiosqlite
from datetime import datetime
from typing import List, Dict, Optional
import os

class BaseballLegendProfileDB:
    """Baseball Legend Profile Database Handler"""

    def __init__(self, db_path: str = None):
        """Initialize database"""
        if db_path is None:
            db_path = os.path.join(os.path.dirname(__file__), 'baseball_legends.db')
        self.db_path = db_path

    async def get_connection(self):
        """Get async database connection"""
        return await aiosqlite.connect(self.db_path)

    async def init_db(self):
        """Initialize database tables"""
        conn = await self.get_connection()
        cursor = await conn.cursor()

        # Legends table (伝説的選手)
        await cursor.execute('''
            CREATE TABLE IF NOT EXISTS legends (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_name TEXT NOT NULL,
                birth_date DATE,
                death_date DATE,
                birthplace TEXT,
                debut_year INTEGER,
                retirement_year INTEGER,
                primary_position TEXT,
                teams TEXT,  -- JSON array
                hall_of_fame BOOLEAN DEFAULT 0,
                hall_of_fame_year INTEGER,
                hall_of_fame_votes REAL,
                hall_of_fame_ballot TEXT,
                biography TEXT,
                photo_url TEXT,
                career_highlights TEXT,  -- JSON array
                nickname TEXT,
                height_cm INTEGER,
                weight_kg INTEGER,
                bats TEXT,  -- left, right, both
                throws TEXT,  -- left, right
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Career Statistics table (通算成績)
        await cursor.execute('''
            CREATE TABLE IF NOT EXISTS career_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                legend_id INTEGER,
                league TEXT,
                games INTEGER,
                at_bats INTEGER,
                runs INTEGER,
                hits INTEGER,
                doubles INTEGER,
                triples INTEGER,
                home_runs INTEGER,
                rbis INTEGER,
                stolen_bases INTEGER,
                batting_avg REAL,
                on_base_pct REAL,
                slugging_pct REAL,
                ops REAL,
                pitching_wins INTEGER,
                pitching_losses INTEGER,
                pitching_era REAL,
                pitching_so INTEGER,
                FOREIGN KEY (legend_id) REFERENCES legends(id)
            )
        ''')

        # Awards and Honors table (表彰・受賞歴)
        await cursor.execute('''
            CREATE TABLE IF NOT EXISTS awards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                legend_id INTEGER,
                award_name TEXT NOT NULL,
                year INTEGER,
                category TEXT,  -- mvp, cy_young, gold_glove, silver_slugger, etc.
                details TEXT,
                FOREIGN KEY (legend_id) REFERENCES legends(id)
            )
        ''')

        # Legendary Episodes table (伝説的エピソード)
        await cursor.execute('''
            CREATE TABLE IF NOT EXISTS episodes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                legend_id INTEGER,
                episode_date DATE,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                category TEXT,  -- record_breaking, dramatic_performance, unique_achievement
                impact TEXT,
                quotes TEXT,
                media_url TEXT,
                FOREIGN KEY (legend_id) REFERENCES legends(id)
            )
        ''')

        # Season Statistics table (シーズン成績)
        await cursor.execute('''
            CREATE TABLE IF NOT EXISTS season_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                legend_id INTEGER,
                season INTEGER NOT NULL,
                team TEXT,
                games INTEGER,
                at_bats INTEGER,
                runs INTEGER,
                hits INTEGER,
                home_runs INTEGER,
                rbis INTEGER,
                stolen_bases INTEGER,
                batting_avg REAL,
                pitching_wins INTEGER,
                pitching_losses INTEGER,
                pitching_era REAL,
                notes TEXT,
                FOREIGN KEY (legend_id) REFERENCES legends(id)
            )
        ''')

        await conn.commit()
        await conn.close()

    # Legends Operations
    async def add_legend(self, player_name: str, primary_position: str,
                        birth_date: str = None, death_date: str = None,
                        birthplace: str = None, debut_year: int = None,
                        retirement_year: int = None, teams: str = None,
                        hall_of_fame: bool = False, hall_of_fame_year: int = None,
                        biography: str = None, nickname: str = None,
                        height_cm: int = None, weight_kg: int = None,
                        bats: str = None, throws: str = None) -> int:
        """Add a legendary player"""
        conn = await self.get_connection()
        cursor = await conn.cursor()
        await cursor.execute('''
            INSERT INTO legends
            (player_name, birth_date, death_date, birthplace, debut_year, retirement_year,
             primary_position, teams, hall_of_fame, hall_of_fame_year, biography,
             nickname, height_cm, weight_kg, bats, throws)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (player_name, birth_date, death_date, birthplace, debut_year, retirement_year,
              primary_position, teams, hall_of_fame, hall_of_fame_year, biography,
              nickname, height_cm, weight_kg, bats, throws))
        legend_id = cursor.lastrowid
        await conn.commit()
        await conn.close()
        return legend_id

    async def get_legends(self, hall_of_fame: bool = None, position: str = None,
                         limit: int = 20) -> List[Dict]:
        """Get legendary players with optional filters"""
        conn = await self.get_connection()
        cursor = await conn.cursor()

        query = 'SELECT * FROM legends WHERE 1=1'
        params = []

        if hall_of_fame is not None:
            query += ' AND hall_of_fame = ?'
            params.append(1 if hall_of_fame else 0)
        if position:
            query += ' AND primary_position = ?'
            params.append(position)

        query += ' ORDER BY player_name ASC LIMIT ?'
        params.append(limit)

        await cursor.execute(query, params)
        rows = await cursor.fetchall()
        await conn.close()

        columns = [description[0] for description in cursor.description]
        return [dict(zip(columns, row)) for row in rows]

    async def get_legend(self, legend_id: int) -> Optional[Dict]:
        """Get a specific legend by ID"""
        conn = await self.get_connection()
        cursor = await conn.cursor()
        await cursor.execute('SELECT * FROM legends WHERE id = ?', (legend_id,))
        row = await cursor.fetchone()
        await conn.close()

        if row:
            columns = [description[0] for description in cursor.description]
            return dict(zip(columns, row))
        return None

    async def search_legends(self, query: str, limit: int = 10) -> List[Dict]:
        """Search legends by name or nickname"""
        conn = await self.get_connection()
        cursor = await conn.cursor()
        await cursor.execute('''
            SELECT * FROM legends
            WHERE player_name LIKE ? OR nickname LIKE ?
            ORDER BY player_name ASC
            LIMIT ?
        ''', (f'%{query}%', f'%{query}%', limit))
        rows = await cursor.fetchall()
        await conn.close()

        columns = [description[0] for description in cursor.description]
        return [dict(zip(columns, row)) for row in rows]

    # Career Statistics Operations
    async def add_career_stats(self, legend_id: int, league: str = None,
                             games: int = None, at_bats: int = None, runs: int = None,
                             hits: int = None, doubles: int = None, triples: int = None,
                             home_runs: int = None, rbis: int = None,
                             stolen_bases: int = None, batting_avg: float = None,
                             on_base_pct: float = None, slugging_pct: float = None,
                             ops: float = None, pitching_wins: int = None,
                             pitching_losses: int = None, pitching_era: float = None,
                             pitching_so: int = None) -> int:
        """Add career statistics for a legend"""
        conn = await self.get_connection()
        cursor = await conn.cursor()
        await cursor.execute('''
            INSERT INTO career_stats
            (legend_id, league, games, at_bats, runs, hits, doubles, triples, home_runs,
             rbis, stolen_bases, batting_avg, on_base_pct, slugging_pct, ops,
             pitching_wins, pitching_losses, pitching_era, pitching_so)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (legend_id, league, games, at_bats, runs, hits, doubles, triples,
              home_runs, rbis, stolen_bases, batting_avg, on_base_pct, slugging_pct,
              ops, pitching_wins, pitching_losses, pitching_era, pitching_so))
        stats_id = cursor.lastrowid
        await conn.commit()
        await conn.close()
        return stats_id

    async def get_career_stats(self, legend_id: int) -> Optional[Dict]:
        """Get career statistics for a legend"""
        conn = await self.get_connection()
        cursor = await conn.cursor()
        await cursor.execute('SELECT * FROM career_stats WHERE legend_id = ?', (legend_id,))
        row = await cursor.fetchone()
        await conn.close()

        if row:
            columns = [description[0] for description in cursor.description]
            return dict(zip(columns, row))
        return None

    # Awards Operations
    async def add_award(self, legend_id: int, award_name: str, year: int = None,
                       category: str = None, details: str = None) -> int:
        """Add an award/honor for a legend"""
        conn = await self.get_connection()
        cursor = await conn.cursor()
        await cursor.execute('''
            INSERT INTO awards (legend_id, award_name, year, category, details)
            VALUES (?, ?, ?, ?, ?)
        ''', (legend_id, award_name, year, category, details))
        award_id = cursor.lastrowid
        await conn.commit()
        await conn.close()
        return award_id

    async def get_awards(self, legend_id: int) -> List[Dict]:
        """Get all awards for a legend"""
        conn = await self.get_connection()
        cursor = await conn.cursor()
        await cursor.execute('''
            SELECT * FROM awards WHERE legend_id = ? ORDER BY year DESC
        ''', (legend_id,))
        rows = await cursor.fetchall()
        await conn.close()

        columns = [description[0] for description in cursor.description]
        return [dict(zip(columns, row)) for row in rows]

    # Episodes Operations
    async def add_episode(self, legend_id: int, title: str, description: str,
                         episode_date: str = None, category: str = None,
                         impact: str = None, quotes: str = None,
                         media_url: str = None) -> int:
        """Add a legendary episode"""
        conn = await self.get_connection()
        cursor = await conn.cursor()
        await cursor.execute('''
            INSERT INTO episodes
            (legend_id, episode_date, title, description, category, impact, quotes, media_url)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (legend_id, episode_date, title, description, category, impact, quotes, media_url))
        episode_id = cursor.lastrowid
        await conn.commit()
        await conn.close()
        return episode_id

    async def get_episodes(self, legend_id: int) -> List[Dict]:
        """Get all legendary episodes for a legend"""
        conn = await self.get_connection()
        cursor = await conn.cursor()
        await cursor.execute('''
            SELECT * FROM episodes WHERE legend_id = ? ORDER BY episode_date DESC
        ''', (legend_id,))
        rows = await cursor.fetchall()
        await conn.close()

        columns = [description[0] for description in cursor.description]
        return [dict(zip(columns, row)) for row in rows]

    # Season Statistics Operations
    async def add_season_stats(self, legend_id: int, season: int, team: str = None,
                              games: int = None, at_bats: int = None, runs: int = None,
                              hits: int = None, home_runs: int = None, rbis: int = None,
                              stolen_bases: int = None, batting_avg: float = None,
                              pitching_wins: int = None, pitching_losses: int = None,
                              pitching_era: float = None, notes: str = None) -> int:
        """Add season statistics for a legend"""
        conn = await self.get_connection()
        cursor = await conn.cursor()
        await cursor.execute('''
            INSERT INTO season_stats
            (legend_id, season, team, games, at_bats, runs, hits, home_runs,
             rbis, stolen_bases, batting_avg, pitching_wins, pitching_losses,
             pitching_era, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (legend_id, season, team, games, at_bats, runs, hits, home_runs,
              rbis, stolen_bases, batting_avg, pitching_wins, pitching_losses,
              pitching_era, notes))
        stats_id = cursor.lastrowid
        await conn.commit()
        await conn.close()
        return stats_id

    async def get_season_stats(self, legend_id: int) -> List[Dict]:
        """Get all season statistics for a legend"""
        conn = await self.get_connection()
        cursor = await conn.cursor()
        await cursor.execute('''
            SELECT * FROM season_stats WHERE legend_id = ? ORDER BY season DESC
        ''', (legend_id,))
        rows = await cursor.fetchall()
        await conn.close()

        columns = [description[0] for description in cursor.description]
        return [dict(zip(columns, row)) for row in rows]

    async def compare_legends(self, legend_id1: int, legend_id2: int) -> Dict:
        """Compare two legends' career statistics"""
        conn = await self.get_connection()
        cursor = await conn.cursor()

        await cursor.execute('''
            SELECT l.*, c.*
            FROM legends l
            LEFT JOIN career_stats c ON l.id = c.legend_id
            WHERE l.id IN (?, ?)
        ''', (legend_id1, legend_id2))

        rows = await cursor.fetchall()
        await conn.close()

        columns = [description[0] for description in cursor.description]
        results = [dict(zip(columns, row)) for row in rows]

        if len(results) == 2:
            return {
                'legend1': results[0],
                'legend2': results[1]
            }
        return None

    async def get_summary(self) -> Dict:
        """Get database summary"""
        conn = await self.get_connection()
        cursor = await conn.cursor()

        await cursor.execute("SELECT COUNT(*) FROM legends")
        total_legends = (await cursor.fetchone())[0]

        await cursor.execute("SELECT COUNT(*) FROM legends WHERE hall_of_fame = 1")
        hall_of_fame_legends = (await cursor.fetchone())[0]

        await cursor.execute("SELECT COUNT(*) FROM awards")
        total_awards = (await cursor.fetchone())[0]

        await cursor.execute("SELECT COUNT(*) FROM episodes")
        total_episodes = (await cursor.fetchone())[0]

        await conn.close()

        return {
            'total_legends': total_legends,
            'hall_of_fame_legends': hall_of_fame_legends,
            'total_awards': total_awards,
            'total_episodes': total_episodes
        }


if __name__ == '__main__':
    import asyncio
    async def test():
        db = BaseballLegendProfileDB()
        await db.init_db()
        print("Database initialized successfully!")
        summary = await db.get_summary()
        print("\nSummary:", summary)

    asyncio.run(test())
