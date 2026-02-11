#!/usr/bin/env python3
"""
Inventory Agent #24 - Discord Integration
"""

import re
from db import *

def parse_message(message):
    """Parse message"""
    # Add item
    add_match = re.match(r'(?:追加|add)[:：]\s*(.+)', message, re.IGNORECASE)
    if add_match:
        return parse_add(add_match.group(1))

    # Update quantity
    qty_match = re.match(r'(?:在庫|quantity|qty)[:：]\s*(\d+)\s*[,，]\s*(-?\d+)', message, re.IGNORECASE)
    if qty_match:
        return {'action': 'update_quantity', 'item_id': int(qty_match.group(1)), 'quantity': int(qty_match.group(2))}

    # Adjust stock
    adjust_match = re.match(r'(?:調整|adjust)[:：]\s*(\d+)\s*[,，]\s*(-?\d+)', message, re.IGNORECASE)
    if adjust_match:
        return {'action': 'adjust_stock', 'item_id': int(adjust_match.group(1)), 'change': int(adjust_match.group(2))}

    # List
    list_match = re.match(r'(?:一覧|list)(?:[:：]\s*(\w+))?', message, re.IGNORECASE)
    if list_match:
        category = list_match.group(1) if list_match.group(1) else None
        return {'action': 'list', 'category': category}

    # Search
    search_match = re.match(r'(?:検索|search)[:：]\s*(.+)', message, re.IGNORECASE)
    if search_match:
        return {'action': 'search', 'keyword': search_match.group(1)}

    # Low stock
    if message.strip() in ['残り少ない', 'low', 'low_stock']:
        return {'action': 'low_stock'}

    # Stats
    if message.strip() in ['統計', 'stats']:
        return {'action': 'stats'}

    return None

def parse_add(content):
    """Parse add content"""
    result = {'action': 'add', 'name': None, 'description': None, 'category': None, 'sku': None, 'quantity': 0, 'unit': None, 'location': None, 'min_stock': 0, 'cost_price': None, 'sell_price': None}

    # Name
    name_match = re.match(r'^([^、,]+)', content)
    if name_match:
        result['name'] = name_match.group(1).strip()

    # Quantity
    qty_match = re.search(r'数量[:：]\s*(\d+)', content)
    if qty_match:
        result['quantity'] = int(qty_match.group(1))

    # Category
    cat_match = re.search(r'カテゴリ[:：]\s*(.+?)(?:[、,]|$)', content)
    if cat_match:
        result['category'] = cat_match.group(1).strip()

    # SKU
    sku_match = re.search(r'SKU[:：]\s*(\w+)', content)
    if sku_match:
        result['sku'] = sku_match.group(1)

    # Location
    loc_match = re.search(r'場所|ロケーション[:：]\s*(.+?)(?:[、,]|$)', content)
    if loc_match:
        result['location'] = loc_match.group(1).strip()

    # Unit
    unit_match = re.search(r'単位[:：]\s*(.+?)(?:[、,]|$)', content)
    if unit_match:
        result['unit'] = unit_match.group(1).strip()

    # Min stock
    min_match = re.search(r'最小在庫|min[:：]\s*(\d+)', content)
    if min_match:
        result['min_stock'] = int(min_match.group(1))

    # Cost price
    cost_match = re.search(r'(?:原価|cost)[:：]\s*(\d+)', content)
    if cost_match:
        result['cost_price'] = float(cost_match.group(1))

    # Sell price
    sell_match = re.search(r'(?:売価|price)[:：]\s*(\d+)', content)
    if sell_match:
        result['sell_price'] = float(sell_match.group(1))

    # Description
    desc_match = re.search(r'説明[:：]\s*(.+)', content)
    if desc_match:
        result['description'] = desc_match.group(1).strip()

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
            parsed['sku'],
            parsed['quantity'],
            parsed['unit'],
            parsed['location'],
            parsed['min_stock'],
            parsed['cost_price'],
            parsed['sell_price']
        )

        response = f"✅ アイテム #{item_id} 追加完了\n"
        response += f"名前: {parsed['name']}\n"
        if parsed['category']:
            response += f"カテゴリ: {parsed['category']}\n"
        response += f"数量: {parsed['quantity']}"
        if parsed['unit']:
            response += f" {parsed['unit']}"

        return response

    elif action == 'update_quantity':
        update_quantity(parsed['item_id'], parsed['quantity'])
        return f"📦 アイテム #{parsed['item_id']} の数量を {parsed['quantity']} に更新"

    elif action == 'adjust_stock':
        change = parsed['change']
        adjust_stock(parsed['item_id'], change)
        action_text = "追加" if change > 0 else "減算"
        return f"📦 アイテム #{parsed['item_id']} に {abs(change)} {action_text}"

    elif action == 'list':
        items = list_items(category=parsed['category'])

        if not items:
            return f"📦 アイテムがありません"

        category_text = f" ({parsed['category']})" if parsed['category'] else ""
        response = f"📦 一覧{category_text} ({len(items)}件):\n"
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

    elif action == 'low_stock':
        items = get_low_stock_items()

        if not items:
            return "✅ 在庫不足のアイテムはありません"

        response = f"⚠️ 在庫不足アイテム ({len(items)}件):\n"
        for item in items:
            response += format_item(item)

        return response

    elif action == 'stats':
        stats = get_stats()

        response = "📊 在庫統計:\n"
        response += f"全アイテム: {stats['total_items']}件\n"
        response += f"総数量: {stats['total_quantity']}\n"
        response += f"在庫不足: {stats['low_stock_count']}件\n"
        if stats['total_value'] > 0:
            response += f"総価値: ¥{int(stats['total_value']):,}"

        return response

    return None

def format_item(item):
    """Format item"""
    id, name, description, category, sku, quantity, unit, location, min_stock, cost_price, sell_price, status, created_at = item

    # Low stock warning
    warning = " ⚠️" if quantity < min_stock else ""

    response = f"\n📦 [{id}] {name}{warning}\n"
    response += f"    数量: {quantity}"
    if unit:
        response += f" {unit}"
    if min_stock > 0:
        response += f" (最小: {min_stock})"
    response += "\n"

    if category:
        response += f"    カテゴリ: {category}\n"
    if location:
        response += f"    場所: {location}\n"
    if cost_price:
        response += f"    原価: ¥{int(cost_price):,}\n"

    return response

if __name__ == '__main__':
    init_db()

    test_messages = [
        "追加: ノートPC, カテゴリ: 電子機器, 数量: 5, 最小: 2, 原価: 80000",
        "追加: マウス, カテゴリ: 周辺機器, 数量: 20, 最小: 5",
        "一覧",
        "在庫: 1, 10",
        "調整: 1, -3",
        "検索: ノート",
        "残り少ない",
        "統計",
    ]

    for msg in test_messages:
        print(f"\n入力: {msg}")
        result = handle_message(msg)
        if result:
            print(result)
