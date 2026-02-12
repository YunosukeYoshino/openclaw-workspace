#!/usr/bin/env python3
"""
音楽エージェント #31 - Discord連携
"""

import re
from db import *

def parse_message(message):
    """メッセージを解析"""
    # 曲追加
    song_match = re.match(r'(?:曲|song|music)[:：]\s*(.+)', message, re.IGNORECASE)
    if song_match:
        return parse_add_song(song_match.group(1))

    # 曲更新
    update_match = re.match(r'(?:曲更新|update song|music update)[:：]\s*(\d+)\s*(.+)', message, re.IGNORECASE)
    if update_match:
        return {'action': 'update_song', 'song_id': int(update_match.group(1)), 'content': update_match.group(2)}

    # 曲削除
    delete_match = re.match(r'(?:曲削除|delete song|remove song)[:：]\s*(\d+)', message, re.IGNORECASE)
    if delete_match:
        return {'action': 'delete_song', 'song_id': int(delete_match.group(1))}

    # プレイリスト追加
    playlist_match = re.match(r'(?:プレイリスト|playlist)[:：]\s*(.+)', message, re.IGNORECASE)
    if playlist_match:
        return parse_add_playlist(playlist_match.group(1))

    # プレイリストに曲追加
    add_match = re.match(r'(?:追加|add)[:：]\s*(\d+)\s*曲\s*(\d+)', message, re.IGNORECASE)
    if add_match:
        return {'action': 'add_to_playlist', 'playlist_id': int(add_match.group(1)), 'song_id': int(add_match.group(2))}

    # プレイリストから曲削除
    remove_match = re.match(r'(?:削除|remove)[:：]\s*(\d+)\s*曲\s*(\d+)', message, re.IGNORECASE)
    if remove_match:
        return {'action': 'remove_from_playlist', 'playlist_id': int(remove_match.group(1)), 'song_id': int(remove_match.group(2))}

    # プレイリスト表示
    show_match = re.match(r'(?:プレイリスト|playlist)[：:]\s*(\d+)', message, re.IGNORECASE)
    if show_match:
        return {'action': 'show_playlist', 'playlist_id': int(show_match.group(1))}

    # 検索
    search_match = re.match(r'(?:検索|search)[:：]\s*(.+)', message, re.IGNORECASE)
    if search_match:
        return {'action': 'search', 'keyword': search_match.group(1)}

    # 曲一覧
    list_match = re.match(r'(?:(?:曲|song|music)(?:一覧|list)|list|songs)', message, re.IGNORECASE)
    if list_match:
        return {'action': 'list_songs'}

    # プレイリスト一覧
    if message.strip() in ['プレイリスト一覧', 'playlists', 'list playlists']:
        return {'action': 'list_playlists'}

    # ジャンル別
    genre_match = re.match(r'(?:ジャンル|genre)[：:]\s*(.+)', message, re.IGNORECASE)
    if genre_match:
        return {'action': 'list_by_genre', 'genre': genre_match.group(1)}

    # アーティスト別
    artist_match = re.match(r'(?:アーティスト|artist)[：:]\s*(.+)', message, re.IGNORECASE)
    if artist_match:
        return {'action': 'list_by_artist', 'artist': artist_match.group(1)}

    # 統計
    if message.strip() in ['統計', 'stats', '音楽統計']:
        return {'action': 'stats'}

    return None

def parse_add_song(content):
    """曲追加を解析"""
    result = {'action': 'add_song', 'title': None, 'artist': None, 'album': None,
              'genre': None, 'year': None, 'rating': None, 'notes': None}

    # タイトル (最初の部分)
    title_match = re.match(r'^([^、,（\(【♪]+)', content)
    if title_match:
        result['title'] = title_match.group(1).strip()

    # アーティスト
    artist_match = re.search(r'(?:アーティスト|artist|歌手|by)[：:]\s*([^、,]+)', content)
    if artist_match:
        result['artist'] = artist_match.group(1).strip()

    # アルバム
    album_match = re.search(r'(?:アルバム|album)[：:]\s*([^、,]+)', content)
    if album_match:
        result['album'] = album_match.group(1).strip()

    # ジャンル
    genre_match = re.search(r'(?:ジャンル|genre)[：:]\s*([^、,]+)', content)
    if genre_match:
        result['genre'] = genre_match.group(1).strip()

    # 年
    year_match = re.search(r'(?:年|year)[：:]\s*(\d{4})', content)
    if year_match:
        result['year'] = int(year_match.group(1))

    # 評価
    rating_match = re.search(r'(?:評価|rating|点数)[：:]\s*(\d)', content)
    if rating_match:
        rating = int(rating_match.group(1))
        if 1 <= rating <= 5:
            result['rating'] = rating

    # メモ
    notes_match = re.search(r'(?:メモ|備考|memo|note)[：:]\s*(.+)', content)
    if notes_match:
        result['notes'] = notes_match.group(1).strip()

    # タイトルがまだない場合、最初の項目より前をタイトルとする
    if not result['title']:
        for key in ['アーティスト', 'artist', '歌手', 'by', 'アルバム', 'album',
                    'ジャンル', 'genre', '年', 'year', '評価', 'rating', '点数',
                    'メモ', '備考', 'memo', 'note']:
            match = re.search(rf'{key}[：:]', content)
            if match:
                result['title'] = content[:match.start()].strip()
                break
        else:
            result['title'] = content.strip()

    return result

def parse_add_playlist(content):
    """プレイリスト追加を解析"""
    result = {'action': 'add_playlist', 'name': None, 'description': None}

    # 名前 (最初の部分)
    name_match = re.match(r'^([^、,（\(]+)', content)
    if name_match:
        result['name'] = name_match.group(1).strip()

    # 説明
    desc_match = re.search(r'(?:説明|description|desc)[：:]\s*(.+)', content)
    if desc_match:
        result['description'] = desc_match.group(1).strip()

    # 名前がまだない場合、説明より前を名前とする
    if not result['name']:
        desc_match = re.search(r'(?:説明|description|desc)[：:]', content)
        if desc_match:
            result['name'] = content[:desc_match.start()].strip()
        else:
            result['name'] = content.strip()

    return result

def parse_update_song(content):
    """曲更新を解析"""
    result = {}

    # タイトル
    title_match = re.search(r'(?:タイトル|title)[：:]\s*([^、,]+)', content)
    if title_match:
        result['title'] = title_match.group(1).strip()

    # アーティスト
    artist_match = re.search(r'(?:アーティスト|artist|歌手|by)[：:]\s*([^、,]+)', content)
    if artist_match:
        result['artist'] = artist_match.group(1).strip()

    # アルバム
    album_match = re.search(r'(?:アルバム|album)[：:]\s*([^、,]+)', content)
    if album_match:
        result['album'] = album_match.group(1).strip()

    # ジャンル
    genre_match = re.search(r'(?:ジャンル|genre)[：:]\s*([^、,]+)', content)
    if genre_match:
        result['genre'] = genre_match.group(1).strip()

    # 年
    year_match = re.search(r'(?:年|year)[：:]\s*(\d{4})', content)
    if year_match:
        result['year'] = int(year_match.group(1))

    # 評価
    rating_match = re.search(r'(?:評価|rating|点数)[：:]\s*(\d)', content)
    if rating_match:
        rating = int(rating_match.group(1))
        if 1 <= rating <= 5:
            result['rating'] = rating

    # メモ
    notes_match = re.search(r'(?:メモ|備考|memo|note)[：:]\s*(.+)', content)
    if notes_match:
        result['notes'] = notes_match.group(1).strip()

    return result

def handle_message(message):
    """メッセージを処理"""
    parsed = parse_message(message)

    if not parsed:
        return None

    action = parsed['action']

    if action == 'add_song':
        if not parsed['title']:
            return "❌ タイトルを入力してください"

        song_id = add_song(
            parsed['title'],
            parsed['artist'],
            parsed['album'],
            parsed['genre'],
            parsed['year'],
            parsed['rating'],
            parsed['notes']
        )

        response = f"🎵 曲 #{song_id} 追加完了\n"
        response += f"タイトル: {parsed['title']}\n"
        if parsed['artist']:
            response += f"アーティスト: {parsed['artist']}\n"
        if parsed['album']:
            response += f"アルバム: {parsed['album']}\n"
        if parsed['genre']:
            response += f"ジャンル: {parsed['genre']}\n"
        if parsed['year']:
            response += f"年: {parsed['year']}\n"
        if parsed['rating']:
            stars = "⭐" * parsed['rating']
            response += f"評価: {stars}\n"
        if parsed['notes']:
            response += f"メモ: {parsed['notes']}"

        return response

    elif action == 'update_song':
        updates = parse_update_song(parsed['content'])

        if not updates:
            return "❌ 更新内容がありません"

        update_song(parsed['song_id'], **updates)

        song = list_songs()
        if song:
            response = f"✅ 曲 #{parsed['song_id']} 更新完了"
            return response
        else:
            return f"❌ 曲 #{parsed['song_id']} が見つかりません"

    elif action == 'delete_song':
        delete_song(parsed['song_id'])
        return f"🗑️ 曲 #{parsed['song_id']} 削除完了"

    elif action == 'add_playlist':
        if not parsed['name']:
            return "❌ プレイリスト名を入力してください"

        playlist_id = add_playlist(parsed['name'], parsed['description'])

        response = f"📋 プレイリスト #{playlist_id} 追加完了\n"
        response += f"名前: {parsed['name']}\n"
        if parsed['description']:
            response += f"説明: {parsed['description']}"

        return response

    elif action == 'add_to_playlist':
        add_song_to_playlist(parsed['playlist_id'], parsed['song_id'])
        return f"🎵 プレイリスト #{parsed['playlist_id']} に曲 #{parsed['song_id']} を追加しました"

    elif action == 'remove_from_playlist':
        remove_song_from_playlist(parsed['playlist_id'], parsed['song_id'])
        return f"🗑️ プレイリスト #{parsed['playlist_id']} から曲 #{parsed['song_id']} を削除しました"

    elif action == 'show_playlist':
        playlist_data = get_playlist(parsed['playlist_id'])

        if not playlist_data['playlist']:
            return f"❌ プレイリスト #{parsed['playlist_id']} が見つかりません"

        response = f"📋 {playlist_data['playlist'][1]}\n"
        if playlist_data['playlist'][2]:
            response += f"{playlist_data['playlist'][2]}\n"
        response += f"\n"

        if not playlist_data['songs']:
            response += "曲がありません"
        else:
            for i, song in enumerate(playlist_data['songs'], 1):
                response += format_song_for_playlist(i, song)

        return response

    elif action == 'search':
        keyword = parsed['keyword']
        songs = search_songs(keyword)

        if not songs:
            return f"🔍 「{keyword}」の検索結果: 見つかりませんでした"

        response = f"🔍 「{keyword}」の検索結果 ({len(songs)}件):\n"
        for song in songs:
            response += format_song(song)

        return response

    elif action == 'list_songs':
        songs = list_songs()

        if not songs:
            return "🎵 曲がありません"

        response = f"🎵 曲一覧 ({len(songs)}件):\n"
        for song in songs:
            response += format_song(song)

        return response

    elif action == 'list_playlists':
        playlists = list_playlists()

        if not playlists:
            return "📋 プレイリストがありません"

        response = f"📋 プレイリスト一覧 ({len(playlists)}件):\n"
        for playlist in playlists:
            response += f"[{playlist[0]}] {playlist[1]} ({playlist[3]}曲)\n"
            if playlist[2]:
                response += f"    {playlist[2]}\n"

        return response

    elif action == 'list_by_genre':
        songs = list_songs(genre=parsed['genre'])

        if not songs:
            return f"🎵 「{parsed['genre']}」の曲がありません"

        response = f"🎵 {parsed['genre']}の曲 ({len(songs)}件):\n"
        for song in songs:
            response += format_song(song)

        return response

    elif action == 'list_by_artist':
        songs = list_songs(artist=parsed['artist'])

        if not songs:
            return f"🎵 「{parsed['artist']}」の曲がありません"

        response = f"🎵 {parsed['artist']}の曲 ({len(songs)}件):\n"
        for song in songs:
            response += format_song(song)

        return response

    elif action == 'stats':
        stats = get_stats()

        response = "📊 音楽統計:\n"
        response += f"全曲数: {stats['total_songs']}曲\n"
        response += f"アーティスト数: {stats['artists']}人\n"
        response += f"ジャンル数: {stats['genres']}種類\n"
        response += f"プレイリスト数: {stats['playlists']}個"
        if stats['avg_rating']:
            response += f"\n平均評価: {stats['avg_rating']}⭐"

        return response

    return None

def format_song(song):
    """曲をフォーマット"""
    id, title, artist, album, genre, year, rating, notes, created_at = song

    response = f"\n[{id}] {title}"
    if artist:
        response += f" - {artist}"
    if rating:
        stars = "⭐" * rating
        response += f" {stars}\n"
    else:
        response += "\n"

    if album:
        response += f"    💿 {album}\n"
    if genre:
        response += f"    🎭 {genre}\n"
    if year:
        response += f"    📅 {year}\n"
    if notes:
        response += f"    📝 {notes}\n"

    return response

def format_song_for_playlist(position, song):
    """プレイイスト用の曲をフォーマット"""
    id, title, artist, album, genre, year, rating, pos = song

    response = f"{position}. "
    if artist:
        response += f"{artist} - "
    response += f"{title}"

    if rating:
        response += f" {'⭐' * rating}"

    response += "\n"

    return response

if __name__ == '__main__':
    # テスト
    init_db()

    test_messages = [
        "曲: Bohemian Rhapsody, アーティスト: Queen, アルバム: A Night at the Opera, 評価: 5",
        "曲: Hotel California, アーティスト: Eagles, ジャンル: Rock",
        "プレイリスト: クラシックロック, 説明: 70年代の名曲集",
        "追加: 1 曲 1",
        "プレイリスト: 1",
        "検索: Queen",
        "統計",
    ]

    for msg in test_messages:
        print(f"\n入力: {msg}")
        result = handle_message(msg)
        if result:
            print(result)
