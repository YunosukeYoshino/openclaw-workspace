#!/usr/bin/env python3
"""
マルチモーダル音声合成エージェント - データベースモジュール
"""

import sqlite3
import os
from typing import List, Dict, Any, Optional
from datetime import datetime

class MultimodalTextToSpeechAgentDB:
    """マルチモーダル音声合成エージェント データベース管理クラス"""

    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            db_path = os.path.join(os.path.dirname(__file__), 'multimodal-text-to-speech-agent.db')
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """データベース初期化"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("tts_generations (id INTEGER PRIMARY KEY, text TEXT, voice_id TEXT, emotion TEXT, audio_path TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
        conn.commit()
        conn.close()

    def add_entry(self, content_type: str, media_path: str, analysis_result: str,
                  confidence: float, tags: List[str]) -> int:
        """新しいエントリーを追加"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO tts_generations (content_type, media_path, analysis_result, confidence, tags) VALUES (?, ?, ?, ?, ?)",
            (content_type, media_path, analysis_result, confidence, ','.join(tags))
        )
        entry_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return entry_id

    def get_entry(self, entry_id: int) -> Optional[Dict[str, Any]]:
        """エントリーを取得"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tts_generations WHERE id = ?", (entry_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return dict(
                id=row[0],
                content_type=row[1],
                media_path=row[2],
                analysis_result=row[3],
                confidence=row[4],
                tags=row[5].split(',') if row[5] else [],
                created_at=row[6]
            )
        return None

    def list_entries(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """エントリー一覧を取得"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tts_generations ORDER BY created_at DESC LIMIT ? OFFSET ?", (limit, offset))
        rows = cursor.fetchall()
        conn.close()
        return [dict(
            id=row[0],
            content_type=row[1],
            media_path=row[2],
            analysis_result=row[3],
            confidence=row[4],
            tags=row[5].split(',') if row[5] else [],
            created_at=row[6]
        ) for row in rows]

    def search_by_tag(self, search_tag: str) -> List[Dict[str, Any]]:
        """タグで検索"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tts_generations WHERE tags LIKE ?", (f'%{search_tag}%',))
        rows = cursor.fetchall()
        conn.close()
        result = []
        for row in rows:
            result.append(dict(
                id=row[0],
                content_type=row[1],
                media_path=row[2],
                analysis_result=row[3],
                confidence=row[4],
                tags=row[5].split(',') if row[5] else [],
                created_at=row[6]
            ))
        return result

    def delete_entry(self, entry_id: int) -> bool:
        """エントリーを削除"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tts_generations WHERE id = ?", (entry_id,))
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return success

    def get_stats(self) -> Dict[str, Any]:
        """統計情報を取得"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM tts_generations")
        total = cursor.fetchone()[0]
        cursor.execute("SELECT content_type, COUNT(*) FROM tts_generations GROUP BY content_type")
        by_type = dict()
        for row in cursor.fetchall():
            by_type[row[0]] = row[1]
        conn.close()
        return dict(total=total, by_type=by_type)
