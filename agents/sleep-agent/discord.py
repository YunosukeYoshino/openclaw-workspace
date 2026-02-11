#!/usr/bin/env python3
"""
スリープエージェント #42 - Discord連携
"""

import re
from datetime import datetime, timedelta
from db import *

def parse_message(message):
    """メッセージを解析"""
    # 追加
    add_match = re.match(r'(?:睡眠|sleep)[：:]\s*(.+)', message, re.IGNORECASE)
    if add_match:
        return {'action': 'add', 'content': add_match.group(1)}

    # 更新
    update_match = re.match(r'(?:更新|update)[：:]\s*(\d+)\s*(.+)', message, re.IGNORECASE)
    if update_match:
        return {'action': 'update', 'sleep_id': int(update_match.group(1)), 'content': update_match.group(2)}

    # 削除
    delete_match = re.match(r'(?:削除|delete|remove)[：:]\s*(\d+)', message, re.IGNORECASE)
    if delete_match:
        return {'action': 'delete', 'sleep_id': int(delete_match.group(1))}

    # 一覧
    list_match = re.match(r'(?:(?:睡眠|sleep)(?:一覧|list)|list|sleeps)', message, re.IGNORECASE)
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
    if message.strip() in ['統計', 'stats', '睡眠統計']:
        return {'action': 'stats'}

    return None

def parse_add(content):
    """追加内容を解析"""
    result = {'date': None, 'bed_time': None, 'wake_time': None, 'duration_hours': None,
              'quality': None, 'mood': None, 'notes': None}

    # 日付
    date_match = re.search(r'(?:日付|date)[：:]\s*([^、,]+)', content, re.IGNORECASE)
    if date_match:
        result['date'] = parse_date(date_match.group(1).strip())
    else:
        # デフォルトは昨日
        result['date'] = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

    # 就寝時刻
    bed_match = re.search(r'(?:就寝|bed|就寝時刻)[：:]?\s*(\d{1,2}[：:]\d{2})', content)
    if bed_match:
        result['bed_time'] = bed_match.group(1).replace('：', ':')

    # 起床時刻
    wake_match = re.search(r'(?:起床|wake|起床時刻)[：:]?\s*(\d{1,2}[：:]\d{2})', content)
    if wake_match:
        result['wake_time'] = wake_match.group(1).replace('：', ':')

    # 睡眠時間
    duration_match = re.search(r'(?:時間|duration|睡眠時間)[：:]?\s*(\d+\.?\d*)', content)
    if duration_match:
        result['duration_hours'] = float(duration_match.group(1))

    # 品質
    quality_match = re.search(r'(?:品質|quality|良さ)[：:]?\s*(\d)', content)
    if quality_match:
        result['quality'] = int(quality_match.group(1))

    # 気分
    mood_match = re.search(r'(?:気分|mood)[：:]\s*([^、,]+)', content, re.IGNORECASE)
    if mood_match:
        result['mood'] = mood_match.group(1).strip()

    # メモ
    notes_match = re.search(r'(?:メモ|memo|note)[：:]\s*(.+)', content)
    if notes_match:
        result['notes'] = notes_match.group(1).strip()

    return result

def parse_update(content):
    """更新内容を解析"""
    result = {}

    # 就寝時刻
    bed_match = re.search(r'(?:就寝|bed)[：:]?\s*(\d{1,2}[：:]\d{2})', content)
    if bed_match:
        result['bed_time'] = bed_match.group(1).replace('：', ':')

    # 起床時刻
    wake_match = re.search(r'(?:起床|wake)[：:]?\s*(\d{1,2}[：:]\d{2})', content)
    if wake_match:
        result['wake_time'] = wake_match.group(1).replace('：', ':')

    # 睡眠時間
    duration_match = re.search(r'(?:時間|duration)[：:]?\s*(\d+\.?\d*)', content)
    if duration_match:
        result['duration_hours'] = float(duration_match.group(1))

    # 品質
    quality_match = re.search(r'(?:品質|quality)[：:]?\s*(\d)', content)
    if quality_match:
        result['quality'] = int(quality_match.group(1))

    # 気分
    mood_match = re.search(r'(?:気分|mood)[：:]\s*([^、,]+)', content, re.IGNORECASE)
    if mood_match:
        result['mood'] = mood_match.group(1).strip()

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

        sleep_id = add_sleep(
            content['date'],
            content['bed_time'],
            content['wake_time'],
            content['duration_hours'],
            content['quality'],
            content['mood'],
            content['notes']
        )

        response = f"😴 睡眠 #{sleep_id} 追加完了\n"
        response += f"日付: {content['date']}\n"
        if content['bed_time']:
            response += f"就寝: {content['bed_time']}\n"
        if content['wake_time']:
            response += f"起床: {content['wake_time']}\n"
        if content['duration_hours']:
            response += f"時間: {content['duration_hours']}時間\n"
        if content['quality']:
            stars = '⭐' * content['quality']
            response += f"品質: {stars}\n"
        if content['mood']:
            response += f"気分: {content['mood']}\n"
        if content['notes']:
            response += f"メモ: {content['notes']}"

        return response

    elif action == 'update':
        updates = parse_update(parsed['content'])

        if not updates:
            return "❌ 更新内容がありません"

        update_sleep(parsed['sleep_id'], **updates)

        response = f"✅ 睡眠 #{parsed['sleep_id']} 更新完了"

        return response

    elif action == 'delete':
        delete_sleep(parsed['sleep_id'])
        return f"🗑️ 睡眠 #{parsed['sleep_id']} 削除完了"

    elif action == 'list':
        sleeps = list_sleeps()

        if not sleeps:
            return "😴 睡眠記録がありません"

        response = f"😴 睡眠記録 ({len(sleeps)}件):\n"
        for sleep in sleeps:
            response += format_sleep(sleep)

        return response

    elif action == 'today':
        date = datetime.now().strftime("%Y-%m-%d")
        sleep = get_by_date(date)

        if not sleep:
            return "😴 今日の睡眠記録はまだありません"

        return format_sleep(sleep, show_title=False)

    elif action == 'yesterday':
        date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        sleep = get_by_date(date)

        if not sleep:
            return "😴 昨日の睡眠記録はありません"

        return format_sleep(sleep, show_title=False)

    elif action == 'this_week':
        week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        sleeps = list_sleeps(date_from=week_ago)

        if not sleeps:
            return "😴 今週の睡眠記録はありません"

        response = f"😴 今週の睡眠 ({len(sleeps)}件):\n"
        for sleep in sleeps:
            response += format_sleep(sleep)

        return response

    elif action == 'stats':
        stats = get_stats()

        response = "📊 睡眠統計:\n"
        response += f"全記録: {stats['total']}日\n"
        if stats['avg_duration']:
            response += f"平均睡眠: {stats['avg_duration']}時間\n"
        if stats['avg_quality']:
            stars = '⭐' * int(stats['avg_quality'])
            response += f"平均品質: {stats['avg_quality']}/5 {stars}\n"
        if stats['yesterday']:
            response += f"昨日: {stats['yesterday']}時間\n"
        if stats['week_count'] > 0:
            response += f"今週平均: {stats['week_avg_duration']}時間\n"
            if stats['week_avg_quality']:
                response += f"今週品質: {stats['week_avg_quality']}/5"

        return response

    return None

def format_sleep(sleep, show_title=True):
    """睡眠をフォーマット"""
    id, date, bed_time, wake_time, duration_hours, quality, mood, notes, created_at = sleep

    response = ""
    if show_title:
        response = f"\n🌙 [{id}] {date}\n"

    parts = []
    if bed_time and wake_time:
        parts.append(f"{bed_time} - {wake_time}")
    if duration_hours:
        parts.append(f"{duration_hours}時間")
    if quality:
        stars = '⭐' * quality
        parts.append(f"{quality}/5 {stars}")

    if parts:
        response += f"    {' | '.join(parts)}\n"

    if mood:
        response += f"    😊 {mood}\n"

    return response

if __name__ == '__main__':
    init_db()

    test_messages = [
        "睡眠: 就寝 23:00, 起床 7:00, 時間 8, 品質 4, 気分 良い",
        "睡眠: 時間 6.5, 品質 3",
        "昨日",
        "今週",
        "統計",
    ]

    for msg in test_messages:
        print(f"\n入力: {msg}")
        result = handle_message(msg)
        if result:
            print(result)
