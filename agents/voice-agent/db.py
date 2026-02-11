#!/usr/bin/env python3
"""
Voice Assistant Agent
- Speech recognition
- Text-to-speech synthesis
- Voice command management
"""

import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / "voice.db"

def init_db():
    """Initialize database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Voice commands table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS voice_commands (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        command_name TEXT NOT NULL,
        command_pattern TEXT NOT NULL,
        action_type TEXT NOT NULL,
        action_params TEXT,
        description TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        usage_count INTEGER DEFAULT 0,
        active BOOLEAN DEFAULT 1
    )
    ''')

    # Voice history table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS voice_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        transcription TEXT NOT NULL,
        recognized_command_id INTEGER,
        action_executed TEXT,
        success BOOLEAN,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (recognized_command_id) REFERENCES voice_commands(id)
    )
    ''')

    # TTS history table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tts_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        text TEXT NOT NULL,
        voice_id TEXT,
        duration REAL,
        file_path TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Voice settings table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS voice_settings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        recognition_language TEXT DEFAULT 'ja-JP',
        tts_voice_id TEXT,
        tts_speed REAL DEFAULT 1.0,
        tts_pitch REAL DEFAULT 1.0,
        auto_response BOOLEAN DEFAULT 1,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(user_id)
    )
    ''')

    # Custom vocabulary table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS custom_vocabulary (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        word TEXT NOT NULL,
        pronunciation TEXT,
        category TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(word)
    )
    ''')

    # Indexes
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_voice_commands_pattern ON voice_commands(command_pattern)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_voice_commands_active ON voice_commands(active)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_voice_history_timestamp ON voice_history(timestamp)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_custom_vocab_category ON custom_vocabulary(category)')

    conn.commit()
    conn.close()
    print("✅ Database initialized")

def add_voice_command(name, pattern, action_type, action_params=None, description=None):
    """Add voice command"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO voice_commands (command_name, command_pattern, action_type, action_params, description)
    VALUES (?, ?, ?, ?, ?)
    ''', (name, pattern, action_type, action_params, description))

    command_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return command_id

def get_voice_command(pattern):
    """Find voice command by pattern"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT * FROM voice_commands
    WHERE active = 1 AND ? LIKE command_pattern
    ORDER BY LENGTH(command_pattern) DESC
    LIMIT 1
    ''', (pattern,))

    command = cursor.fetchone()
    conn.close()
    return command

def list_voice_commands(active_only=True):
    """List voice commands"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    if active_only:
        cursor.execute('SELECT * FROM voice_commands WHERE active = 1 ORDER BY command_name')
    else:
        cursor.execute('SELECT * FROM voice_commands ORDER BY command_name')

    commands = cursor.fetchall()
    conn.close()
    return commands

def update_voice_command(command_id, **kwargs):
    """Update voice command"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    updates = []
    values = []
    for key, value in kwargs.items():
        if value is not None:
            updates.append(f"{key} = ?")
            values.append(value)
    values.append(command_id)

    if updates:
        cursor.execute(f'''
        UPDATE voice_commands
        SET {', '.join(updates)}
        WHERE id = ?
        ''', values)
        conn.commit()

    conn.close()

def delete_voice_command(command_id):
    """Delete voice command (soft delete)"""
    update_voice_command(command_id, active=0)

def add_voice_history(transcription, recognized_command_id=None, action_executed=None, success=None):
    """Add voice interaction history"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO voice_history (transcription, recognized_command_id, action_executed, success)
    VALUES (?, ?, ?, ?)
    ''', (transcription, recognized_command_id, action_executed, success))

    # Update command usage count
    if recognized_command_id:
        cursor.execute('''
        UPDATE voice_commands
        SET usage_count = usage_count + 1
        WHERE id = ?
        ''', (recognized_command_id,))

    history_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return history_id

def get_voice_history(limit=20):
    """Get voice interaction history"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT vh.*, vc.command_name
    FROM voice_history vh
    LEFT JOIN voice_commands vc ON vh.recognized_command_id = vc.id
    ORDER BY vh.timestamp DESC
    LIMIT ?
    ''', (limit,))

    history = cursor.fetchall()
    conn.close()
    return history

def add_tts_history(text, voice_id=None, duration=None, file_path=None):
    """Add TTS history"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO tts_history (text, voice_id, duration, file_path)
    VALUES (?, ?, ?, ?)
    ''', (text, voice_id, duration, file_path))

    tts_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return tts_id

def get_tts_history(limit=20):
    """Get TTS history"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT * FROM tts_history
    ORDER BY created_at DESC
    LIMIT ?
    ''', (limit,))

    history = cursor.fetchall()
    conn.close()
    return history

def set_voice_setting(user_id, recognition_language=None, tts_voice_id=None,
                     tts_speed=None, tts_pitch=None, auto_response=None):
    """Set voice settings for user"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT OR REPLACE INTO voice_settings
    (user_id, recognition_language, tts_voice_id, tts_speed, tts_pitch, auto_response, updated_at)
    VALUES (?, COALESCE(?, (SELECT recognition_language FROM voice_settings WHERE user_id = ?)),
            COALESCE(?, (SELECT tts_voice_id FROM voice_settings WHERE user_id = ?)),
            COALESCE(?, (SELECT tts_speed FROM voice_settings WHERE user_id = ?)),
            COALESCE(?, (SELECT tts_pitch FROM voice_settings WHERE user_id = ?)),
            COALESCE(?, (SELECT auto_response FROM voice_settings WHERE user_id = ?)), ?)
    ''', (user_id, recognition_language, user_id, tts_voice_id, user_id, tts_speed, user_id,
          tts_pitch, user_id, auto_response, user_id, datetime.now()))

    conn.commit()
    conn.close()

def get_voice_setting(user_id):
    """Get voice settings for user"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM voice_settings WHERE user_id = ?', (user_id,))
    settings = cursor.fetchone()
    conn.close()
    return settings

def add_custom_vocabulary(word, pronunciation=None, category=None):
    """Add custom vocabulary word"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute('''
        INSERT INTO custom_vocabulary (word, pronunciation, category)
        VALUES (?, ?, ?)
        ''', (word, pronunciation, category))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        conn.close()
        return False

def get_custom_vocabulary(category=None):
    """Get custom vocabulary"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    if category:
        cursor.execute('SELECT * FROM custom_vocabulary WHERE category = ? ORDER BY word', (category,))
    else:
        cursor.execute('SELECT * FROM custom_vocabulary ORDER BY word')

    vocab = cursor.fetchall()
    conn.close()
    return vocab

def get_stats():
    """Get voice statistics"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    stats = {}

    # Total voice interactions
    cursor.execute('SELECT COUNT(*) FROM voice_history')
    stats['total_interactions'] = cursor.fetchone()[0]

    # Successful interactions
    cursor.execute("SELECT COUNT(*) FROM voice_history WHERE success = 1")
    stats['successful_interactions'] = cursor.fetchone()[0]

    # Active commands
    cursor.execute('SELECT COUNT(*) FROM voice_commands WHERE active = 1')
    stats['active_commands'] = cursor.fetchone()[0]

    # Most used commands
    cursor.execute('''
    SELECT command_name, usage_count
    FROM voice_commands
    WHERE active = 1
    ORDER BY usage_count DESC
    LIMIT 5
    ''')
    stats['most_used_commands'] = cursor.fetchall()

    # TTS count
    cursor.execute('SELECT COUNT(*) FROM tts_history')
    stats['tts_count'] = cursor.fetchone()[0]

    # Custom vocabulary count
    cursor.execute('SELECT COUNT(*) FROM custom_vocabulary')
    stats['vocab_count'] = cursor.fetchone()[0]

    # Recent interactions (last 24 hours)
    cursor.execute('''
    SELECT COUNT(*) FROM voice_history
    WHERE timestamp >= datetime('now', '-24 hours')
    ''')
    stats['recent_interactions'] = cursor.fetchone()[0]

    conn.close()
    return stats

if __name__ == '__main__':
    init_db()
