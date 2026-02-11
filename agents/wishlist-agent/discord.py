#!/usr/bin/env python3
"""
Wishlist Agent #22 - Discord Integration
"""

import re
from db import *

def parse_message(message):
    """Parse message"""
    # Add item
    add_match = re.match(r'(?:追加|add)[:：]\s*(.+)', message, re.IGNORECASE)
    if add_match:
        return parse_add(add_match.group(1))

    # Mark acquired
    acquire_match = re.match(r'(?:取得|acquired)[:：]\s*(\d+)', message, re.IGNORECASE)
    if acquire_match:
        return {'action': 'acquire', 'item_id': int(acquire_match.group(1))}

    # Update status
    status_match = re.match(r'(?:ステータス|status)[:：]\s*(\d+)\s*[,，]\s*(\w+)', message, re.IGNORECASE)
    if status_match:
        return {'action': 'update_status', 'item_id': int(status_match.group(1)), 'status': status_match.group(2)}

    # List
    list_match = re.match(r'(?:一覧|list)(?:[:：]\s*(\w+))?', message, re.IGNORECASE)
    if list_match:
        status = list_match.group(1) if list_match.group(1) else None
        return {'action': 'list', 'status': status}

    # Search
    search_match = re.match(r'(?:検索|search)[:：]\s*(.+)', message, re.IGNORECASE)
    if search_match:
        return {'action': 'search', 'keyword': search_match.group(1)}

    # Delete
    delete_match = re.match(r'(?:削除|delete)[:：]\s*(\d+)', message, re.IGNORECASE)
    if delete_match:
        return {'action': 'delete', 'item_id': int(delete_match.group(1))}

    # Stats
    if message.strip() in ['統計', 'stats']:
        return {'action': 'stats'}

    return None

def parse_add(content):
    """Parse add content"""
    result = {'action': 'add', 'name': None, 'description': None, 'category': None, 'price': None, 'url': None, 'priority': None, 'notes': None}

    # Name
    name_match = re.match(r'^([^、,]+)', content)
    if name_match:
        result['name'] = name_match.group(1).strip()

    # Category
    cat_match = re.search(r'カテゴリ[:：]\s*(.+?)(?:[、,]|$)', content)
    if cat_match:
        result['category'] = cat_match.group(1).strip()

    # Price
    price_match = re.search(r'価格[:：]\s*(\d+)', content)
    if price_match:
        result['price'] = float(price_match.group(1))

    # URL
    url_match = re.search(r'https?://[^\s、,]+', content)
    if url_match:
        result['url'] = url_match.group(0).strip()

    # Priority
    pri_match = re.search(r'優先[:：]\s*(\d)', content)
    if pri_match:
        result['priority'] = int(pri_match.group(1))

    # Description
    desc_match = re.search(r'説明[:：]\s*(.+)', content)
    if desc_match:
        result['description'] = desc_match.group(1).strip()

    # Notes
    note_match = re.search(r'メモ[:：]\s*(.+)', content)
    if note_match:
        result['notes'] = note_match.group(1).strip()

    return result

def handle_message(message):
    """Handle message"""
    parsed = parse_message(message)

    if not parsed:
        return None

    action = parsed['action']

    if action == 'add':
        if not parsed['name']:
            return "❌ 名前を入力してください"

        item_id = add_item(
            parsed['name'],
            parsed['description'],
            parsed['category'],
            parsed['price'],
            parsed['url'],
            parsed['priority'],
            parsed['notes']
        )

        response = f"✅ アイテム #{item_id} 追加完了\n"
        response += f"名前: {parsed['name']}\n"
        if parsed['category']:
            response += f"カテゴリ: {parsed['category']}\n"
        if parsed['price']:
            response += f"価格: ¥{parsed['price']}\n"
        if parsed['url']:
            response += f"URL: {parsed['url']}"

        return response

    elif action == 'acquire':
        mark_acquired(parsed['item_id'])
        return f"🎉 アイテム #{parsed['item_id']} を取得！"

    elif action == 'update_status':
        status_map = {'wanted': 'wanted', 'acquired': 'acquired', 'abandoned': 'abandoned'}
        status = status_map.get(parsed['status'].lower(), parsed['status'])
        update_status(parsed['item_id'], status)
        return f"✅ アイテム #{parsed['item_id']} のステータスを {status} に更新"

    elif action == 'list':
        items = list_items(status=parsed['status'])

        if not items:
            return f"📋 アイテムがありません"

        status_text = f" ({parsed['status']})" if parsed['status'] else ""
        response = f"📋 一覧{status_text} ({len(items)}件):\n"
        for item in items:
            response += format_item(item)

        return response

    elif action == 'search':
        items = search_items(parsed['keyword'])

        if not items:
            return f"🔍 「{parsed['keyword']}」の検索結果: 見つかりませんでした"

        response = f"🔍 「{parsed['keyword']}」の検索結果 ({len(items)}件):\n"
        for item in items:
            response += format_item(item)

        return response

    elif action == 'delete':
        delete_item(parsed['item_id'])
        return f"🗑️ アイテム #{parsed['item_id']} を削除"

    elif action == 'stats':
        stats = get_stats()

        response = "📊 統計:\n"
        response += f"全アイテム: {stats['total']}件\n"
        response += f"欲しい: {stats['wanted']}件\n"
        response += f"取得済み: {stats['acquired']}件\n"
        response += f"諦めた: {stats['abandoned']}件\n"
        if stats['total_price'] > 0:
            response += f"合計価格: ¥{int(stats['total_price']):,}"

        return response

    return None

def format_item(item):
    """Format item"""
    id, name, description, category, price, url, priority, status, notes, created_at, updated_at = item

    status_map = {'wanted': '🎁', 'acquired': '✅', 'abandoned': '❌'}
    status_icon = status_map.get(status, '❓')

    response = f"\n{status_icon} [{id}] {name}\n"
    if category:
        response += f"    カテゴリ: {category}\n"
    if price:
        response += f"    価格: ¥{int(price):,}\n"

    return response

if __name__ == '__main__':
    init_db()

    test_messages = [
        "追加: 新しいガジェット, カテゴリ: 電子機器, 価格: 15000",
        "追加: 本, カテゴリ: 本",
        "一覧",
        "一覧: wanted",
        "取得: 1",
        "検索: ガジェット",
        "統計",
    ]

    for msg in test_messages:
        print(f"\n入力: {msg}")
        result = handle_message(msg)
        if result:
            print(result)
