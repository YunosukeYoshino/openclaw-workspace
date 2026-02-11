#!/usr/bin/env python3
"""
グラティチュードエージェント #44 - Discord連携
"""

import re
from datetime import datetime, timedelta
from db import *

def parse_message(message):
    """メッセージを解析"""
    # 追加
    add_match = re.match(r'(?:感謝|gratitude|thank)[：:]\s*(.+)', message, re.IGNORECASE)
    if add_match:
        return {'action': 'add', 'content': add_match.group(1)}

    # 複数追加
    multi_match = re.match(r'(?:感謝|gratitude|thank)[：:]?\s*(.+)、\s*(.+)、\s*(.+)', message)
    if multi_match:
        return {'action': 'add_multi', 'items': [
            multi_match.group(1).strip(),
            multi_match.group(2).strip(),
            multi_match.group(3).strip()
        ]}

    # 更新
    update_match = re.match(r'(?:更新|update)[：:]\s*(\d+)\s*(.+)', message, re.IGNORECASE)
    if update_match:
        return {'action': 'update', 'gratitude_id': int(update_match.group(1)), 'content': update_match.group(2)}

    # 削除
    delete_match = re.match(r'(?:削除|delete|remove)[：:]\s*(\d+)', message, re.IGNORECASE)
    if delete_match:
        return {'action': 'delete', 'gratitude_id': int(delete_match.group(1))}

    # 検索
    search_match = re.match(r'(?:検索|search)[：:]\s*(.+)', message, re.IGNORECASE)
    if search_match:
        return {'action': 'search', 'keyword': search_match.group(1)}

    # 一覧
    list_match = re.match(r'(?:(?:感謝|gratitude|thank)(?:一覧|list)|list|thanks)', message, re.IGNORECASE)
    if list_match:
        return {'action': 'list'}

    # 今日
    if message.strip() in ['今日', 'today']:
        return {'action': 'today'}

    # 昨日
    if message.strip() in ['昨日', 'yesterday']:
        return {'action': 'yesterday'}

    # 今週
    if message.strip() in ['今週', 'this week']:
        return {'action': 'this_week'}

    # カテゴリ
    if message.strip() in ['カテゴリ', 'categories']:
        return {'action': 'categories'}

    # 統計
    if message.strip() in ['統計', 'stats', '感謝統計']:
        return {'action': 'stats'}

    return None

def parse_add(content):
    """追加内容を解析"""
    result = {'date': None, 'item': None, 'category': None, 'notes': None}

    # 日付
    date_match = re.search(r'(?:日付|date)[：:]\s*([^、,]+)', content, re.IGNORECASE)
    if date_match:
        result['date'] = parse_date(date_match.group(1).strip())
    else:
        # デフォルトは今日
        result['date'] = datetime.now().strftime("%Y-%m-%d")

    # アイテム (最初の項目より前)
    for key in ['カテゴリ', 'category', 'メモ', 'memo', 'note']:
        match = re.search(rf'{key}[×:：]', content)
        if match:
            result['item'] = content[:match.start()].strip()
            break
    else:
        result['item'] = content.strip()

    # カテゴリ
    category_match = re.search(r'(?:カテゴリ|category)[：:]\s*([^、,]+)', content, re.IGNORECASE)
    if category_match:
        result['category'] = category_match.group(1).strip()

    # メモ
    notes_match = re.search(r'(?:メモ|memo|note)[：:]\s*(.+)', content)
    if notes_match:
        result['notes'] = notes_match.group(1).strip()

    return result

def parse_update(content):
    """更新内容を解析"""
    result = {}

    # 日付
    date_match = re.search(r'(?:日付|date)[：:]\s*([^、,]+)', content, re.IGNORECASE)
    if date_match:
        result['date'] = parse_date(date_match.group(1).strip())

    # アイテム
    item_match = re.search(r'(?:アイテム|item|感謝)[：:]\s*(.+)', content, re.IGNORECASE)
    if item_match:
        result['item'] = item_match.group(1).strip()

    # カテゴリ
    category_match = re.search(r'(?:カテゴリ|category)[：:]\s*([^、,]+)', content, re.IGNORECASE)
    if category_match:
        result['category'] = category_match.group(1).strip()

    # メモ
    notes_match = re.search(r'(?:メモ|memo|note)[：:]\s*(.+)', content)
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
        return (today - timedelta(days=1)).strftime("%Y-%m-%d")

    # 日付形式
    date_match = re.match(r'(\d{4})-(\d{1,2})-(\d{1,2})', date_str)
    if date_match:
        return f"{date_match.group(1)}-{date_match.group(2).zfill(2)}-{date_match.group(3).zfill(2)}"

    date_match = re.match(r'(\d{1,2})/(\d{1,2})', date_str)
    if date_match:
        month = int(date_match.group(1))
        day = int(date_match.group(2))
        return datetime(today.year, month, day).strftime("%Y-%m-%d")

    return None

def handle_message(message):
    """メッセージを処理"""
    parsed = parse_message(message)

    if not parsed:
        return None

    action = parsed['action']

    if action == 'add':
        content = parse_add(parsed['content'])

        if not content['item']:
            return "❌ 感謝する内容を入力してください"

        gratitude_id = add_gratitude(
            content['date'],
            content['item'],
            content['category'],
            content['notes']
        )

        response = f"🙏 感謝 #{gratitude_id} 追加完了\n"
        response += f"日付: {content['date']}\n"
        response += f"感謝: {content['item']}\n"
        if content['category']:
            response += f"カテゴリ: {content['category']}\n"
        if content['notes']:
            response += f"メモ: {content['notes']}"

        return response

    elif action == 'add_multi':
        date = datetime.now().strftime("%Y-%m-%d")
        ids = []
        for item in parsed['items']:
            gratitude_id = add_gratitude(date, item)
            ids.append(gratitude_id)

        response = f"🙏 {len(parsed['items'])}件の感謝を追加しました\n"
        for i, item in enumerate(parsed['items'], 1):
            response += f"{i}. {item} (#{ids[i-1]})\n"

        return response

    elif action == 'update':
        updates = parse_update(parsed['content'])

        if not updates:
            return "❌ 更新内容がありません"

        update_gratitude(parsed['gratitude_id'], **updates)

        response = f"✅ 感謝 #{parsed['gratitude_id']} 更新完了"

        return response

    elif action == 'delete':
        delete_gratitude(parsed['gratitude_id'])
        return f"🗑️ 感謝 #{parsed['gratitude_id']} 削除完了"

    elif action == 'search':
        keyword = parsed['keyword']
        gratitude_list = search_gratitude(keyword)

        if not gratitude_list:
            return f"🔍 「{keyword}」の検索結果: 見つかりませんでした"

        response = f"🔍 「{keyword}」の検索結果 ({len(gratitude_list)}件):\n"
        for gratitude in gratitude_list:
            response += format_gratitude(gratitude)

        return response

    elif action == 'list':
        gratitude_list = list_gratitude()

        if not gratitude_list:
            return "🙏 感謝日記がありません"

        response = f"🙏 感謝日記 ({len(gratitude_list)}件):\n"
        for gratitude in gratitude_list:
            response += format_gratitude(gratitude)

        return response

    elif action == 'today':
        date = datetime.now().strftime("%Y-%m-%d")
        gratitude_list = get_by_date(date)

        if not gratitude_list:
            return f"🙏 今日の感謝はまだありません"

        response = f"🙏 今日の感謝 ({len(gratitude_list)}件):\n"
        for gratitude in gratitude_list:
            response += format_gratitude(gratitude, show_date=False)

        return response

    elif action == 'yesterday':
        date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        gratitude_list = get_by_date(date)

        if not gratitude_list:
            return f"🙏 昨日の感謝はありません"

        response = f"🙏 昨日の感謝 ({len(gratitude_list)}件):\n"
        for gratitude in gratitude_list:
            response += format_gratitude(gratitude, show_date=False)

        return response

    elif action == 'this_week':
        week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        gratitude_list = list_gratitude(date_from=week_ago)

        if not gratitude_list:
            return f"🙏 今週の感謝はありません"

        response = f"🙏 今週の感謝 ({len(gratitude_list)}件):\n"
        for gratitude in gratitude_list:
            response += format_gratitude(gratitude)

        return response

    elif action == 'categories':
        categories = get_categories()

        if not categories:
            return "🙏 カテゴリがありません"

        response = "📁 カテゴリ一覧:\n"
        for category, count in categories:
            response += f"  • {category} ({count}件)\n"

        return response

    elif action == 'stats':
        stats = get_stats()

        response = "📊 感謝統計:\n"
        response += f"全記録: {stats['total']}件\n"
        response += f"記録日数: {stats['total_days']}日\n"
        response += f"今日: {stats['today']}件\n"
        response += f"今週: {stats['this_week']}件\n"
        response += f"今月: {stats['this_month']}件"

        return response

    return None

def format_gratitude(gratitude, show_date=True):
    """感謝をフォーマット"""
    id, date, item, category, notes, created_at = gratitude

    response = ""
    if show_date:
        response = f"\n🙏 [{id}] {date}\n"
        response += f"    {item}\n"
    else:
        response = f"\n🙏 [{id}] {item}\n"

    if category:
        response += f"    📁 {category}\n"

    return response

if __name__ == '__main__':
    init_db()

    test_messages = [
        "感謝: 家族、仕事、健康",
        "感謝: 美しい天気, カテゴリ: 自然",
        "今日",
        "今週",
        "統計",
    ]

    for msg in test_messages:
        print(f"\n入力: {msg}")
        result = handle_message(msg)
        if result:
            print(result)
