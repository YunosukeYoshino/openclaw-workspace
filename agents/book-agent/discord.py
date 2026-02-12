#!/usr/bin/env python3
"""
読書記録エージェント #4 - Discord連携
"""

import re
from db import *

def parse_message(message):
    """メッセージを解析"""
    # 本追加
    book_match = re.match(r'読書[:：]\s*(.+)', message)
    if book_match:
        return parse_book(book_match.group(1))

    # 検索
    search_match = re.match(r'検索[:：]\s*(.+)', message)
    if search_match:
        return {'action': 'search', 'keyword': search_match.group(1)}

    # 一覧
    if message.strip() in ['読書一覧', '一覧', 'list', 'books']:
        return {'action': 'list'}

    # 統計
    if message.strip() in ['統計', 'stats', '読書統計']:
        return {'action': 'stats'}

    return None

def parse_book(content):
    """本情報を解析"""
    result = {'action': 'book', 'title': None, 'author': None, 'genre': None, 'rating': None, 'memo': None}

    # タイトル (最初の部分)
    title_match = re.match(r'^([^、,（\(]+)', content)
    if title_match:
        result['title'] = title_match.group(1).strip()
        content = content.replace(title_match.group(0), '').strip()

    # 著者
    author_match = re.search(r'著者[:：]\s*([^、,]+)', content)
    if author_match:
        result['author'] = author_match.group(1).strip()

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

    if action == 'book':
        if not parsed['title']:
            return "❌ タイトルを入力してください"

        book_id = add_book(
            parsed['title'],
            parsed['author'],
            parsed['genre'],
            parsed['rating'],
            parsed['memo'],
            datetime.now().strftime("%Y-%m-%d"),
            datetime.now().strftime("%Y-%m-%d")
        )

        response = f"📚 読書記録 #{book_id} 追加完了\n"
        response += f"タイトル: {parsed['title']}\n"
        if parsed['author']:
            response += f"著者: {parsed['author']}\n"
        if parsed['genre']:
            response += f"ジャンル: {parsed['genre']}\n"
        if parsed['rating']:
            response += f"評価: {parsed['rating']}/5⭐"
        if parsed['memo']:
            response += f"\nメモ: {parsed['memo']}"

        return response

    elif action == 'search':
        keyword = parsed['keyword']
        books = search_books(keyword)

        if not books:
            return f"🔍 「{keyword}」の検索結果: 見つかりませんでした"

        response = f"🔍 「{keyword}」の検索結果 ({len(books)}件):\n"
        for book in books:
            id, title, author, genre, rating, finished_at = book
            response += f"\n[{id}] {title}\n"
            if author:
                response += f"    著者: {author}\n"
            if genre:
                response += f"    ジャンル: {genre}\n"
            if rating:
                stars = "⭐" * rating
                response += f"    評価: {stars}\n"

        return response

    elif action == 'list':
        books = list_books()

        if not books:
            return "📚 読書記録がありません"

        response = f"📚 読書記録一覧 ({len(books)}件):\n"
        for book in books:
            id, title, author, genre, rating, finished_at = book
            response += f"\n[{id}] {title}\n"
            if author:
                response += f"    著者: {author}\n"
            if genre:
                response += f"    ジャンル: {genre}\n"
            if rating:
                stars = "⭐" * rating
                response += f"    評価: {stars}\n"

        return response

    elif action == 'stats':
        stats = get_stats()

        response = "📊 読書統計:\n"
        response += f"全冊数: {stats['total_books']}冊\n\n"

        if stats['by_genre']:
            response += "ジャンル別:\n"
            for genre, count in stats['by_genre'].items():
                response += f"  - {genre}: {count}冊\n"

        if stats['by_rating']:
            response += "\n評価別:\n"
            for rating, count in stats['by_rating'].items():
                stars = "⭐" * rating
                response += f"  - {stars} ({rating}): {count}冊\n"

        return response

    return None

if __name__ == '__main__':
    # テスト
    init_db()

    test_messages = [
        "読書: 吾輩は猫である, 著者:夏目漱石, ジャンル:文学, 評価:5",
        "読書: プログラミング入門, 著者:誰か, ジャンル:技術, 評価:4",
        "読書: SF小説, 評価:3",
        "検索: 夏目",
        "読書一覧",
        "統計",
    ]

    for msg in test_messages:
        print(f"\n入力: {msg}")
        result = handle_message(msg)
        if result:
            print(result)
