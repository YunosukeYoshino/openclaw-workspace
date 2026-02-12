#!/usr/bin/env python3
"""
映画記録エージェント #6 - Discord連携
"""

import re
from db import *

def parse_message(message):
    """メッセージを解析"""
    # 映画追加
    movie_match = re.match(r'映画[:：]\s*(.+)', message)
    if movie_match:
        return parse_movie(movie_match.group(1))

    # 検索
    search_match = re.match(r'検索[:：]\s*(.+)', message)
    if search_match:
        return {'action': 'search', 'keyword': search_match.group(1)}

    # 一覧
    if message.strip() in ['映画一覧', '一覧', 'list', 'movies']:
        return {'action': 'list'}

    # 統計
    if message.strip() in ['統計', 'stats', '映画統計']:
        return {'action': 'stats'}

    return None

def parse_movie(content):
    """映画情報を解析"""
    result = {'action': 'movie', 'title': None, 'director': None, 'genre': None, 'rating': None, 'memo': None}

    # タイトル (最初の部分)
    title_match = re.match(r'^([^、,（\(（]+)', content)
    if title_match:
        result['title'] = title_match.group(1).strip()
        content = content.replace(title_match.group(0), '').strip()

    # 監督
    director_match = re.search(r'監督[:：]\s*([^、,]+)', content)
    if director_match:
        result['director'] = director_match.group(1).strip()

    # ジャンル
    genre_match = re.search(r'ジャンル[:：]\s*([^、,]+)', content)
    if genre_match:
        result['genre'] = genre_match.group(1).strip()

    # 評価
    rating_match = re.search(r'評価[:：]\s*(\d+)(?:/5)?', content)
    if rating_match:
        result['rating'] = int(rating_match.group(1))

    # メモ
    memo_match = re.search(r'メモ[:：]\s*(.+)', content)
    if memo_match:
        result['memo'] = memo_match.group(1).strip()

    return result

def handle_message(message):
    """メッセージを処理"""
    parsed = parse_message(message)

    if not parsed:
        return None

    action = parsed['action']

    if action == 'movie':
        if not parsed['title']:
            return "❌ タイトルを入力してください"

        movie_id = add_movie(
            parsed['title'],
            parsed['director'],
            parsed['genre'],
            parsed['rating'],
            parsed['memo'],
            datetime.now().strftime("%Y-%m-%d")
        )

        response = f"🎬 映画記録 #{movie_id} 追加完了\n"
        response += f"タイトル: {parsed['title']}\n"
        if parsed['director']:
            response += f"監督: {parsed['director']}\n"
        if parsed['genre']:
            response += f"ジャンル: {parsed['genre']}\n"
        if parsed['rating']:
            stars = "⭐" * parsed['rating']
            response += f"評価: {stars}"
        if parsed['memo']:
            response += f"\nメモ: {parsed['memo']}"

        return response

    elif action == 'search':
        keyword = parsed['keyword']
        movies = search_movies(keyword)

        if not movies:
            return f"🔍 「{keyword}」の検索結果: 見つかりませんでした"

        response = f"🔍 「{keyword}」の検索結果 ({len(movies)}件):\n"
        for movie in movies:
            response += format_movie(movie)

        return response

    elif action == 'list':
        movies = list_movies()

        if not movies:
            return "🎬 映画記録がありません"

        response = f"🎬 映画記録一覧 ({len(movies)}件):\n"
        for movie in movies:
            response += format_movie(movie)

        return response

    elif action == 'stats':
        stats = get_stats()

        response = "📊 映画統計:\n"
        response += f"全映画数: {stats['total_movies']}本\n\n"

        if stats['by_genre']:
            response += "ジャンル別:\n"
            for genre, count in stats['by_genre'].items():
                response += f"  - {genre}: {count}本\n"

        if stats['by_rating']:
            response += "\n評価別:\n"
            for rating, count in stats['by_rating'].items():
                stars = "⭐" * rating
                response += f"  - {stars} ({rating}): {count}本\n"

        return response

    return None

def format_movie(movie):
    """映画をフォーマット"""
    id, title, director, genre, rating, watched_at = movie
    response = f"\n[{id}] {title}\n"
    if director:
        response += f"    監督: {director}\n"
    if genre:
        response += f"    ジャンル: {genre}\n"
    if rating:
        stars = "⭐" * rating
        response += f"    評価: {stars}\n"
    response += f"    視聴日: {watched_at}\n"
    return response

if __name__ == '__main__':
    # テスト
    init_db()

    test_messages = [
        "映画: インセプション, 監督:クリストファー・ノーラン, ジャンル:SF, 評価:5",
        "映画: ザ・マトリックス, ジャンル:SF, 評価:4",
        "映画: ローマの休日, 評価:5",
        "検索: ノーラン",
        "映画一覧",
        "統計",
    ]

    for msg in test_messages:
        print(f"\n入力: {msg}")
        result = handle_message(msg)
        if result:
            print(result)
