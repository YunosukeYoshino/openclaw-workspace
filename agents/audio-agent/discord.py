#!/usr/bin/env python3
"""
Audio Agent #1 - Discord Integration
"""

import re
from db import *

def parse_message(message):
    """Parse message"""
    # Add audio
    add_match = re.match(r'(?:追加|add)[:：]\s*(.+)', message, re.IGNORECASE)
    if add_match:
        return parse_add(add_match.group(1))

    # Update audio
    update_match = re.match(r'(?:更新|update)[:：]\s*(\d+)\s*[,，]\s*(.+)', message, re.IGNORECASE)
    if update_match:
        return {'action': 'update', 'audio_id': int(update_match.group(1)), 'content': update_match.group(2)}

    # Delete audio
    delete_match = re.match(r'(?:削除|delete)[:：]\s*(\d+)', message, re.IGNORECASE)
    if delete_match:
        return {'action': 'delete', 'audio_id': int(delete_match.group(1))}

    # List audio
    list_match = re.match(r'(?:一覧|list|audio)(?:[:：]\s*(.+))?', message, re.IGNORECASE)
    if list_match:
        category = list_match.group(1).strip() if list_match.group(1) else None
        return {'action': 'list', 'category': category}

    # Search audio
    search_match = re.match(r'(?:検索|search)[:：]\s*(.+)', message, re.IGNORECASE)
    if search_match:
        return {'action': 'search', 'query': search_match.group(1)}

    # Create playlist
    playlist_match = re.match(r'(?:プレイリスト|playlist)[:：]\s*作成|create\s+(.+)', message, re.IGNORECASE)
    if playlist_match:
        return parse_playlist(playlist_match.group(1) if playlist_match.lastindex else "")

    # Add to playlist
    add_to_match = re.match(r'(?:プレイリスト|playlist)[:：]\s*(\d+)\s*[,，]\s*追加|add\s+\d+\s*,\s*(\d+)', message, re.IGNORECASE)
    if add_to_match:
        return {'action': 'add_to_playlist', 'playlist_id': int(add_to_match.group(1)), 'audio_id': int(add_to_match.group(2))}

    # List playlists
    if re.match(r'プレイリスト一覧|playlists|list playlists', message, re.IGNORECASE):
        return {'action': 'list_playlists'}

    # Recording
    record_match = re.match(r'(?:録音|record)[:：]\s*(.+)', message, re.IGNORECASE)
    if record_match:
        return parse_recording(record_match.group(1))

    # Recordings list
    if re.match(r'録音一覧|recordings|list recordings', message, re.IGNORECASE):
        return {'action': 'list_recordings'}

    # Stats
    if message.strip() in ['統計', 'stats']:
        return {'action': 'stats'}

    return None

def parse_add(content):
    """Parse add content"""
    result = {'action': 'add', 'title': None, 'file_path': None, 'duration': None, 'format': None,
              'bitrate': None, 'category': None, 'tags': None, 'description': None}

    result['title'] = content.split(',')[0].strip()

    file_match = re.search(r'ファイル|file[:：]\s*(.+?)(?:[、,]|$)', content)
    if file_match:
        result['file_path'] = file_match.group(1).strip()

    format_match = re.search(r'形式|format[:：]\s*(\w+)', content)
    if format_match:
        result['format'] = format_match.group(1).lower()

    duration_match = re.search(r'長さ|duration[:：]\s*([\d.]+)', content)
    if duration_match:
        result['duration'] = float(duration_match.group(1))

    category_match = re.search(r'カテゴリ|category[:：]\s*(.+?)(?:[、,]|$)', content)
    if category_match:
        result['category'] = category_match.group(1).strip()

    tags_match = re.search(r'タグ|tags[:：]\s*(.+)', content)
    if tags_match:
        result['tags'] = tags_match.group(1).strip()

    desc_match = re.search(r'説明|description[:：]\s*(.+)', content)
    if desc_match:
        result['description'] = desc_match.group(1).strip()

    return result

def parse_playlist(content):
    """Parse playlist content"""
    result = {'action': 'create_playlist', 'name': None, 'description': None}

    result['name'] = content.split(',')[0].strip()

    desc_match = re.search(r'説明|description[:：]\s*(.+)', content)
    if desc_match:
        result['description'] = desc_match.group(1).strip()

    return result

def parse_recording(content):
    """Parse recording content"""
    result = {'action': 'add_recording', 'title': None, 'file_path': None, 'duration': None, 'format': None, 'notes': None}

    parts = content.split(',')
    result['title'] = parts[0].strip()

    file_match = re.search(r'ファイル|file[:：]\s*(.+?)(?:[、,]|$)', content)
    if file_match:
        result['file_path'] = file_match.group(1).strip()

    duration_match = re.search(r'長さ|duration[:：]\s*([\d.]+)', content)
    if duration_match:
        result['duration'] = float(duration_match.group(1))

    format_match = re.search(r'形式|format[:：]\s*(\w+)', content)
    if format_match:
        result['format'] = format_match.group(1).lower()

    notes_match = re.search(r'メモ|notes[:：]\s*(.+)', content)
    if notes_match:
        result['notes'] = notes_match.group(1).strip()

    return result

def handle_message(message):
    """Handle message"""
    parsed = parse_message(message)

    if not parsed:
        return None

    action = parsed['action']

    if action == 'add':
        if not parsed['title']:
            return "❌ タイトルを入力してください / Please enter a title"

        audio_id = add_audio(
            parsed['title'],
            parsed['file_path'],
            parsed['duration'],
            parsed['format'],
            parsed.get('bitrate'),
            parsed['category'],
            parsed['tags'],
            parsed['description']
        )

        response = f"✅ 音楽を追加しました / Audio added #{audio_id}\n"
        response += f"タイトル: {parsed['title']}\n"
        if parsed['category']:
            response += f"カテゴリ: {parsed['category']}"

        return response

    elif action == 'update':
        audio_id = parsed['audio_id']
        # Parse update content
        updates = {}
        content = parsed['content']

        title_match = re.search(r'タイトル|title[:：]\s*(.+?)(?:[、,]|$)', content)
        if title_match:
            updates['title'] = title_match.group(1).strip()

        category_match = re.search(r'カテゴリ|category[:：]\s*(.+?)(?:[、,]|$)', content)
        if category_match:
            updates['category'] = category_match.group(1).strip()

        tags_match = re.search(r'タグ|tags[:：]\s*(.+)', content)
        if tags_match:
            updates['tags'] = tags_match.group(1).strip()

        desc_match = re.search(r'説明|description[:：]\s*(.+)', content)
        if desc_match:
            updates['description'] = desc_match.group(1).strip()

        if updates:
            update_audio(audio_id, **updates)
            return f"✅ 音楽 #{audio_id} を更新しました / Audio #{audio_id} updated"
        else:
            return "❌ 更新内容を入力してください / Please enter update content"

    elif action == 'delete':
        delete_audio(parsed['audio_id'])
        return f"✅ 音楽 #{parsed['audio_id']} を削除しました / Audio #{parsed['audio_id']} deleted"

    elif action == 'list':
        audio_list = list_audio(category=parsed['category'])

        if not audio_list:
            return f"🎵 音楽がありません / No audio files found"

        category_text = f" ({parsed['category']})" if parsed['category'] else ""
        response = f"🎵 音楽一覧{category_text} ({len(audio_list)}件):\n"
        for audio in audio_list:
            response += format_audio(audio)

        return response

    elif action == 'search':
        results = search_audio(parsed['query'])

        if not results:
            return f"🔍 検索結果がありません / No results found for '{parsed['query']}'"

        response = f"🔍 検索結果: '{parsed['query']}' ({len(results)}件):\n"
        for audio in results:
            response += format_audio(audio)

        return response

    elif action == 'create_playlist':
        if not parsed['name']:
            return "❌ プレイリスト名を入力してください / Please enter playlist name"

        playlist_id = create_playlist(parsed['name'], parsed['description'])
        return f"✅ プレイリスト #{playlist_id} '{parsed['name']}' を作成しました / Playlist #{playlist_id} created"

    elif action == 'add_to_playlist':
        add_to_playlist(parsed['playlist_id'], parsed['audio_id'])
        return f"✅ プレイリスト #{parsed['playlist_id']} に音楽 #{parsed['audio_id']} を追加しました / Added audio to playlist"

    elif action == 'list_playlists':
        playlists = list_playlists()

        if not playlists:
            return "📋 プレイリストがありません / No playlists found"

        response = f"📋 プレイリスト一覧 ({len(playlists)}件):\n"
        for pl in playlists:
            response += format_playlist(pl)

        return response

    elif action == 'add_recording':
        if not parsed['title'] or not parsed['file_path']:
            return "❌ タイトルとファイルパスを入力してください / Please enter title and file path"

        recording_id = add_recording(
            parsed['title'],
            parsed['file_path'],
            parsed['duration'],
            parsed['format'],
            parsed['notes']
        )

        return f"✅ 録音 #{recording_id} '{parsed['title']}' を追加しました / Recording #{recording_id} added"

    elif action == 'list_recordings':
        recordings = list_recordings()

        if not recordings:
            return "🎙️ 録音がありません / No recordings found"

        response = f"🎙️ 録音一覧 ({len(recordings)}件):\n"
        for rec in recordings:
            response += format_recording(rec)

        return response

    elif action == 'stats':
        stats = get_stats()

        response = "📊 音楽統計 / Audio Stats:\n"
        response += f"総数: {stats['total_audio']}件\n"
        response += f"プレイリスト: {stats['total_playlists']}個\n"
        response += f"録音: {stats['total_recordings']}件\n"
        response += f"MP3: {stats['mp3_count']}件\n"
        response += f"WAV: {stats['wav_count']}件\n"
        response += f"総時間: {stats['total_duration']}秒"

        return response

    return None

def format_audio(audio):
    """Format audio"""
    id, title, file_path, duration, format, bitrate, category, tags, description, created_at = audio

    response = f"\n🎵 [{id}] {title}\n"
    if duration:
        response += f"    長さ: {duration}秒\n"
    if format:
        response += f"    形式: {format.upper()}\n"
    if category:
        response += f"    カテゴリ: {category}\n"

    return response

def format_playlist(pl):
    """Format playlist"""
    id, name, description, created_at = pl

    response = f"\n📋 [{id}] {name}\n"
    if description:
        response += f"    {description}\n"

    return response

def format_recording(rec):
    """Format recording"""
    id, title, file_path, duration, format, recorded_at, notes = rec

    response = f"\n🎙️ [{id}] {title}\n"
    if duration:
        response += f"    長さ: {duration}秒\n"
    if format:
        response += f"    形式: {format.upper()}\n"
    if notes:
        response += f"    メモ: {notes}\n"

    return response

if __name__ == '__main__':
    init_db()
