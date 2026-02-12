#!/usr/bin/env python3
"""
メディテーションエージェント #43 - Discord連携
"""

import re
from datetime import datetime, timedelta
from db import *

def parse_message(message):
    """メッセージを解析"""
    # 追加
    add_match = re.match(r'(?:瞑想|meditation)[：:]\s*(.+)', message, re.IGNORECASE)
    if add_match:
        return {'action': 'add', 'content': add_match.group(1)}

    # 更新
    update_match = re.match(r'(?:更新|update)[：:]\s*(\d+)\s*(.+)', message, re.IGNORECASE)
    if update_match:
        return {'action': 'update', 'meditation_id': int(update_match.group(1)), 'content': update_match.group(2)}

    # 削除
    delete_match = re.match(r'(?:削除|delete|remove)[：:]\s*(\d+)', message, re.IGNORECASE)
    if delete_match:
        return {'action': 'delete', 'meditation_id': int(delete_match.group(1))}

    # 一覧
    list_match = re.match(r'(?:(?:瞑想|meditation)(?:一覧|list)|list|meditations)', message, re.IGNORECASE)
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

    # 統計
    if message.strip() in ['統計', 'stats', '瞑想統計']:
        return {'action': 'stats'}

    return None

def parse_add(content):
    """追加内容を解析"""
    result = {'date': None, 'time': None, 'duration_minutes': None,
              'meditation_type': None, 'notes': None, 'rating': None}

    # 日付
    date_match = re.search(r'(?:日付|date)[：:]\s*([^、,]+)', content, re.IGNORECASE)
    if date_match:
        result['date'] = parse_date(date_match.group(1).strip())
    else:
        # デフォルトは今日
        result['date'] = datetime.now().strftime("%Y-%m-%d")

    # 時間
    time_match = re.search(r'(?:時間|time|時刻)[：:]?\s*(\d{1,2}[：:]\d{2})', content)
    if time_match:
        result['time'] = time_match.group(1).replace('：', ':')

    # 持続時間
    duration_match = re.search(r'(?:時間|duration|持続)[：:]?\s*(\d+)\s*(分|min|時間|hour)?', content)
    if duration_match:
        result['duration_minutes'] = int(duration_match.group(1))
        if duration_match.group(2) and ('時間' in duration_match.group(2) or 'hour' in duration_match.group(2).lower()):
            result['duration_minutes'] *= 60

    # タイプ
    type_match = re.search(r'(?:タイプ|type|種類)[：:]\s*([^、,]+)', content, re.IGNORECASE)
    if type_match:
        result['meditation_type'] = type_match.group(1).strip()

    # 評価
    rating_match = re.search(r'(?:評価|rating|良さ)[：:]?\s*(\d)', content)
    if rating_match:
        result['rating'] = int(rating_match.group(1))

    # メモ
    notes_match = re.search(r'(?:メモ|memo|note)[：:]\s*(.+)', content)
    if notes_match:
        result['notes'] = notes_match.group(1).strip()

    # タイプがまだない場合、最初の項目より前をタイプとする
    if not result['meditation_type']:
        for key in ['日付', 'date', '時間', 'time', '時刻', '持続', 'duration', '分', 'min', 'メモ', 'memo', 'note', '評価', 'rating', 'タイプ', 'type']:
            match = re.search(rf'{key}[×:：]', content)
            if match:
                result['meditation_type'] = content[:match.start()].strip()
                break
        else:
            result['meditation_type'] = content.strip()

    return result

def parse_update(content):
    """更新内容を解析"""
    result = {}

    # 時間
    time_match = re.search(r'(?:時間|time)[：:]?\s*(\d{1,2}[：:]\d{2})', content)
    if time_match:
        result['time'] = time_match.group(1).replace('：', ':')

    # 持続時間
    duration_match = re.search(r'(?:時間|duration)[：:]?\s*(\d+)', content)
    if duration_match:
        result['duration_minutes'] = int(duration_match.group(1))

    # タイプ
    type_match = re.search(r'(?:タイプ|type)[：:]\s*([^、,]+)', content, re.IGNORECASE)
    if type_match:
        result['meditation_type'] = type_match.group(1).strip()

    # 評価
    rating_match = re.search(r'(?:評価|rating)[：:]?\s*(\d)', content)
    if rating_match:
        result['rating'] = int(rating_match.group(1))

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

        meditation_id = add_meditation(
            content['date'],
            content['time'],
            content['duration_minutes'],
            content['meditation_type'],
            content['notes'],
            content['rating']
        )

        response = f"🧘 瞑想 #{meditation_id} 追加完了\n"
        response += f"日付: {content['date']}\n"
        if content['meditation_type']:
            response += f"タイプ: {content['meditation_type']}\n"
        if content['time']:
            response += f"時間: {content['time']}\n"
        if content['duration_minutes']:
            response += f"持続: {content['duration_minutes']}分\n"
        if content['rating']:
            stars = '⭐' * content['rating']
            response += f"評価: {content['rating']}/5 {stars}\n"
        if content['notes']:
            response += f"メモ: {content['notes']}"

        return response

    elif action == 'update':
        updates = parse_update(parsed['content'])

        if not updates:
            return "❌ 更新内容がありません"

        update_meditation(parsed['meditation_id'], **updates)

        response = f"✅ 瞑想 #{parsed['meditation_id']} 更新完了"

        return response

    elif action == 'delete':
        delete_meditation(parsed['meditation_id'])
        return f"🗑️ 瞑想 #{parsed['meditation_id']} 削除完了"

    elif action == 'list':
        meditations = list_meditations()

        if not meditations:
            return "🧘 瞑想記録がありません"

        response = f"🧘 瞑想記録 ({len(meditations)}件):\n"
        for meditation in meditations:
            response += format_meditation(meditation)

        return response

    elif action == 'today':
        date = datetime.now().strftime("%Y-%m-%d")
        meditations = get_by_date(date)

        if not meditations:
            return "🧘 今日の瞑想はまだありません"

        response = f"🧘 今日の瞑想 ({len(meditations)}件):\n"
        for meditation in meditations:
            response += format_meditation(meditation)

        return response

    elif action == 'yesterday':
        date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        meditations = get_by_date(date)

        if not meditations:
            return "🧘 昨日の瞑想はありません"

        response = f"🧘 昨日の瞑想 ({len(meditations)}件):\n"
        for meditation in meditations:
            response += format_meditation(meditation)

        return response

    elif action == 'this_week':
        week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        meditations = list_meditations(date_from=week_ago)

        if not meditations:
            return "🧘 今週の瞑想はありません"

        response = f"🧘 今週の瞑想 ({len(meditations)}件):\n"
        for meditation in meditations:
            response += format_meditation(meditation)

        return response

    elif action == 'stats':
        stats = get_stats()

        response = "📊 瞑想統計:\n"
        response += f"全記録: {stats['total']}回\n"
        response += f"総時間: {stats['total_hours']}時間 ({stats['total_minutes']}分)\n"
        response += f"今日: {stats['today']}回\n"
        response += f"今月: {stats['this_month']}回\n"
        if stats['week_count'] > 0:
            response += f"今週: {stats['week_count']}回 ({stats['week_minutes']}分)\n"
        if stats['avg_rating']:
            stars = '⭐' * int(stats['avg_rating'])
            response += f"平均評価: {stats['avg_rating']}/5 {stars}"

        return response

    return None

def format_meditation(meditation):
    """瞑想をフォーマット"""
    id, date, time, duration_minutes, meditation_type, notes, rating, created_at = meditation

    response = f"\n🧘 [{id}] {date}"
    if time:
        response += f" {time}"
    response += "\n"

    parts = []
    if meditation_type:
        parts.append(f"タイプ: {meditation_type}")
    if duration_minutes:
        parts.append(f"{duration_minutes}分")
    if rating:
        stars = '⭐' * rating
        parts.append(f"{rating}/5")

    if parts:
        response += f"    {' | '.join(parts)}\n"

    if notes:
        response += f"    📝 {notes}\n"

    return response

if __name__ == '__main__':
    init_db()

    test_messages = [
        "瞑想: 呼吸瞑想, 時間 10, 評価 4",
        "瞑想: マインドフルネス, 時間 15",
        "今日",
        "今週",
        "統計",
    ]

    for msg in test_messages:
        print(f"\n入力: {msg}")
        result = handle_message(msg)
        if result:
            print(result)
