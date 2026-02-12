#!/usr/bin/env python3
"""
ブックマーク管理エージェント - Discord連携
Bookmark Management Agent - Discord Integration
"""

import re
from datetime import datetime
from db import *

def parse_message(message):
    """メッセージを解析 / Parse message"""

    # ブックマーク追加 / Add bookmark
    add_match = re.match(r'(?:ブックマーク|bookmark|ブクマ|bm)[:：]\s*(.+)', message, re.IGNORECASE)
    if add_match:
        return parse_add(add_match.group(1))

    # 削除 / Delete
    delete_match = re.match(r'(?:削除|delete|del)[:：]\s*(\d+)', message, re.IGNORECASE)
    if delete_match:
        return {'action': 'delete', 'bookmark_id': int(delete_match.group(1))}

    # 検索 / Search
    search_match = re.match(r'(?:検索|search)[:：]\s*(.+)', message, re.IGNORECASE)
    if search_match:
        return {'action': 'search', 'keyword': search_match.group(1)}

    # タグ検索 / Search by tag
    tag_match = re.match(r'(?:タグ|tag)[:：]\s*(.+)', message, re.IGNORECASE)
    if tag_match:
        return {'action': 'search_tag', 'tag_name': tag_match.group(1)}

    # 一覧 / List
    list_match = re.match(r'(?:ブックマーク|bookmark|ブクマ)(?:一覧|list)?', message, re.IGNORECASE)
    if list_match:
        return {'action': 'list'}

    # カテゴリ一覧 / Category list
    if message.strip() in ['カテゴリ一覧', 'categories', 'cats']:
        return {'action': 'categories'}

    # タグ一覧 / Tag list
    if message.strip() in ['タグ一覧', 'tags']:
        return {'action': 'tags'}

    # 共有リンク作成 / Create share link
    share_match = re.match(r'(?:共有|share)[:：]\s*(\d+)', message, re.IGNORECASE)
    if share_match:
        return {'action': 'share', 'bookmark_id': int(share_match.group(1))}

    # 統計 / Stats
    if message.strip() in ['統計', 'stats', 'ブックマーク統計']:
        return {'action': 'stats'}

    # 更新 / Update
    update_match = re.match(r'(?:更新|update)[:：]\s*(\d+)\s*,\s*(.+)', message, re.IGNORECASE)
    if update_match:
        return parse_update(int(update_match.group(1)), update_match.group(2))

    return None

def parse_add(content):
    """ブックマーク追加を解析 / Parse bookmark add"""
    result = {'action': 'add', 'url': None, 'title': None, 'description': None, 'category': None, 'tags': None}

    # URL (http/httpsで始まるもの)
    url_match = re.search(r'https?://[^\s,、]+', content)
    if url_match:
        result['url'] = url_match.group(0).strip()
        content = content.replace(url_match.group(0), '', 1).strip()
    else:
        return None  # URLは必須

    # タイトル
    title_match = re.search(r'(?:タイトル|title)[:：]\s*([^,、]+)', content, re.IGNORECASE)
    if title_match:
        result['title'] = title_match.group(1).strip()

    # 説明
    desc_match = re.search(r'(?:説明|description|desc)[:：]\s*(.+)', content, re.IGNORECASE)
    if desc_match:
        result['description'] = desc_match.group(1).strip()

    # カテゴリ
    cat_match = re.search(r'(?:カテゴリ|category|cat)[:：]\s*([^,、]+)', content, re.IGNORECASE)
    if cat_match:
        result['category'] = cat_match.group(1).strip()

    # タグ
    tag_match = re.search(r'(?:タグ|tag)[:：]\s*(.+)', content, re.IGNORECASE)
    if tag_match:
        tags_str = tag_match.group(1).strip()
        # カンマ、スペースで区切られたタグを配列に
        result['tags'] = [t.strip() for t in re.split(r'[,、\s]+', tags_str) if t.strip()]

    return result

def parse_update(bookmark_id, content):
    """更新を解析 / Parse update"""
    result = {'action': 'update', 'bookmark_id': bookmark_id, 'url': None, 'title': None, 'description': None, 'category': None}

    # URL
    url_match = re.search(r'url[:：]\s*(https?://[^\s,、]+)', content, re.IGNORECASE)
    if url_match:
        result['url'] = url_match.group(1).strip()

    # タイトル
    title_match = re.search(r'(?:タイトル|title)[:：]\s*([^,、]+)', content, re.IGNORECASE)
    if title_match:
        result['title'] = title_match.group(1).strip()

    # 説明
    desc_match = re.search(r'(?:説明|description|desc)[:：]\s*(.+)', content, re.IGNORECASE)
    if desc_match:
        result['description'] = desc_match.group(1).strip()

    # カテゴリ
    cat_match = re.search(r'(?:カテゴリ|category|cat)[:：]\s*([^,、]+)', content, re.IGNORECASE)
    if cat_match:
        result['category'] = cat_match.group(1).strip()

    return result

def handle_message(message):
    """メッセージを処理 / Handle message"""
    parsed = parse_message(message)

    if not parsed:
        return None

    action = parsed['action']

    if action == 'add':
        if not parsed['url']:
            return "❌ URLを入力してください / Please enter a URL"

        bookmark_id = add_bookmark(
            parsed['url'],
            parsed['title'],
            parsed['description'],
            parsed['category'],
            parsed['tags']
        )

        response = f"✅ ブックマーク #{bookmark_id} 追加完了 / Bookmark added\n"
        response += f"URL: {parsed['url']}\n"
        if parsed['title']:
            response += f"タイトル / Title: {parsed['title']}\n"
        if parsed['category']:
            response += f"カテゴリ / Category: {parsed['category']}\n"
        if parsed['tags']:
            response += f"タグ / Tags: {', '.join(parsed['tags'])}"

        return response

    elif action == 'delete':
        delete_bookmark(parsed['bookmark_id'])
        return f"🗑️ ブックマーク #{parsed['bookmark_id']} 削除完了 / Bookmark deleted"

    elif action == 'search':
        keyword = parsed['keyword']
        bookmarks = search_bookmarks(keyword)

        if not bookmarks:
            return f"🔍 「{keyword}」の検索結果: 見つかりませんでした / No results found for \"{keyword}\""

        response = f"🔍 「{keyword}」の検索結果 ({len(bookmarks)}件 / results):\n"
        for bookmark in bookmarks:
            response += format_bookmark(bookmark)

        return response

    elif action == 'search_tag':
        tag_name = parsed['tag_name']
        bookmarks = search_by_tag(tag_name)

        if not bookmarks:
            return f"🏷️ タグ「{tag_name}」の検索結果: 見つかりませんでした / No bookmarks found with tag \"{tag_name}\""

        response = f"🏷️ タグ「{tag_name}」のブックマーク ({len(bookmarks)}件 / bookmarks):\n"
        for bookmark in bookmarks:
            response += format_bookmark(bookmark)

        return response

    elif action == 'list':
        bookmarks = list_bookmarks()

        if not bookmarks:
            return "📋 ブックマークがありません / No bookmarks found"

        response = f"📋 ブックマーク一覧 ({len(bookmarks)}件 / bookmarks):\n"
        for bookmark in bookmarks:
            response += format_bookmark(bookmark)

        return response

    elif action == 'categories':
        categories = get_categories()

        if not categories:
            return "📁 カテゴリがありません / No categories found"

        response = "📁 カテゴリ一覧 / Categories:\n"
        for cat in categories:
            response += f"  • {cat[1]}\n"

        return response

    elif action == 'tags':
        tags = get_tags()

        if not tags:
            return "🏷️ タグがありません / No tags found"

        response = "🏷️ タグ一覧 / Tags:\n"
        for tag in tags:
            response += f"  • {tag[1]}\n"

        return response

    elif action == 'share':
        shared_key = create_share_link(parsed['bookmark_id'])
        return f"🔗 共有リンク / Share link: `!bm get {shared_key}`"

    elif action == 'update':
        update_bookmark(
            parsed['bookmark_id'],
            parsed['url'],
            parsed['title'],
            parsed['description'],
            parsed['category']
        )
        response = f"✏️ ブックマーク #{parsed['bookmark_id']} 更新完了 / Bookmark updated\n"
        if parsed['title']:
            response += f"タイトル / Title: {parsed['title']}\n"
        if parsed['category']:
            response += f"カテゴリ / Category: {parsed['category']}\n"

        return response

    elif action == 'stats':
        stats = get_stats()

        response = "📊 ブックマーク統計 / Bookmark Stats:\n"
        response += f"全ブックマーク数 / Total: {stats['total_bookmarks']}件\n"
        response += f"共有済み / Shared: {stats['shared']}件"

        if stats['by_category']:
            top_cat = list(stats['by_category'].items())[0]
            response += f"\nトップカテゴリ / Top category: {top_cat[0]} ({top_cat[1]}件)"

        if stats['by_tag']:
            top_tag = list(stats['by_tag'].items())[0]
            response += f"\nトップタグ / Top tag: {top_tag[0]} ({top_tag[1]}件)"

        return response

    return None

def format_bookmark(bookmark):
    """ブックマークをフォーマット / Format bookmark"""
    id, url, title, description, category, view_count, created_at = bookmark

    response = f"\n🔗 [{id}] "
    response += f"{title if title else url[:50]}...\n"
    if description:
        response += f"    💬 {description[:100]}...\n"
    response += f"    🔗 {url}\n"
    if category:
        response += f"    📁 {category}\n"
    response += f"    👁️ {view_count}回\n"

    return response

if __name__ == '__main__':
    # テスト / Test
    init_db()

    test_messages = [
        "ブックマーク: https://example.com, タイトル:Example Site, カテゴリ:Work",
        "ブックマーク: https://github.com, タグ:code, git, dev",
        "タグ: code",
        "検索: github",
        "ブックマーク一覧",
        "統計",
    ]

    for msg in test_messages:
        print(f"\n入力 / Input: {msg}")
        result = handle_message(msg)
        if result:
            print(result)
