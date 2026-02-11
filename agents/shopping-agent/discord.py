#!/usr/bin/env python3
"""
買い物エージェント #34 - Discord連携
"""

import re
from db import *

def parse_message(message):
    """メッセージを解析"""
    # 商品追加
    item_match = re.match(r'(?:買い物|shopping|買う|買って)[：:]\s*(.+)', message, re.IGNORECASE)
    if item_match:
        return parse_add(item_match.group(1))

    # 更新
    update_match = re.match(r'(?:更新|update)[：:]\s*(\d+)\s*(.+)', message, re.IGNORECASE)
    if update_match:
        return {'action': 'update', 'item_id': int(update_match.group(1)), 'content': update_match.group(2)}

    # 削除
    delete_match = re.match(r'(?:削除|delete|remove)[：:]\s*(\d+)', message, re.IGNORECASE)
    if delete_match:
        return {'action': 'delete', 'item_id': int(delete_match.group(1))}

    # 購入
    purchase_match = re.match(r'(?:購入|bought|buy|done)[：:]\s*(\d+)', message, re.IGNORECASE)
    if purchase_match:
        return {'action': 'purchase', 'item_id': int(purchase_match.group(1))}

    # キャンセル
    cancel_match = re.match(r'(?:キャンセル|cancel)[：:]\s*(\d+)', message, re.IGNORECASE)
    if cancel_match:
        return {'action': 'cancel', 'item_id': int(cancel_match.group(1))}

    # 検索
    search_match = re.match(r'(?:検索|search)[：:]\s*(.+)', message, re.IGNORECASE)
    if search_match:
        return {'action': 'search', 'keyword': search_match.group(1)}

    # 一覧
    list_match = re.match(r'(?:(?:買い物|shopping)(?:一覧|list)|list|items)', message, re.IGNORECASE)
    if list_match:
        return {'action': 'list'}

    # 未購入
    if message.strip() in ['未購入', 'pending', '買い物リスト']:
        return {'action': 'list_pending'}

    # 購入済み
    if message.strip() in ['購入済み', 'purchased', 'bought']:
        return {'action': 'list_purchased'}

    # カテゴリ別
    category_match = re.match(r'(?:カテゴリ|category)[：:]\s*(.+)', message, re.IGNORECASE)
    if category_match:
        return {'action': 'list_by_category', 'category': category_match.group(1)}

    # お店別
    store_match = re.match(r'(?:お店|store|ショップ|shop)[：:]\s*(.+)', message, re.IGNORECASE)
    if store_match:
        return {'action': 'list_by_store', 'store': store_match.group(1)}

    # 統計
    if message.strip() in ['統計', 'stats', '買い物統計']:
        return {'action': 'stats'}

    return None

def parse_add(content):
    """商品追加を解析"""
    result = {'action': 'add', 'name': None, 'category': None, 'price': None, 'quantity': 1,
              'status': 'pending', 'priority': None, 'store': None, 'notes': None}

    # 商品名 (最初の部分)
    name_match = re.match(r'^([^、,（\(【]+)', content)
    if name_match:
        result['name'] = name_match.group(1).strip()

    # カテゴリ
    category_match = re.search(r'(?:カテゴリ|category|種類)[：:]\s*([^、,]+)', content)
    if category_match:
        result['category'] = category_match.group(1).strip()

    # 価格
    price_match = re.search(r'(?:価格|price|値段|￥|¥)[：:]?\s*(\d+)', content)
    if price_match:
        result['price'] = int(price_match.group(1))

    # 数量
    quantity_match = re.search(r'(?:数量|quantity|個)[：:]\s*(\d+)', content)
    if quantity_match:
        result['quantity'] = int(quantity_match.group(1))

    # 優先順位
    priority_match = re.search(r'(?:優先|priority|急ぎ|urgent)[：:]\s*(高|中|低|\d)', content)
    if priority_match:
        priority = priority_match.group(1)
        if priority == '高' or priority == '3' or priority == '急ぎ' or priority == 'urgent':
            result['priority'] = 3
        elif priority == '中' or priority == '2':
            result['priority'] = 2
        elif priority == '低' or priority == '1':
            result['priority'] = 1

    # お店
    store_match = re.search(r'(?:お店|store|ショップ|shop|店)[：:]\s*([^、,]+)', content)
    if store_match:
        result['store'] = store_match.group(1).strip()

    # メモ
    notes_match = re.search(r'(?:メモ|備考|memo|note)[：:]\s*(.+)', content)
    if notes_match:
        result['notes'] = notes_match.group(1).strip()

    # 商品名がまだない場合、最初の項目より前を商品名とする
    if not result['name']:
        for key in ['カテゴリ', 'category', '種類', '価格', 'price', '値段', '￥', '¥',
                    '数量', 'quantity', '個', '優先', 'priority', '急ぎ', 'urgent',
                    'お店', 'store', 'ショップ', 'shop', '店', 'メモ', '備考', 'memo', 'note']:
            match = re.search(rf'{key}[：:]', content)
            if match:
                result['name'] = content[:match.start()].strip()
                break
        else:
            result['name'] = content.strip()

    return result

def parse_update(content):
    """更新内容を解析"""
    result = {}

    # 商品名
    name_match = re.search(r'(?:名前|name|商品名)[：:]\s*([^、,]+)', content)
    if name_match:
        result['name'] = name_match.group(1).strip()

    # カテゴリ
    category_match = re.search(r'(?:カテゴリ|category|種類)[：:]\s*([^、,]+)', content)
    if category_match:
        result['category'] = category_match.group(1).strip()

    # 価格
    price_match = re.search(r'(?:価格|price|値段|￥|¥)[：:]?\s*(\d+)', content)
    if price_match:
        result['price'] = int(price_match.group(1))

    # 数量
    quantity_match = re.search(r'(?:数量|quantity|個)[：:]\s*(\d+)', content)
    if quantity_match:
        result['quantity'] = int(quantity_match.group(1))

    # ステータス
    status_match = re.search(r'(?:ステータス|status|状態)[：:]\s*(未購入|pending|購入済み|purchased|キャンセル|cancelled)', content)
    if status_match:
        status_map = {
            '未購入': 'pending', 'pending': 'pending',
            '購入済み': 'purchased', 'purchased': 'purchased',
            'キャンセル': 'cancelled', 'cancelled': 'cancelled'
        }
        result['status'] = status_map.get(status_match.group(1).lower())

    # 優先順位
    priority_match = re.search(r'(?:優先|priority|急ぎ|urgent)[：:]\s*(高|中|低|\d)', content)
    if priority_match:
        priority = priority_match.group(1)
        if priority == '高' or priority == '3' or priority == '急ぎ' or priority == 'urgent':
            result['priority'] = 3
        elif priority == '中' or priority == '2':
            result['priority'] = 2
        elif priority == '低' or priority == '1':
            result['priority'] = 1

    # お店
    store_match = re.search(r'(?:お店|store|ショップ|shop|店)[：:]\s*([^、,]+)', content)
    if store_match:
        result['store'] = store_match.group(1).strip()

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

    if action == 'add':
        if not parsed['name']:
            return "❌ 商品名を入力してください"

        item_id = add_item(
            parsed['name'],
            parsed['category'],
            parsed['price'],
            parsed['quantity'],
            parsed['status'],
            parsed['priority'],
            parsed['store'],
            parsed['notes']
        )

        response = f"🛒 商品 #{item_id} 追加完了\n"
        response += f"商品名: {parsed['name']}\n"
        if parsed['category']:
            response += f"カテゴリ: {parsed['category']}\n"
        if parsed['price']:
            response += f"価格: ¥{parsed['price']:,}\n"
        if parsed['quantity'] > 1:
            response += f"数量: {parsed['quantity']}\n"
        if parsed['priority']:
            priority_text = ['低', '中', '高'][parsed['priority'] - 1]
            response += f"優先度: {priority_text}\n"
        if parsed['store']:
            response += f"お店: {parsed['store']}\n"
        if parsed['notes']:
            response += f"メモ: {parsed['notes']}"

        return response

    elif action == 'update':
        updates = parse_update(parsed['content'])

        if not updates:
            return "❌ 更新内容がありません"

        update_item(parsed['item_id'], **updates)

        response = f"✅ 商品 #{parsed['item_id']} 更新完了"

        return response

    elif action == 'delete':
        delete_item(parsed['item_id'])
        return f"🗑️ 商品 #{parsed['item_id']} 削除完了"

    elif action == 'purchase':
        update_item(parsed['item_id'], status='purchased')
        return f"✅ 商品 #{parsed['item_id']} 購入完了！"

    elif action == 'cancel':
        update_item(parsed['item_id'], status='cancelled')
        return f"❌ 商品 #{parsed['item_id']} キャンセルしました"

    elif action == 'search':
        keyword = parsed['keyword']
        items = search_items(keyword)

        if not items:
            return f"🔍 「{keyword}」の検索結果: 見つかりませんでした"

        response = f"🔍 「{keyword}」の検索結果 ({len(items)}件):\n"
        for item in items:
            response += format_item(item)

        return response

    elif action == 'list':
        items = list_items()

        if not items:
            return "🛒 商品がありません"

        response = f"🛒 商品一覧 ({len(items)}件):\n"
        for item in items:
            response += format_item(item)

        return response

    elif action == 'list_pending':
        items = list_items(status='pending')

        if not items:
            return "🛒 未購入商品はありません"

        response = f"🛒 未購入商品 ({len(items)}件):\n"
        for item in items:
            response += format_item(item)

        return response

    elif action == 'list_purchased':
        items = list_items(status='purchased')

        if not items:
            return "🛒 購入済み商品はありません"

        response = f"🛒 購入済み商品 ({len(items)}件):\n"
        for item in items:
            response += format_item(item)

        return response

    elif action == 'list_by_category':
        items = list_items(category=parsed['category'])

        if not items:
            return f"🛒 「{parsed['category']}」の商品はありません"

        response = f"🛒 {parsed['category']} ({len(items)}件):\n"
        for item in items:
            response += format_item(item)

        return response

    elif action == 'list_by_store':
        items = list_items(store=parsed['store'])

        if not items:
            return f"🛒 「{parsed['store']}」の商品はありません"

        response = f"🛒 {parsed['store']} ({len(items)}件):\n"
        for item in items:
            response += format_item(item)

        return response

    elif action == 'stats':
        stats = get_stats()

        response = "📊 買い物統計:\n"
        response += f"全商品数: {stats['total']}件\n"
        response += f"未購入: {stats['pending']}件\n"
        response += f"購入済み: {stats['purchased']}件\n"
        if stats['pending_amount'] > 0:
            response += f"未購入総額: ¥{stats['pending_amount']:,}\n"
        if stats['total_amount'] > 0:
            response += f"総額: ¥{stats['total_amount']:,}"

        return response

    return None

def format_item(item):
    """商品をフォーマット"""
    id, name, category, price, quantity, status, priority, store, notes, created_at, purchased_at = item

    # ステータス表示
    status_icons = {'pending': '⏳', 'purchased': '✅', 'cancelled': '❌'}
    status_icon = status_icons.get(status, '❓')

    # 優先度表示
    priority_icons = ["", "🟢", "🟡", "🔴"]
    priority_icon = priority_icons[priority] if priority else ""

    response = f"\n{status_icon} [{id}] {name} {priority_icon}\n"

    parts = []
    if category:
        parts.append(f"📁 {category}")
    if price:
        if quantity > 1:
            parts.append(f"¥{price:,}×{quantity}")
        else:
            parts.append(f"¥{price:,}")
    if store:
        parts.append(f"🏪 {store}")

    if parts:
        response += f"    {' '.join(parts)}\n"

    if notes:
        response += f"    📝 {notes}\n"

    return response

if __name__ == '__main__':
    # テスト
    init_db()

    test_messages = [
        "買い物: 牛乳, カテゴリ: 食料品, 価格: 200",
        "買い物: 新しいパソコン, カテゴリ: 電子機器, 価格: 150000, 優先: 高",
        "購入: 1",
        "未購入",
        "検索: 食料品",
        "統計",
    ]

    for msg in test_messages:
        print(f"\n入力: {msg}")
        result = handle_message(msg)
        if result:
            print(result)
