#!/usr/bin/env python3
"""
ゲームエージェント #32 - Discord連携
"""

import re
from db import *

def parse_message(message):
    """メッセージを解析"""
    # ゲーム追加
    game_match = re.match(r'(?:ゲーム|game)[：:]\s*(.+)', message, re.IGNORECASE)
    if game_match:
        return parse_add(game_match.group(1))

    # 更新
    update_match = re.match(r'(?:更新|update)[：:]\s*(\d+)\s*(.+)', message, re.IGNORECASE)
    if update_match:
        return {'action': 'update', 'game_id': int(update_match.group(1)), 'content': update_match.group(2)}

    # 削除
    delete_match = re.match(r'(?:削除|delete|remove)[：:]\s*(\d+)', message, re.IGNORECASE)
    if delete_match:
        return {'action': 'delete', 'game_id': int(delete_match.group(1))}

    # クリア
    complete_match = re.match(r'(?:クリア|completed|cleared|finish)[：:]\s*(\d+)', message, re.IGNORECASE)
    if complete_match:
        return {'action': 'complete', 'game_id': int(complete_match.group(1))}

    # 中断
    drop_match = re.match(r'(?:中断|dropped|quit)[：:]\s*(\d+)', message, re.IGNORECASE)
    if drop_match:
        return {'action': 'drop', 'game_id': int(drop_match.group(1))}

    # 検索
    search_match = re.match(r'(?:検索|search)[：:]\s*(.+)', message, re.IGNORECASE)
    if search_match:
        return {'action': 'search', 'keyword': search_match.group(1)}

    # 一覧
    list_match = re.match(r'(?:(?:ゲーム|game)(?:一覧|list)|list|games)', message, re.IGNORECASE)
    if list_match:
        return {'action': 'list'}

    # プレイ中
    if message.strip() in ['プレイ中', 'playing', 'プレイ中一覧']:
        return {'action': 'list_playing'}

    # クリア済み
    if message.strip() in ['クリア済み', 'completed', 'クリア一覧']:
        return {'action': 'list_completed'}

    # ウィッシュリスト
    if message.strip() in ['ウィッシュリスト', 'wishlist', '欲しいもの']:
        return {'action': 'list_wishlist'}

    # ジャンル別
    genre_match = re.match(r'(?:ジャンル|genre)[：:]\s*(.+)', message, re.IGNORECASE)
    if genre_match:
        return {'action': 'list_by_genre', 'genre': genre_match.group(1)}

    # プラットフォーム別
    platform_match = re.match(r'(?:プラットフォーム|platform)[：:]\s*(.+)', message, re.IGNORECASE)
    if platform_match:
        return {'action': 'list_by_platform', 'platform': platform_match.group(1)}

    # 統計
    if message.strip() in ['統計', 'stats', 'ゲーム統計']:
        return {'action': 'stats'}

    return None

def parse_add(content):
    """ゲーム追加を解析"""
    result = {'action': 'add', 'title': None, 'platform': None, 'genre': None,
              'start_date': None, 'end_date': None, 'play_time': None, 'status': 'playing',
              'rating': None, 'notes': None}

    # タイトル (最初の部分)
    title_match = re.match(r'^([^、,（\(【]+)', content)
    if title_match:
        result['title'] = title_match.group(1).strip()

    # プラットフォーム
    platform_match = re.search(r'(?:プラットフォーム|platform|機種)[：:]\s*([^、,]+)', content)
    if platform_match:
        result['platform'] = platform_match.group(1).strip()

    # ジャンル
    genre_match = re.search(r'(?:ジャンル|genre)[：:]\s*([^、,]+)', content)
    if genre_match:
        result['genre'] = genre_match.group(1).strip()

    # 開始日
    start_match = re.search(r'(?:開始|start|from)[：:]\s*([^、,]+)', content)
    if start_match:
        result['start_date'] = parse_date(start_match.group(1).strip())

    # 終了日
    end_match = re.search(r'(?:終了|end|to|until)[：:]\s*([^、,]+)', content)
    if end_match:
        result['end_date'] = parse_date(end_match.group(1).strip())

    # プレイ時間
    time_match = re.search(r'(?:プレイ時間|play time|時間)[：:]\s*(\d+)(時間|h|hr)?', content)
    if time_match:
        result['play_time'] = int(time_match.group(1))

    # ステータス
    status_match = re.search(r'(?:ステータス|status)[：:]\s*(プレイ中|playing|クリア|completed|中断|dropped|ウィッシュリスト|wishlist)', content)
    if status_match:
        status_map = {
            'プレイ中': 'playing', 'playing': 'playing',
            'クリア': 'completed', 'completed': 'completed',
            '中断': 'dropped', 'dropped': 'dropped',
            'ウィッシュリスト': 'wishlist', 'wishlist': 'wishlist'
        }
        result['status'] = status_map.get(status_match.group(1).lower(), 'playing')

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
        for key in ['プラットフォーム', 'platform', '機種', 'ジャンル', 'genre', '開始', 'start', 'from',
                    '終了', 'end', 'to', 'until', 'プレイ時間', 'play time', '時間',
                    'ステータス', 'status', '評価', 'rating', '点数', 'メモ', '備考', 'memo', 'note']:
            match = re.search(rf'{key}[：:]', content)
            if match:
                result['title'] = content[:match.start()].strip()
                break
        else:
            result['title'] = content.strip()

    return result

def parse_update(content):
    """更新内容を解析"""
    result = {}

    # タイトル
    title_match = re.search(r'(?:タイトル|title)[：:]\s*([^、,]+)', content)
    if title_match:
        result['title'] = title_match.group(1).strip()

    # プラットフォーム
    platform_match = re.search(r'(?:プラットフォーム|platform|機種)[：:]\s*([^、,]+)', content)
    if platform_match:
        result['platform'] = platform_match.group(1).strip()

    # ジャンル
    genre_match = re.search(r'(?:ジャンル|genre)[：:]\s*([^、,]+)', content)
    if genre_match:
        result['genre'] = genre_match.group(1).strip()

    # 開始日
    start_match = re.search(r'(?:開始|start|from)[：:]\s*([^、,]+)', content)
    if start_match:
        result['start_date'] = parse_date(start_match.group(1).strip())

    # 終了日
    end_match = re.search(r'(?:終了|end|to|until)[：:]\s*([^、,]+)', content)
    if end_match:
        result['end_date'] = parse_date(end_match.group(1).strip())

    # プレイ時間
    time_match = re.search(r'(?:プレイ時間|play time|時間)[：:]\s*(\d+)', content)
    if time_match:
        result['play_time'] = int(time_match.group(1))

    # ステータス
    status_match = re.search(r'(?:ステータス|status)[：:]\s*(プレイ中|playing|クリア|completed|中断|dropped|ウィッシュリスト|wishlist)', content)
    if status_match:
        status_map = {
            'プレイ中': 'playing', 'playing': 'playing',
            'クリア': 'completed', 'completed': 'completed',
            '中断': 'dropped', 'dropped': 'dropped',
            'ウィッシュリスト': 'wishlist', 'wishlist': 'wishlist'
        }
        result['status'] = status_map.get(status_match.group(1).lower())

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

def parse_date(date_str):
    """日付を解析"""
    today = datetime.now()

    # 今日
    if '今日' in date_str:
        return today.strftime("%Y-%m-%d")

    # 昨日
    if '昨日' in date_str:
        from datetime import timedelta
        return (today - timedelta(days=1)).strftime("%Y-%m-%d")

    # 明日
    if '明日' in date_str:
        from datetime import timedelta
        return (today + timedelta(days=1)).strftime("%Y-%m-%d")

    # 日付形式
    date_match = re.match(r'(\d{4})-(\d{1,2})-(\d{1,2})', date_str)
    if date_match:
        return f"{date_match.group(1)}-{date_match.group(2).zfill(2)}-{date_match.group(3).zfill(2)}"

    date_match = re.match(r'(\d{1,2})/(\d{1,2})', date_str)
    if date_match:
        month = int(date_match.group(1))
        day = int(date_match.group(2))
        return datetime(today.year, month, day).strftime("%Y-%m-%d")

    # 数字 + 日前
    days_match = re.match(r'(\d+)日前', date_str)
    if days_match:
        from datetime import timedelta
        days = int(days_match.group(1))
        return (today - timedelta(days=days)).strftime("%Y-%m-%d")

    return None

def handle_message(message):
    """メッセージを処理"""
    parsed = parse_message(message)

    if not parsed:
        return None

    action = parsed['action']

    if action == 'add':
        if not parsed['title']:
            return "❌ タイトルを入力してください"

        game_id = add_game(
            parsed['title'],
            parsed['platform'],
            parsed['genre'],
            parsed['start_date'],
            parsed['end_date'],
            parsed['play_time'],
            parsed['status'],
            parsed['rating'],
            parsed['notes']
        )

        response = f"🎮 ゲーム #{game_id} 追加完了\n"
        response += f"タイトル: {parsed['title']}\n"
        if parsed['platform']:
            response += f"プラットフォーム: {parsed['platform']}\n"
        if parsed['genre']:
            response += f"ジャンル: {parsed['genre']}\n"
        if parsed['start_date']:
            response += f"開始日: {parsed['start_date']}\n"
        if parsed['end_date']:
            response += f"終了日: {parsed['end_date']}\n"
        if parsed['play_time']:
            response += f"プレイ時間: {parsed['play_time']}時間\n"
        if parsed['rating']:
            stars = "⭐" * parsed['rating']
            response += f"評価: {stars}\n"
        if parsed['notes']:
            response += f"メモ: {parsed['notes']}"

        return response

    elif action == 'update':
        updates = parse_update(parsed['content'])

        if not updates:
            return "❌ 更新内容がありません"

        update_game(parsed['game_id'], **updates)

        game = get_game(parsed['game_id'])
        if game:
            response = f"✅ ゲーム #{parsed['game_id']} 更新完了\n"
            response += format_game(game)
            return response
        else:
            return f"❌ ゲーム #{parsed['game_id']} が見つかりません"

    elif action == 'delete':
        delete_game(parsed['game_id'])
        return f"🗑️ ゲーム #{parsed['game_id']} 削除完了"

    elif action == 'complete':
        update_game(parsed['game_id'], status='completed')
        return f"🎉 ゲーム #{parsed['game_id']} クリアおめでとう！"

    elif action == 'drop':
        update_game(parsed['game_id'], status='dropped')
        return f"⏸️ ゲーム #{parsed['game_id']} 中断"

    elif action == 'search':
        keyword = parsed['keyword']
        games = search_games(keyword)

        if not games:
            return f"🔍 「{keyword}」の検索結果: 見つかりませんでした"

        response = f"🔍 「{keyword}」の検索結果 ({len(games)}件):\n"
        for game in games:
            response += format_game(game)

        return response

    elif action == 'list':
        games = list_games()

        if not games:
            return "🎮 ゲームがありません"

        response = f"🎮 ゲーム一覧 ({len(games)}件):\n"
        for game in games:
            response += format_game(game)

        return response

    elif action == 'list_playing':
        games = list_games(status='playing')

        if not games:
            return "🎮 プレイ中のゲームはありません"

        response = f"🎮 プレイ中のゲーム ({len(games)}件):\n"
        for game in games:
            response += format_game(game)

        return response

    elif action == 'list_completed':
        games = list_games(status='completed')

        if not games:
            return "🎮 クリア済みのゲームはありません"

        response = f"🎮 クリア済みのゲーム ({len(games)}件):\n"
        for game in games:
            response += format_game(game)

        return response

    elif action == 'list_wishlist':
        games = list_games(status='wishlist')

        if not games:
            return "🎮 ウィッシュリストにはありません"

        response = f"🎮 ウィッシュリスト ({len(games)}件):\n"
        for game in games:
            response += format_game(game)

        return response

    elif action == 'list_by_genre':
        games = list_games(genre=parsed['genre'])

        if not games:
            return f"🎮 「{parsed['genre']}」のゲームはありません"

        response = f"🎮 {parsed['genre']} ({len(games)}件):\n"
        for game in games:
            response += format_game(game)

        return response

    elif action == 'list_by_platform':
        games = list_games(platform=parsed['platform'])

        if not games:
            return f"🎮 「{parsed['platform']}」のゲームはありません"

        response = f"🎮 {parsed['platform']} ({len(games)}件):\n"
        for game in games:
            response += format_game(game)

        return response

    elif action == 'stats':
        stats = get_stats()

        response = "📊 ゲーム統計:\n"
        response += f"全ゲーム数: {stats['total']}本\n"
        response += f"プレイ中: {stats['playing']}本\n"
        response += f"クリア済み: {stats['completed']}本\n"
        response += f"中断: {stats['dropped']}本\n"
        response += f"ウィッシュリスト: {stats['wishlist']}本\n"
        if stats['total_play_time'] > 0:
            response += f"総プレイ時間: {stats['total_play_time']}時間"
        if stats['avg_rating']:
            response += f"\n平均評価: {stats['avg_rating']}⭐"

        return response

    return None

def format_game(game):
    """ゲームをフォーマット"""
    id, title, platform, genre, start_date, end_date, play_time, status, rating, notes, created_at = game

    # ステータス表示
    status_icons = {'playing': '🎮', 'completed': '✅', 'dropped': '⏸️', 'wishlist': '📋'}
    status_icon = status_icons.get(status, '❓')

    response = f"\n{status_icon} [{id}] {title}\n"

    if platform:
        response += f"    🖥️ {platform}\n"
    if genre:
        response += f"    🎭 {genre}\n"
    if start_date:
        response += f"    📅 {start_date} - {end_date or '?'}\n"
    if play_time:
        response += f"    ⏱️ {play_time}時間\n"
    if rating:
        stars = "⭐" * rating
        response += f"    {stars}\n"
    if notes:
        response += f"    📝 {notes}\n"

    return response

if __name__ == '__main__':
    # テスト
    init_db()

    test_messages = [
        "ゲーム: ゼルダの伝説, プラットフォーム: Switch, ジャンル: アクションRPG",
        "ゲーム: マリオカート, プラットフォーム: Switch, ジャンル: レース, 評価: 5",
        "クリア: 1",
        "プレイ中",
        "検索: Switch",
        "統計",
    ]

    for msg in test_messages:
        print(f"\n入力: {msg}")
        result = handle_message(msg)
        if result:
            print(result)
