#!/usr/bin/env python3
"""
Calendar Event Agent #2 - Discord Integration
"""

import re
from datetime import datetime, timedelta
from db import *

def parse_message(message):
    """Parse message"""
    # Add event
    add_match = re.match(r'(?:追加|add)[:：]\s*(.+)', message, re.IGNORECASE)
    if add_match:
        return parse_add(add_match.group(1))

    # Update event
    update_match = re.match(r'(?:更新|update)[:：]\s*(\d+)\s*[,，]\s*(.+)', message, re.IGNORECASE)
    if update_match:
        return {'action': 'update', 'event_id': int(update_match.group(1)), 'content': update_match.group(2)}

    # Delete event
    delete_match = re.match(r'(?:削除|delete)[:：]\s*(\d+)', message, re.IGNORECASE)
    if delete_match:
        return {'action': 'delete', 'event_id': int(delete_match.group(1))}

    # List events
    list_match = re.match(r'(?:一覧|list|events)(?:[:：]\s*(.+))?', message, re.IGNORECASE)
    if list_match:
        date_str = list_match.group(1).strip() if list_match.group(1) else None
        if date_str and date_str in ['今日', '明日', 'today', 'tomorrow']:
            date_str = parse_date(date_str)
        return {'action': 'list', 'date': date_str}

    # Search events
    search_match = re.match(r'(?:検索|search)[:：]\s*(.+)', message, re.IGNORECASE)
    if search_match:
        return {'action': 'search', 'query': search_match.group(1)}

    # Add attendee
    attendee_match = re.match(r'(?:参加者|attendee)[:：]\s*(\d+)\s*[,，]\s*(.+)', message, re.IGNORECASE)
    if attendee_match:
        return {'action': 'add_attendee', 'event_id': int(attendee_match.group(1)), 'name': attendee_match.group(2)}

    # Upcoming
    if re.match(r'(?:今後|upcoming)', message, re.IGNORECASE):
        return {'action': 'upcoming'}

    # Stats
    if message.strip() in ['統計', 'stats']:
        return {'action': 'stats'}

    return None

def parse_add(content):
    """Parse add content"""
    result = {'action': 'add', 'title': None, 'start_date': None, 'description': None,
              'start_time': None, 'end_date': None, 'end_time': None,
              'location': None, 'category': None, 'priority': 'medium'}

    result['title'] = content.split(',')[0].strip()

    date_match = re.search(r'(?:日付|date)[:：]\s*(.+?)(?:[、,]|$)', content)
    if date_match:
        result['start_date'] = parse_date(date_match.group(1).strip())

    time_match = re.search(r'(?:時間|time)[:：]\s*(\d{1,2}:\d{2})', content)
    if time_match:
        result['start_time'] = time_match.group(1)

    end_time_match = re.search(r'(?:終了時間|end)[:：]\s*(\d{1,2}:\d{2})', content)
    if end_time_match:
        result['end_time'] = end_time_match.group(1)

    location_match = re.search(r'(?:場所|location)[:：]\s*(.+?)(?:[、,]|$)', content)
    if location_match:
        result['location'] = location_match.group(1).strip()

    category_match = re.search(r'(?:カテゴリ|category)[:：]\s*(.+?)(?:[、,]|$)', content)
    if category_match:
        result['category'] = category_match.group(1).strip()

    priority_match = re.search(r'(?:優先度|priority)[:：]\s*(low|medium|high|低|中|高)', content)
    if priority_match:
        p = priority_match.group(1).lower()
        priority_map = {'低': 'low', '中': 'medium', '高': 'high'}
        result['priority'] = priority_map.get(p, p)

    desc_match = re.search(r'(?:説明|description)[:：]\s*(.+)', content)
    if desc_match:
        result['description'] = desc_match.group(1).strip()

    return result

def parse_date(date_str):
    """Parse date string"""
    today = datetime.now()

    if date_str in ['今日', 'today']:
        return today.strftime("%Y-%m-%d")
    elif date_str in ['明日', 'tomorrow']:
        return (today + timedelta(days=1)).strftime("%Y-%m-%d")

    if '-' in date_str:
        parts = date_str.split('-')
        if len(parts) == 3:
            return f"{parts[0]}-{parts[1].zfill(2)}-{parts[2].zfill(2)}"

    if '/' in date_str:
        parts = date_str.split('/')
        if len(parts) == 2:
            return f"{today.year}-{parts[0].zfill(2)}-{parts[1].zfill(2)}"

    return date_str

def handle_message(message):
    """Handle message"""
    parsed = parse_message(message)

    if not parsed:
        return None

    action = parsed['action']

    if action == 'add':
        if not parsed['title']:
            return "❌ タイトルを入力してください / Please enter a title"

        event_id = add_event(
            parsed['title'],
            parsed['start_date'] or datetime.now().strftime('%Y-%m-%d'),
            parsed['description'],
            parsed['start_time'],
            parsed['end_date'],
            parsed['end_time'],
            parsed['location'],
            parsed['category'],
            parsed['priority']
        )

        response = f"✅ イベント #{event_id} を追加しました / Event #{event_id} added\n"
        response += f"タイトル: {parsed['title']}\n"
        if parsed['start_date']:
            response += f"日付: {parsed['start_date']}\n"
        if parsed['start_time']:
            response += f"時間: {parsed['start_time']}"

        return response

    elif action == 'update':
        event_id = parsed['event_id']
        updates = {}
        content = parsed['content']

        title_match = re.search(r'(?:タイトル|title)[:：]\s*(.+?)(?:[、,]|$)', content)
        if title_match:
            updates['title'] = title_match.group(1).strip()

        date_match = re.search(r'(?:日付|date)[:：]\s*(.+?)(?:[、,]|$)', content)
        if date_match:
            updates['start_date'] = parse_date(date_match.group(1).strip())

        location_match = re.search(r'(?:場所|location)[:：]\s*(.+?)(?:[、,]|$)', content)
        if location_match:
            updates['location'] = location_match.group(1).strip()

        status_match = re.search(r'(?:ステータス|status)[:：]\s*(confirmed|tentative|cancelled)', content)
        if status_match:
            updates['status'] = status_match.group(1)

        if updates:
            update_event(event_id, **updates)
            return f"✅ イベント #{event_id} を更新しました / Event #{event_id} updated"
        else:
            return "❌ 更新内容を入力してください / Please enter update content"

    elif action == 'delete':
        delete_event(parsed['event_id'])
        return f"✅ イベント #{parsed['event_id']} を削除しました / Event #{parsed['event_id']} deleted"

    elif action == 'list':
        events = list_events(date=parsed['date'])

        if not events:
            date_text = f" ({parsed['date']})" if parsed['date'] else ""
            return f"📅 イベント{date_text} がありません / No events found"

        date_text = f" ({parsed['date']})" if parsed['date'] else ""
        response = f"📅 イベント一覧{date_text} ({len(events)}件):\n"
        for event in events:
            response += format_event(event)

        return response

    elif action == 'search':
        results = search_events(parsed['query'])

        if not results:
            return f"🔍 検索結果がありません / No results found for '{parsed['query']}'"

        response = f"🔍 検索結果: '{parsed['query']}' ({len(results)}件):\n"
        for event in results:
            response += format_event(event)

        return response

    elif action == 'add_attendee':
        add_attendee(parsed['event_id'], parsed['name'])
        return f"✅ イベント #{parsed['event_id']} に参加者 '{parsed['name']}' を追加しました / Attendee added"

    elif action == 'upcoming':
        events = get_upcoming_events()

        if not events:
            return "📅 今後のイベントがありません / No upcoming events"

        response = f"📅 今後のイベント ({len(events)}件):\n"
        for event in events:
            response += format_event(event)

        return response

    elif action == 'stats':
        stats = get_stats()

        response = "📊 イベント統計 / Event Stats:\n"
        response += f"総数: {stats['total_events']}件\n"
        response += f"確認済み: {stats['confirmed']}件\n"
        response += f"未定: {stats['tentative']}件\n"
        response += f"キャンセル: {stats['cancelled']}件\n"
        response += f"今日: {stats['today_events']}件"

        return response

    return None

def format_event(event):
    """Format event"""
    id, title, description, start_date, start_time, end_date, end_time, location, category, priority, status, created_at = event

    priority_map = {'low': '🟢', 'medium': '🟡', 'high': '🔴'}
    status_map = {'confirmed': '✅', 'tentative': '⏳', 'cancelled': '❌'}

    response = f"\n{status_map.get(status, '❓')} [{id}] {title}\n"
    if start_date:
        response += f"    日付: {start_date}\n"
    if start_time:
        response += f"    時間: {start_time}"
        if end_time:
            response += f" - {end_time}"
        response += "\n"
    if location:
        response += f"    場所: {location}\n"
    if category:
        response += f"    カテゴリ: {category}\n"

    return response

if __name__ == '__main__':
    init_db()
