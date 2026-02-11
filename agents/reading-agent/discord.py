#!/usr/bin/env python3
"""
リーディングエージェント #41 - Discord連携
"""

import re
from datetime import datetime
from db import *

def parse_message(message):
    """メッセージを解析"""
    # 追加
    add_match = re.match(r'(?:読書|reading|book)[：:]\s*(.+)', message, re.IGNORECASE)
    if add_match:
        return {'action': 'add', 'content': add_match.group(1)}

    # 更新
    update_match = re.match(r'(?:更新|update)[：:]\s*(\d+)\s*(.+)', message, re.IGNORECASE)
    if update_match:
        return {'action': 'update', 'book_id': int(update_match.group(1)), 'content': update_match.group(2)}

    # 読了
    finish_match = re.match(r'(?:読了|finish|complete)[：:]\s*(\d+)', message, re.IGNORECASE)
    if finish_match:
        return {'action': 'finish', 'book_id': int(finish_match.group(1))}

    # 進捗
    progress_match = re.match(r'(?:進捗|progress)[：:]\s*(\d+)\s*([^:]+)?', message, re.IGNORECASE)
    if progress_match:
        note = progress_match.group(2).strip() if progress_match.group(2) else None
        return {'action': 'progress', 'book_id': int(progress_match.group(1)), 'note': note}

    # 削除
    delete_match = re.match(r'(?:削除|delete|remove)[：:]\s*(\d+)', message, re.IGNORECASE)
    if delete_match:
        return {'action': 'delete', 'book_id': int(delete_match.group(1))}

    # 検索
    search_match = re.match(r'(?:検索|search)[：:]\s*(.+)', message, re.IGNORECASE)
    if search_match:
        return {'action': 'search', 'keyword': search_match.group(1)}

    # 一覧
    list_match = re.match(r'(?:(?:読書|reading|book)(?:一覧|list)|list|books)', message, re.IGNORECASE)
    if list_match:
        return {'action': 'list'}

    # 読書中
    if message.strip() in ['読書中', 'reading', 'now reading']:
        return {'action': 'list_by_status', 'status': 'reading'}

    # 読了本
    if message.strip() in ['読了', 'completed', 'finished']:
        return {'action': 'list_by_status', 'status': 'completed'}

    # 統計
    if message.strip() in ['統計', 'stats', '読書統計']:
        return {'action': 'stats'}

    return None

def parse_add(content):
    """追加内容を解析"""
    result = {'title': None, 'author': None, 'isbn': None, 'pages': None,
              'status': 'reading', 'notes': None, 'tags': None}

    # 書名 (最初の項目より前)
    for key in ['著者', 'author', 'ISBN', 'isbn', 'ページ', 'pages', 'メモ', 'memo', 'note', 'タグ', 'tag']:
        match = re.search(rf'{key}[：:]', content)
        if match:
            result['title'] = content[:match.start()].strip()
            break
    else:
        result['title'] = content.strip()

    # 著者
    author_match = re.search(r'(?:著者|author)[：:]\s*([^、,]+)', content, re.IGNORECASE)
    if author_match:
        result['author'] = author_match.group(1).strip()

    # ISBN
    isbn_match = re.search(r'(?:ISBN|isbn)[：:]\s*(\d+)', content)
    if isbn_match:
        result['isbn'] = isbn_match.group(1)

    # ページ数
    pages_match = re.search(r'(?:ページ|pages?)[：:]?\s*(\d+)', content, re.IGNORECASE)
    if pages_match:
        result['pages'] = int(pages_match.group(1))

    # メモ
    notes_match = re.search(r'(?:メモ|memo|note)[：:]\s*(.+)', content)
    if notes_match:
        result['notes'] = notes_match.group(1).strip()

    # タグ
    tags_match = re.search(r'(?:タグ|tags?)[：:]\s*(.+)', content, re.IGNORECASE)
    if tags_match:
        result['tags'] = tags_match.group(1).strip()

    return result

def parse_update(content):
    """更新内容を解析"""
    result = {}

    # 書名
    title_match = re.search(r'(?:書名|title)[：:]\s*([^、,]+)', content, re.IGNORECASE)
    if title_match:
        result['title'] = title_match.group(1).strip()

    # 著者
    author_match = re.search(r'(?:著者|author)[：:]\s*([^、,]+)', content, re.IGNORECASE)
    if author_match:
        result['author'] = author_match.group(1).strip()

    # 評価
    rating_match = re.search(r'(?:評価|rating)[：:]\s*(\d)', content)
    if rating_match:
        result['rating'] = int(rating_match.group(1))

    # メモ
    notes_match = re.search(r'(?:メモ|memo|note)[：:]\s*(.+)', content)
    if notes_match:
        result['notes'] = notes_match.group(1).strip()

    # タグ
    tags_match = re.search(r'(?:タグ|tags?)[：:]\s*(.+)', content, re.IGNORECASE)
    if tags_match:
        result['tags'] = tags_match.group(1).strip()

    return result

def handle_message(message):
    """メッセージを処理"""
    parsed = parse_message(message)

    if not parsed:
        return None

    action = parsed['action']

    if action == 'add':
        content = parse_add(parsed['content'])

        if not content['title']:
            return "❌ 書名を入力してください"

        book_id = add_book(
            content['title'],
            content['author'],
            content['isbn'],
            content['pages'],
            content['status'],
            notes=content['notes'],
            tags=content['tags']
        )

        response = f"📖 本 #{book_id} 追加完了\n"
        response += f"書名: {content['title']}\n"
        if content['author']:
            response += f"著者: {content['author']}\n"
        if content['pages']:
            response += f"ページ: {content['pages']}ページ\n"
        if content['notes']:
            response += f"メモ: {content['notes']}"

        return response

    elif action == 'update':
        updates = parse_update(parsed['content'])

        if not updates:
            return "❌ 更新内容がありません"

        update_book(parsed['book_id'], **updates)

        response = f"✅ 本 #{parsed['book_id']} 更新完了"

        return response

    elif action == 'finish':
        finish_date = datetime.now().strftime("%Y-%m-%d")
        update_book(parsed['book_id'], status='completed', finish_date=finish_date)
        return f"🎉 本 #{parsed['book_id']} 読了完了！"

    elif action == 'progress':
        progress_id = add_progress(parsed['book_id'], note=parsed['note'])
        return f"📝 進捗記録 #{progress_id} 追加完了 (本 #{parsed['book_id']})"

    elif action == 'delete':
        delete_book(parsed['book_id'])
        return f"🗑️ 本 #{parsed['book_id']} 削除完了"

    elif action == 'search':
        keyword = parsed['keyword']
        books = search_books(keyword)

        if not books:
            return f"🔍 「{keyword}」の検索結果: 見つかりませんでした"

        response = f"🔍 「{keyword}」の検索結果 ({len(books)}件):\n"
        for book in books:
            response += format_book(book)

        return response

    elif action == 'list':
        books = list_books()

        if not books:
            return "📖 本がありません"

        response = f"📖 本一覧 ({len(books)}件):\n"
        for book in books:
            response += format_book(book)

        return response

    elif action == 'list_by_status':
        books = list_books(status=parsed['status'])

        if not books:
            if parsed['status'] == 'reading':
                return "📖 読書中の本はありません"
            else:
                return "📖 読了した本はありません"

        status_text = "読書中" if parsed['status'] == 'reading' else "読了"
        response = f"📖 {status_text}の本 ({len(books)}件):\n"
        for book in books:
            response += format_book(book)

        return response

    elif action == 'stats':
        stats = get_stats()

        response = "📊 読書統計:\n"
        response += f"全本数: {stats['total']}冊\n"
        if stats['by_status'].get('reading'):
            response += f"読書中: {stats['by_status']['reading']}冊\n"
        if stats['by_status'].get('completed'):
            response += f"読了: {stats['by_status']['completed']}冊\n"
        if stats['completed_this_month']:
            response += f"今月読了: {stats['completed_this_month']}冊\n"
        if stats['avg_rating']:
            response += f"平均評価: {stats['avg_rating']}/5.0\n"
        if stats['total_pages'] > 0:
            response += f"総ページ数: {stats['total_pages']:,}ページ"

        return response

    return None

def format_book(book):
    """本をフォーマット"""
    id, title, author, isbn, pages, rating, status, start_date, finish_date, notes, tags, created_at = book

    status_emoji = {
        'reading': '📖',
        'completed': '✅',
        'abandoned': '🚫'
    }

    response = f"\n{status_emoji.get(status, '📚')} [{id}] {title}\n"

    parts = []
    if author:
        parts.append(f"著者: {author}")
    if rating:
        stars = '⭐' * rating
        parts.append(f"評価: {stars}")
    if status == 'completed' and finish_date:
        parts.append(f"読了日: {finish_date}")

    if parts:
        response += f"    {' | '.join(parts)}\n"

    return response

if __name__ == '__main__':
    init_db()

    test_messages = [
        "読書: Clean Code, 著者: Robert C. Martin, ページ: 464",
        "読書: Pythonの勉強",
        "読了: 1",
        "読書中",
        "統計",
    ]

    for msg in test_messages:
        print(f"\n入力: {msg}")
        result = handle_message(msg)
        if result:
            print(result)
