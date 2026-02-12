#!/usr/bin/env python3
"""
Audio Summarizer Database
音声要約エージェントのデータベース管理
"""

import sqlite3
from pathlib import Path
from datetime import datetime

class AudioSummarizerDB:
    """音声要約データベース"""

    def __init__(self, db_path=None):
        if db_path is None:
            db_path = Path(__file__).parent / "audio_summarizer.db"
        self.db_path = Path(db_path)
        self.init_db()

    def init_db(self):
        """データベース初期化"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS summaries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            audio_file TEXT NOT NULL,
            transcription TEXT,
            summary TEXT,
            key_points TEXT,
            sent_to_slack BOOLEAN DEFAULT 0,
            slack_timestamp TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        conn.commit()
        conn.close()

    def add_summary(self, audio_file, transcription, summary, key_points, slack_timestamp=None):
        """要約を追加"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO summaries (audio_file, transcription, summary, key_points, slack_timestamp)
        VALUES (?, ?, ?, ?, ?)
        """, (audio_file, transcription, summary, key_points, slack_timestamp))

        summary_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return summary_id

    def get_summary(self, summary_id):
        """要約を取得"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM summaries WHERE id = ?", (summary_id,))
        row = cursor.fetchone()

        conn.close()

        if row:
            return {
                'id': row[0],
                'audio_file': row[1],
                'transcription': row[2],
                'summary': row[3],
                'key_points': row[4],
                'sent_to_slack': bool(row[5]),
                'slack_timestamp': row[6],
                'created_at': row[7]
            }
        return None

    def get_all_summaries(self):
        """全要約を取得"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM summaries ORDER BY created_at DESC")
        rows = cursor.fetchall()

        conn.close()

        return [{
            'id': r[0],
            'audio_file': r[1],
            'transcription': r[2],
            'summary': r[3],
            'key_points': r[4],
            'sent_to_slack': bool(r[5]),
            'slack_timestamp': r[6],
            'created_at': r[7]
        } for r in rows]

    def delete_summary(self, summary_id):
        """要約を削除"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("DELETE FROM summaries WHERE id = ?", (summary_id,))

        conn.commit()
        conn.close()

if __name__ == '__main__':
    db = AudioSummarizerDB()
    print("Audio Summarizer Database initialized.")
