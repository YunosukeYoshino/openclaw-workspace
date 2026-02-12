#!/usr/bin/env python3
"""
Newsfeed Agent #30 - Discord Integration
"""

import re
from db import *

def parse_message(message):
    """Parse message"""
    # Add news
    add_match = re.match(r'(?:追加|add|new)[:：]\s*(.+)', message, re.IGNORECASE)
    if add_match:
        return parse_add(add_match.group(1))

    # Mark read
    read_match = re.match(r'(?:既読|read)[:：]\s*(\d+)', message, re.IGNORECASE)
    if read_match:
        return {'action': 'mark_read', 'news_id': int(read_match.group(1))}

    # Mark saved
    save_match = re.match(r'(?:保存|save|saved)[:：]\s*(\d+)', message, re.IGNORECASE)
    if save_match:
        return {'action': 'mark_saved', 'news_id': int(save_match.group(1))}

    # Add source
    source_match = re.match(r'(?:ソース|source)[:：]\s*(.+)', message, re.IGNORECASE)
    if source_match:
        return parse_source(source_match.group(1))

    # List news
    list_match = re.match(r'(?:一覧|list|news)(?:[:：]\s*(\w+))?', message, re.IGNORECASE)
    if list_match:
        status = list_match.group(1) if list_match.group(1) else None
        return {'action': 'list', 'status': status}

    # Search news
    search_match = re.match(r'(?:検索|search)[:：]\s*(.+)', message, re.IGNORECASE)
    if search_match:
        return {'action': 'search', 'keyword': search_match.group(1)}

    # List sources
    if message.strip() in ['ソース一覧', 'sources']:
        return {'action': 'list_sources'}

    # Archive old news
    archive_match = re.match(r'(?:アーカイブ|archive)[:：]\s*(\d+)', message, re.IGNORECASE)
    if archive_match:
        return {'action': 'archive_old', 'days': int(archive_match.group(1))}

    # Stats
    if message.strip() in ['統計', 'stats']:
        return {'action': 'stats'}

    return None

def parse_add(content):
    """Parse add content"""
    result = {'action': 'add', 'title': None, 'url': None, 'source': None, 'category': None, 'summary': None, 'author': None, 'importance': 0, 'tags': None, 'notes': None}

    # Title
    title_match = re.match(r'^([^、,]+)', content)
    if title_match:
        result['title'] = title_match.group(1).strip()

    # URL
    url_match = re.search(r'https?://[^\s、,]+', content)
    if url_match:
        result['url'] = url_match.group(0).strip()

    # Source
    source_match = re.search(r'ソース|source[:：]\s*(.+?)(?:[、,]|$)', content)
    if source_match:
        result['source'] = source_match.group(1).strip()

    # Category
    cat_match = re.search(r'カテゴリ|category[:：]\s*(.+?)(?:[、,]|$)', content)
    if cat_match:
        result['category'] = cat_match.group(1).strip()

    # Importance
    imp_match = re.search(r'重要度|importance[:：]\s*(\d)', content)
    if imp_match:
        result['importance'] = int(imp_match.group(1))

    # Summary
    sum_match = re.search(r'要約|summary[:：]\s*(.+)', content)
    if sum_match:
        result['summary'] = sum_match.group(1).strip()

    # Tags
    tags_match = re.search(r'タグ|tags[:：]\s*(.+)', content)
    if tags_match:
        result['tags'] = tags_match.group(1).strip()

    # Notes
    note_match = re.search(r'メモ|notes[:：]\s*(.+)', content)
    if note_match:
        result['notes'] = note_match.group(1).strip()

    return result

def parse_source(content):
    """Parse source content"""
    result = {'action': 'add_source', 'name': None, 'url': None, 'category': None}

    # Name
    name_match = re.match(r'^([^、,]+)', content)
    if name_match:
        result['name'] = name_match.group(1).strip()

    # URL
    url_match = re.search(r'https?://[^\s、,]+', content)
    if url_match:
        result['url'] = url_match.group(0).strip()

    # Category
    cat_match = re.search(r'カテゴリ|category[:：]\s*(.+)', content)
    if cat_match:
        result['category'] = cat_match.group(1).strip()

    return result

def handle_message(message):
    """Handle message"""
    parsed = parse_message(message)

    if not parsed:
        return None

    action = parsed['action']

    if action == 'add':
        if not parsed['title']:
            return "❌ タイトルを入力してください"

        news_id = add_news(
            parsed['title'],
            parsed['url'],
            parsed['source'],
            parsed['category'],
            parsed['summary'],
            None,
            parsed['importance'],
            parsed['tags'],
            parsed['notes']
        )

        response = f"📰 ニュース #{news_id} 追加完了\n"
        response += f"タイトル: {parsed['title']}\n"
        if parsed['source']:
            response += f"ソース: {parsed['source']}\n"
        if parsed['category']:
            response += f"カテゴリ: {parsed['category']}"
        if parsed['importance'] > 0:
            response += f" | 重要度: {'⭐' * parsed['importance']}"

        return response

    elif action == 'add_source':
        if not parsed['name']:
            return "❌ ソース名を入力してください"

        source_id = add_source(parsed['name'], parsed['url'], parsed['category'])
        return f"📡 ニュースソース #{source_id} 追加完了: {parsed['name']}"

    elif action == 'mark_read':
        mark_read(parsed['news_id'])
        return f"✅ ニュース #{parsed['news_id']} を既読にしました"

    elif action == 'mark_saved':
        mark_saved(parsed['news_id'])
        return f"⭐ ニュース #{parsed['news_id']} を保存しました"

    elif action == 'list':
        news_items = list_news(status=parsed['status'])

        if not news_items:
            return f"📰 ニュースがありません"

        status_text = f" ({parsed['status']})" if parsed['status'] else ""
        response = f"📰 ニュース一覧{status_text} ({len(news_items)}件):\n"
        for item in news_items:
            response += format_news(item)

        return response

    elif action == 'search':
        news_items = search_news(parsed['keyword'])

        if not news_items:
            return f"🔍 「{parsed['keyword']}」の検索結果: 見つかりませんでした"

        response = f"🔍 「{parsed['keyword']}」の検索結果 ({len(news_items)}件):\n"
        for item in news_items:
            response += format_news(item)

        return response

    elif action == 'list_sources':
        sources = list_sources()

        if not sources:
            return "📡 ニュースソースがありません"

        response = f"📡 ニュースソース一覧 ({len(sources)}件):\n"
        for src in sources:
            response += format_source(src)

        return response

    elif action == 'archive_old':
        archive_old_news(parsed['days'])
        return f"📦 {parsed['days']}日以上前の既読ニュースをアーカイブしました"

    elif action == 'stats':
        stats = get_stats()

        response = "📊 ニュース統計:\n"
        response += f"全ニュース: {stats['total_news']}件\n"
        response += f"未読: {stats['unread']}件\n"
        response += f"既読: {stats['read']}件\n"
        response += f"保存済み: {stats['saved']}件\n"
        response += f"アーカイブ: {stats['archived']}件\n"
        response += f"アクティブソース: {stats['active_sources']}件"

        return response

    return None

def format_news(news):
    """Format news item"""
    id, title, url, source, category, summary, author, publish_date, status, importance, tags, created_at = news

    status_map = {'unread': '🔵', 'read': '⚪', 'saved': '⭐', 'archived': '📦'}
    status_icon = status_map.get(status, '❓')

    importance_stars = '⭐' * importance if importance else ''

    response = f"\n{status_icon} [{id}] {title} {importance_stars}\n"
    if source:
        response += f"    ソース: {source}\n"
    if category:
        response += f"    カテゴリ: {category}\n"

    return response

def format_source(src):
    """Format news source"""
    id, name, url, category, status, last_fetched, created_at = src

    response = f"\n📡 [{id}] {name}\n"
    if category:
        response += f"    カテゴリ: {category}\n"
    if url:
        response += f"    URL: {url}\n"

    return response

if __name__ == '__main__':
    init_db()

    test_messages = [
        "追加: 新技術が発表, ソース: TechNews, カテゴリ: テクノロジー, 重要度: 3",
        "追加: 新製品リリース, ソース: ProductNews",
        "一覧",
        "一覧: unread",
        "既読: 1",
        "保存: 2",
        "検索: テクノロジー",
        "ソース: TechNews, https://technews.com",
        "ソース一覧",
        "統計",
    ]

    for msg in test_messages:
        print(f"\n入力: {msg}")
        result = handle_message(msg)
        if result:
            print(result)
