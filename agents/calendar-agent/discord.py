#!/usr/bin/env python3
"""
カレンダーエージェント #8 - Discord連携
"""

import re
from datetime import datetime, timedelta
from db import *

def parse_message(message):
    """メッセージを解析"""
    # イベント追加
    event_match = re.match(r'(?:予定|イベント|event|calendar)[:：]\s*(.+)', message, re.IGNORECASE)
    if event_match:
        return parse_event(event_match.group(1))

    # 検索
    search_match = re.match(r'検索[:：]\s*(.+)', message)
    if search_match:
        return {'action': 'search', 'keyword': search_match.group(1)}

    # 一覧
    if message.strip() in ['予定一覧', '一覧', 'list', 'events', 'calendar']:
        return {'action': 'list'}

    # 今週
    if message.strip() in ['今週', '今週の予定', 'this week']:
        return {'action': 'upcoming', 'days': 7}

    # 統計
    if message.strip() in ['統計', 'stats', '予定統計']:
        return {'action': 'stats'}

    return None

def parse_event(content):
    """イベントを解析"""
    result = {'action': 'add', 'title': None, 'datetime': None, 'location': None, 'description': None}

    # タイトル (最初の部分)
    title_match = re.match(r'^([^、,（\(【♪]+)', content)
    if title_match:
        result['title'] = title_match.group(1).strip()
        content = content.replace(title_match.group(0), '').strip()

    # 日時
    datetime_match = re.search(r'日時[:：]\s*([^、,]+)', content)
    if datetime_match:
        result['datetime'] = parse_datetime(datetime_match.group(1).strip())
        content = content.replace(datetime_match.group(0), '').strip()

    # 場所
    location_match = re.search(r'場所[:：]\s*([^、,]+)', content)
    if location_match:
        result['location'] = location_match.group(1).strip()

    # 説明
    desc_match = re.search(r'説明[:：]\s*(.+)', content)
    if desc_match:
        result['description'] = desc_match.group(1).strip()

    # タイトルがまだない場合、日時より前をタイトルとする
    if not result['title']:
        datetime_match = re.search(r'日時[:：]', content)
        if datetime_match:
            result['title'] = content[:datetime_match.start()].strip()
        else:
            result['title'] = content.strip()

    return result

def parse_datetime(dt_str):
    """日時を解析"""
    now = datetime.now()

    # 今日
    if '今日' in dt_str:
        time_match = re.search(r'(\d{1,2}):(\d{2})', dt_str)
        if time_match:
            return datetime(now.year, now.month, now.day, int(time_match.group(1)), int(time_match.group(2))).strftime("%Y-%m-%d %H:%M")
        return now.strftime("%Y-%m-%d 12:00")

    # 明日
    if '明日' in dt_str:
        time_match = re.search(r'(\d{1,2}):(\d{2})', dt_str)
        if time_match:
            return (now + timedelta(days=1)).replace(hour=int(time_match.group(1)), minute=int(time_match.group(2))).strftime("%Y-%m-%d %H:%M")
        return (now + timedelta(days=1)).strftime("%Y-%m-%d 12:00")

    # 日付
    date_match = re.match(r'(\d{4})-(\d{1,2})-(\d{1,2})', dt_str)
    if date_match:
        year = int(date_match.group(1))
        month = int(date_match.group(2))
        day = int(date_match.group(3))
        time_match = re.search(r'(\d{1,2}):(\d{2})', dt_str)
        if time_match:
            return datetime(year, month, day, int(time_match.group(1)), int(time_match.group(2))).strftime("%Y-%m-%d %H:%M")
        return datetime(year, month, day, 12, 0).strftime("%Y-%m-%d %H:%M")

    # 数値 + 日後
    days_match = re.match(r'(\d+)日後', dt_str)
    if days_match:
        days = int(days_match.group(1))
        time_match = re.search(r'(\d{1,2}):(\d{2})', dt_str)
        if time_match:
            return (now + timedelta(days=days)).replace(hour=int(time_match.group(1)), minute=int(time_match.group(2))).strftime("%Y-%m-%d %H:%M")
        return (now + timedelta(days=days)).strftime("%Y-%m-%d 12:00")

    return None

def handle_message(message):
    """メッセージを処理"""
    parsed = parse_message(message)

    if not parsed:
        return None

    action = parsed['action']

    if action == 'add':
        if not parsed['title']:
            return "❌ タイトルを入力してください"

        event_id = add_event(
            parsed['title'],
            parsed['datetime'] or datetime.now().strftime("%Y-%m-%d %H:%M"),
            parsed['location'],
            parsed['description']
        )

        response = f"📅 予定 #{event_id} 追加完了\n"
        response += f"タイトル: {parsed['title']}\n"
        if parsed['datetime']:
            response += f"日時: {parsed['datetime']}\n"
        if parsed['location']:
            response += f"場所: {parsed['location']}"
        if parsed['description']:
            response += f"\n説明: {parsed['description']}"

        return response

    elif action == 'search':
        keyword = parsed['keyword']
        events = search_events(keyword)

        if not events:
            return f"🔍 「{keyword}」の検索結果: 見つかりませんでした"

        response = f"🔍 「{keyword}」の検索結果 ({len(events)}件):\n"
        for event in events:
            response += format_event(event)

        return response

    elif action == 'list':
        events = list_events()

        if not events:
            return "📅 予定がありません"

        response = f"📅 予定一覧 ({len(events)}件):\n"
        for event in events:
            response += format_event(event)

        return response

    elif action == 'upcoming':
        days = parsed.get('days', 7)
        events = list_upcoming_events(days)

        if not events:
            return f"📅 今{days}日間の予定はありません"

        response = f"📅 今{days}日間の予定 ({len(events)}件):\n"
        for event in events:
            response += format_event(event)

        return response

    elif action == 'stats':
        stats = get_stats()

        response = "📊 予定統計:\n"
        response += f"全予定数: {stats['total']}件\n"
        response += f"今後の予定: {stats['upcoming']}件\n"
        response += f"今週の予定: {stats['this_week']}件"

        return response

    return None

def format_event(event):
    """イベントをフォーマット"""
    id, title, event_datetime, location, description, created_at = event

    response = f"\n[{id}] {title}\n"
    response += f"    日時: {event_datetime}\n"
    if location:
        response += f"    場所: {location}\n"
    if description:
        response += f"    説明: {description}\n"

    return response

if __name__ == '__main__':
    # テスト
    init_db()

    test_messages = [
        "予定: ミーティング, 日時: 明日10:00, 場所:会議室A",
        "予定: 誕生日, 日時: 2026-02-14, 説明: 友人の誕生日",
        "予定: 買い物, 日時: 明日18:00",
        "検索: ミーティング",
        "今週",
        "予定一覧",
        "統計",
    ]

    for msg in test_messages:
        print(f"\n入力: {msg}")
        result = handle_message(msg)
        if result:
            print(result)
