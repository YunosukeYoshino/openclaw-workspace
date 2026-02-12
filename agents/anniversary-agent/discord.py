#!/usr/bin/env python3
"""
記念日管理エージェント #59 - Discord連携
"""

import re
from datetime import datetime, timedelta
from db import *

def parse_message(message):
    anniversary_match = re.match(r'(?:記念日|anniversary|記念)[：:]\s*(.+)', message, re.IGNORECASE)
    if anniversary_match:
        return parse_add(anniversary_match.group(1))

    celebration_match = re.match(r'(?:お祝い|celebration|celeb)[：:]\s*(\d+)\s*(.+)', message, re.IGNORECASE)
    if celebration_match:
        parsed = parse_add_celebration(celebration_match.group(2))
        parsed['anniversary_id'] = int(celebration_match.group(1))
        return parsed

    list_match = re.match(r'(?:(?:記念日|anniversary)(?:一覧|list)|list|anniversaries)', message, re.IGNORECASE)
    if list_match:
        return {'action': 'list'}

    celebrations_match = re.match(r'(?:お祝い|celebration|celeb)(?:履歴|history)[：:]\s*(\d+)', message, re.IGNORECASE)
    if celebrations_match:
        return {'action': 'list_celebrations', 'anniversary_id': int(celebrations_match.group(1))}

    upcoming_match = re.match(r'(?:来る|upcoming|次|next)[：:]\s*(\d+)', message, re.IGNORECASE)
    if upcoming_match:
        return {'action': 'upcoming', 'days': int(upcoming_match.group(1))}

    if message.strip() in ['来月', 'next month', '次の月', '来月分']:
        return {'action': 'next_month'}

    update_match = re.match(r'(?:更新|update)[：:]\s*(\d+)\s*(.+)', message, re.IGNORECASE)
    if update_match:
        parsed = parse_update(anniversary_match.group(2) if 'anniversary_match' in locals() else update_match.group(2))
        parsed['anniversary_id'] = int(update_match.group(1))
        return parsed

    return None

def parse_add(content):
    result = {'action': 'add', 'title': None, 'date': None, 'type': None, 'description': None,
              'partner': None, 'location': None, 'notes': None}

    title_match = re.match(r'^([^、,（\(【]+)', content)
    if title_match:
        result['title'] = title_match.group(1).strip()

    date_match = re.search(r'(?:日付|date)[：:]\s*([^、,]+)', content)
    if date_match:
        result['date'] = parse_date(date_match.group(1).strip())

    type_match = re.search(r'(?:タイプ|type|種類)[：:]\s*(wedding|dating|work|other|結婚|交際|仕事|その他)', content)
    if type_match:
        type_str = type_match.group(1).lower()
        type_map = {
            'wedding': 'wedding', '結婚': 'wedding',
            'dating': 'dating', '交際': 'dating',
            'work': 'work', '仕事': 'work',
            'other': 'other', 'その他': 'other'
        }
        result['type'] = type_map.get(type_str, 'other')

    desc_match = re.search(r'(?:説明|description|desc)[：:]\s*(.+)', content)
    if desc_match:
        result['description'] = desc_match.group(1).strip()

    partner_match = re.search(r'(?:相手|partner|パートナー)[：:]\s*([^、,]+)', content)
    if partner_match:
        result['partner'] = partner_match.group(1).strip()

    location_match = re.search(r'(?:場所|location|場)[：:]\s*([^、,]+)', content)
    if location_match:
        result['location'] = location_match.group(1).strip()

    notes_match = re.search(r'(?:メモ|備考|memo|note)[：:]\s*(.+)', content)
    if notes_match:
        result['notes'] = notes_match.group(1).strip()

    if not result['title']:
        for key in ['日付', 'date', 'タイプ', 'type', '種類', '説明', 'description', 'desc',
                    '相手', 'partner', 'パートナー', '場所', 'location', '場', 'メモ', '備考', 'memo', 'note']:
            match = re.search(rf'{key}[：:]', content)
            if match:
                result['title'] = content[:match.start()].strip()
                break
        else:
            result['title'] = content.strip()

    return result

def parse_add_celebration(content):
    result = {'action': 'add_celebration', 'year': None, 'notes': None}

    year_match = re.search(r'(?:年|year)[：:]\s*(\d{4})', content)
    if year_match:
        result['year'] = int(year_match.group(1))
    else:
        result['year'] = datetime.now().year

    notes_match = re.search(r'(?:メモ|備考|memo|note)[：:]\s*(.+)', content)
    if notes_match:
        result['notes'] = notes_match.group(1).strip()

    gift_match = re.search(r'(?:ギフト|gift)[：:]\s*(.+)', content)
    if gift_match:
        result['notes'] = f"ギフト: {gift_match.group(1).strip()}"

    return result

def parse_update(content):
    result = {'action': 'update', 'title': None, 'date': None, 'description': None,
              'partner': None, 'location': None, 'notes': None}

    title_match = re.search(r'(?:タイトル|title|名前)[：:]\s*([^、,]+)', content)
    if title_match:
        result['title'] = title_match.group(1).strip()

    date_match = re.search(r'(?:日付|date)[：:]\s*([^、,]+)', content)
    if date_match:
        result['date'] = parse_date(date_match.group(1).strip())

    desc_match = re.search(r'(?:説明|description|desc)[：:]\s*(.+)', content)
    if desc_match:
        result['description'] = desc_match.group(1).strip()

    partner_match = re.search(r'(?:相手|partner|パートナー)[：:]\s*([^、,]+)', content)
    if partner_match:
        result['partner'] = partner_match.group(1).strip()

    location_match = re.search(r'(?:場所|location|場)[：:]\s*([^、,]+)', content)
    if location_match:
        result['location'] = location_match.group(1).strip()

    notes_match = re.search(r'(?:メモ|備考|memo|note)[：:]\s*(.+)', content)
    if notes_match:
        result['notes'] = notes_match.group(1).strip()

    return result

def parse_date(date_str):
    today = datetime.now()

    if '今日' in date_str:
        return today.strftime("%Y-%m-%d")
    if '明日' in date_str:
        return (today + timedelta(days=1)).strftime("%Y-%m-%d")
    if '来週' in date_str:
        return (today + timedelta(weeks=1)).strftime("%Y-%m-%d")

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
    parsed = parse_message(message)

    if not parsed:
        return None

    action = parsed['action']

    if action == 'add':
        if not parsed['title']:
            return "❌ タイトルを入力してください"

        anniversary_id = add_anniversary(
            parsed['title'],
            parsed['date'],
            parsed['type'],
            parsed['description'],
            parsed['partner'],
            parsed['location'],
            parsed['notes']
        )

        type_icons = {'wedding': '💒', 'dating': '💕', 'work': '💼', 'other': '🎉'}
        type_icon = type_icons.get(parsed['type'], '🎉')

        response = f"{type_icon} 記念日 #{anniversary_id} 追加完了\n"
        response += f"タイトル: {parsed['title']}\n"
        if parsed['date']:
            response += f"日付: {parsed['date']}\n"
        if parsed['partner']:
            response += f"相手: {parsed['partner']}\n"
        if parsed['location']:
            response += f"場所: {parsed['location']}\n"
        if parsed['description']:
            response += f"説明: {parsed['description'][:100]}...\n"

        return response

    elif action == 'add_celebration':
        if not parsed['notes'] and not parsed['year']:
            return "❌ 年かメモを入力してください"

        celebration_id = add_celebration(
            parsed['anniversary_id'],
            parsed['year'],
            parsed['notes']
        )

        return f"🎊 お祝い記録 #{celebration_id} 追加完了: {parsed['year']}年"

    elif action == 'list':
        anniversaries = list_anniversaries()

        if not anniversaries:
            return "📅 記念日がありません"

        response = f"📅 記念日一覧 ({len(anniversaries)}件):\n"
        for anniversary in anniversaries:
            response += format_anniversary(anniversary)

        return response

    elif action == 'list_celebrations':
        celebrations = list_celebrations(parsed['anniversary_id'])

        if not celebrations:
            return f"🎊 記念日 #{parsed['anniversary_id']} のお祝い記録がありません"

        response = f"🎊 記念日 #{parsed['anniversary_id']} のお祝い ({len(celebrations)}件):\n"
        for celebration in celebrations:
            response += format_celebration(celebration)

        return response

    elif action == 'upcoming':
        days = parsed['days']
        anniversaries = get_upcoming(days)

        if not anniversaries:
            return f"📅 今後{days}日以内の記念日はありません"

        response = f"📅 今後{days}日以内の記念日 ({len(anniversaries)}件):\n"
        for anniversary in anniversaries:
            response += format_anniversary(anniversary)

        return response

    elif action == 'next_month':
        next_month = (datetime.now().replace(day=1) + timedelta(days=32)).replace(day=1).month
        today = datetime.now()
        target = datetime(today.year, next_month, 1) if next_month > today.month else datetime(today.year + 1, next_month, 1)

        current_anniversaries = list_anniversaries()
        upcoming = []

        for anniversary in current_anniversaries:
            ann_date = datetime.strptime(anniversary[2], "%Y-%m-%d")
            if ann_date.month == next_month:
                upcoming.append(anniversary)

        if not upcoming:
            return f"📅 来月の記念日はありません"

        response = f"📅 来月の記念日 ({len(upcoming)}件):\n"
        for anniversary in upcoming:
            response += format_anniversary(anniversary)

        return response

    return None

def format_anniversary(anniversary):
    id, title, date, type, description, partner, location, notes, created_at = anniversary

    type_icons = {'wedding': '💒', 'dating': '💕', 'work': '💼', 'other': '🎉'}
    type_icon = type_icons.get(type, '🎉')

    response = f"{type_icon} [{id}] {title} - {date}\n"

    if partner:
        response += f"  💕 {partner}\n"
    if location:
        response += f"  📍 {location}\n"

    return response

def format_celebration(celebration):
    id, anniversary_id, year, notes, created_at = celebration

    response = f"🎊 [{id}] {year}年"

    if notes:
        response += f": {notes[:50]}{'...' if len(notes) > 50 else ''}"

    response += "\n"

    return response

if __name__ == '__main__':
    init_db()

    test_messages = [
        "記念日: 結婚記念日, タイプ: wedding, 日付: 2023-05-01",
        "お祝い: 1 2023, ギフト: ハネムーンウォッチ",
        "記念日一覧",
        "来る 30",
    ]

    for msg in test_messages:
        print(f"\n入力: {msg}")
        result = handle_message(msg)
        if result:
            print(result)
