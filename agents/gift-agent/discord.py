#!/usr/bin/env python3
"""
ギフト記録エージェント #66 - Discord連携
"""

import re
from datetime import datetime
from db import *

def parse_message(message):
    """メッセージを解析"""
    # ギフト追加
    gift_match = re.match(r'(?:ギフト|gift)[：:]\\s*(.+)', message, re.IGNORECASE)
    if gift_match:
        return parse_gift(gift_match.group(1))

    # ギフトアイデア追加
    idea_match = re.match(r'(?:アイデア|idea)[：:]\\s*(.+)', message, re.IGNORECASE)
    if idea_match:
        return parse_gift_idea(idea_match.group(1))

    # ギフト一覧
    if message.strip() in ['ギフト一覧', 'ギフト', 'gifts', 'gift list']:
        return {'action': 'list_gifts'}

    # アイデア一覧
    if message.strip() in ['アイデア一覧', 'アイデア', 'ideas', 'idea list']:
        return {'action': 'list_ideas'}

    # 統計
    if message.strip() in ['統計', 'stats', 'ギフト統計']:
        return {'action': 'stats'}

    return None

def parse_gift(content):
    """ギフト情報を解析"""
    result = {'action': 'add_gift', 'type': None, 'item_name': None, 'recipient_name': None, 'sender_name': None, 'occasion': None, 'date': None, 'price': None, 'notes': None, 'tags': None}

    # タイプ
    if 'もらった' in content or 'received' in content or '貰った' in content:
        result['type'] = 'received'
    elif 'あげた' in content or 'given' in content or '贈った' in content:
        result['type'] = 'given'
    else:
        result['type'] = 'received'  # デフォルト

    # アイテム名（最初の項目）
    item_match = re.search(r'^([^、,タイプ]+)', content)
    if item_match:
        result['item_name'] = item_match.group(1).strip()

    # 受取人/送り主
    if result['type'] == 'given':
        to_match = re.search(r'(?:宛|to|相手)[：:]\\s*([^、,機会]+)', content, re.IGNORECASE)
        if to_match:
            result['recipient_name'] = to_match.group(1).strip()
    else:
        from_match = re.search(r'(?:から|from|送り主)[：:]\\s*([^、,機会]+)', content, re.IGNORECASE)
        if from_match:
            result['sender_name'] = from_match.group(1).strip()

    # 機会
    occasion_match = re.search(r'(?:機会|occasion|理由)[：:]\\s*([^、,金額]+)', content, re.IGNORECASE)
    if occasion_match:
        result['occasion'] = occasion_match.group(1).strip()

    # 金額
    price_match = re.search(r'(?:金額|price|値段)[：:]\\s*(\\d+)', content, re.IGNORECASE)
    if price_match:
        result['price'] = float(price_match.group(1))

    # 日付
    date_match = re.search(r'(?:日付|date)[：:]\\s*(\\d{4}-\\d{2}-\\d{2}|\\d{4}/\\d{2}/\\d{2})', content, re.IGNORECASE)
    if date_match:
        result['date'] = date_match.group(1).replace('/', '-')

    # タグ
    tags_match = re.search(r'(?:タグ|tags?)[：:]\\s*(.+)', content, re.IGNORECASE)
    if tags_match:
        result['tags'] = tags_match.group(1).strip()

    # メモ
    notes_match = re.search(r'(?:メモ|memo|note)[：:]\\s*(.+)', content, re.IGNORECASE)
    if notes_match:
        result['notes'] = notes_match.group(1).strip()

    return result

def parse_gift_idea(content):
    """ギフトアイデアを解析"""
    result = {'action': 'add_idea', 'target_name': None, 'item_name': None, 'category': None, 'priority': 3, 'notes': None}

    # ターゲット名（最初の項目）
    target_match = re.search(r'^([^、,アイテム]+)', content)
    if target_match:
        result['target_name'] = target_match.group(1).strip()

    # アイテム
    item_match = re.search(r'(?:アイテム|item|物)[：:]\\s*([^、,カテゴリ]+)', content, re.IGNORECASE)
    if item_match:
        result['item_name'] = item_match.group(1).strip()
    elif not result['item_name']:
        # ターゲットの次がアイテムと仮定
        after_target = re.sub(r'^([^、,]+)[、,]', '', content)
        item_from_rest = re.match(r'^([^、,カテゴリ]+)', after_target)
        if item_from_rest:
            result['item_name'] = item_from_rest.group(1).strip()

    # カテゴリ
    cat_match = re.search(r'(?:カテゴリ|category)[：:]\\s*([^、,優先度]+)', content, re.IGNORECASE)
    if cat_match:
        result['category'] = cat_match.group(1).strip()

    # 優先度
    priority_match = re.search(r'(?:優先度|priority)[：:]\\s*(\\d+)', content, re.IGNORECASE)
    if priority_match:
        result['priority'] = int(priority_match.group(1))
        result['priority'] = max(1, min(5, result['priority']))

    # メモ
    notes_match = re.search(r'(?:メモ|memo|note)[：:]\\s*(.+)', content, re.IGNORECASE)
    if notes_match:
        result['notes'] = notes_match.group(1).strip()

    return result

def handle_message(message):
    """メッセージを処理"""
    parsed = parse_message(message)

    if not parsed:
        return None

    action = parsed['action']

    if action == 'add_gift':
        if not parsed['item_name']:
            return "❌ ギフトのアイテム名を入力してください"

        gift_id = add_gift(
            parsed['type'],
            parsed['item_name'],
            parsed['recipient_name'],
            parsed['sender_name'],
            parsed['occasion'],
            parsed['date'],
            parsed['price'],
            parsed['notes'],
            parsed['tags']
        )

        type_text = {'given': 'あげた', 'received': 'もらった'}.get(parsed['type'], '')
        response = f"🎁 ギフト #{gift_id} 追加完了\n"
        response += f"タイプ: {type_text}\n"
        response += f"アイテム: {parsed['item_name']}"
        if parsed['recipient_name']:
            response += f"\n宛先: {parsed['recipient_name']}"
        if parsed['sender_name']:
            response += f"\n送り主: {parsed['sender_name']}"
        if parsed['occasion']:
            response += f"\n機会: {parsed['occasion']}"
        if parsed['date']:
            response += f"\n日付: {parsed['date']}"
        if parsed['price']:
            response += f"\n金額: ¥{parsed['price']:,.0f}"
        if parsed['tags']:
            response += f"\nタグ: {parsed['tags']}"
        if parsed['notes']:
            response += f"\nメモ: {parsed['notes']}"

        return response

    elif action == 'add_idea':
        if not parsed['target_name'] or not parsed['item_name']:
            return "❌ ターゲット名とアイテム名を入力してください"

        idea_id = add_gift_idea(
            parsed['target_name'],
            parsed['item_name'],
            parsed['category'],
            parsed['priority'],
            parsed['notes']
        )

        stars = '⭐' * parsed['priority']
        response = f"💡 ギフトアイデア #{idea_id} 追加完了\n"
        response += f"ターゲット: {parsed['target_name']}\n"
        response += f"アイテム: {parsed['item_name']}\n"
        response += f"優先度: {parsed['priority']}/5 {stars}"
        if parsed['category']:
            response += f"\nカテゴリ: {parsed['category']}"
        if parsed['notes']:
            response += f"\nメモ: {parsed['notes']}"

        return response

    elif action == 'list_gifts':
        gifts = list_gifts(limit=20)

        if not gifts:
            return "🎁 ギフト記録がありません"

        response = f"🎁 ギフト記録 ({len(gifts)}件):\n"
        for gift in gifts:
            response += format_gift(gift)

        return response

    elif action == 'list_ideas':
        ideas = list_gift_ideas(limit=20)

        if not ideas:
            return "💡 ギフトアイデアがありません"

        response = f"💡 ギフトアイデア ({len(ideas)}件):\n"
        for idea in ideas:
            response += format_gift_idea(idea)

        return response

    elif action == 'stats':
        stats = get_stats()

        response = "📊 ギフト統計:\n"
        by_type = stats.get('by_type', {})
        if 'given' in by_type:
            response += f"あげた: {by_type['given']}件\n"
        if 'received' in by_type:
            response += f"もらった: {by_type['received']}件\n"
        response += f"今年: {stats.get('this_year', 0)}件\n"
        response += f"アイデア: {stats.get('idea_count', 0)}件"

        return response

    return None

def format_gift(gift):
    """ギフト記録をフォーマット"""
    id, gift_type, item_name, recipient_name, sender_name, occasion, date, price, notes, tags, created_at = gift

    type_icon = {'given': '📤', 'received': '📥'}.get(gift_type, '🎁')
    type_text = {'given': 'あげた', 'received': 'もらった'}.get(gift_type, '')

    response = f"\n{type_icon} [{id}] {type_text} - {item_name}"
    if recipient_name:
        response += f"\n    宛先: {recipient_name}"
    if sender_name:
        response += f"\n    送り主: {sender_name}"
    if occasion:
        response += f"\n    機会: {occasion}"
    if date:
        response += f"\n    日付: {date}"
    if price:
        response += f"\n    金額: ¥{price:,.0f}"
    if tags:
        response += f"\n    タグ: {tags}"
    if notes:
        response += f"\n    メモ: {notes}"
    response += f"\n    登録日: {created_at}"

    return response

def format_gift_idea(idea):
    """ギフトアイデアをフォーマット"""
    id, target_name, item_name, category, priority, notes, status, created_at = idea

    stars = '⭐' * priority
    status_text = {'idea': '💡', 'planned': '📋', 'purchased': '🛒', 'given': '🎁'}.get(status, '💡')

    response = f"\n{status_text} [{id}] {target_name}: {item_name}"
    response += f"\n    優先度: {priority}/5 {stars}"
    if category:
        response += f"\n    カテゴリ: {category}"
    if status != 'idea':
        response += f"\n    状態: {status}"
    if notes:
        response += f"\n    メモ: {notes}"
    response += f"\n    登録日: {created_at}"

    return response

if __name__ == '__main__':
    init_db()

    test_messages = [
        "ギフト: 誕生日ケーキ, 宛: 田中さん, 機会: 誕生日, 金額: 3000",
        "ギフト: ネクタイ, あげた, 宛: 鈴木さん, 機会: 父の日",
        "アイデア: 母, 花束, カテゴリ: 花, 優先度: 5",
        "ギフト一覧",
        "アイデア一覧",
    ]

    for msg in test_messages:
        print(f"\n入力: {msg}")
        result = handle_message(msg)
        if result:
            print(result)
