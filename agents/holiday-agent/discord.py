#!/usr/bin/env python3
"""
休暇管理エージェント #60 - Discord連携
"""

import re
from datetime import datetime, timedelta
from db import *

def parse_message(message):
    holiday_match = re.match(r'(?:休暇|holiday)[：:]\s*(.+)', message, re.IGNORECASE)
    if holiday_match:
        return parse_add_holiday(holiday_match.group(1))

    booking_match = re.match(r'(?:予約|book|booking)[：:]\s*(\d+)\s*(.+)', message, re.IGNORECASE)
    if booking_match:
        parsed = parse_add_booking(booking_match.group(2))
        parsed['holiday_id'] = int(booking_match.group(1))
        return parsed

    update_match = re.match(r'(?:更新|update)[：:]\s*(\d+)\s*(.+)', message, re.IGNORECASE)
    if update_match:
        parsed = parse_update(update_match.group(2))
        parsed['holiday_id'] = int(update_match.group(1))
        return parsed

    list_match = re.match(r'(?:(?:休暇|holiday)(?:一覧|list)|list|holidays)', message, re.IGNORECASE)
    if list_match:
        return {'action': 'list'}

    bookings_match = re.match(r'(?:予約|book|booking)(?:履歴|history|list)[：:]\s*(\d+)', message, re.IGNORECASE)
    if bookings_match:
        return {'action': 'list_bookings', 'holiday_id': int(bookings_match.group(1))}

    status_match = re.match(r'(?:ステータス|status)[：:]\s*(planning|planning|booked|booked|completed|completed|cancelled|cancelled)', message, re.IGNORECASE)
    if status_match:
        return {'action': 'list_by_status', 'status': status_match.group(1)}

    return None

def parse_add_holiday(content):
    result = {'action': 'add', 'title': None, 'destination': None, 'start_date': None,
              'end_date': None, 'days': None, 'budget': None, 'status': 'planning', 'notes': None}

    title_match = re.match(r'^([^、,（\(【]+)', content)
    if title_match:
        result['title'] = title_match.group(1).strip()

    dest_match = re.search(r'(?:目的地|destination|場所)[：:]\s*([^、,]+)', content)
    if dest_match:
        result['destination'] = dest_match.group(1).strip()

    start_match = re.search(r'(?:開始|start|from)[：:]\s*([^、,]+)', content)
    if start_match:
        result['start_date'] = parse_date(start_match.group(1).strip())

    end_match = re.search(r'(?:終了|end|to|until)[：:]\s*([^、,]+)', content)
    if end_match:
        result['end_date'] = parse_date(end_match.group(1).strip())

    budget_match = re.search(r'(?:予算|budget|費用|cost)[：:]?\s*(\d+)', content)
    if budget_match:
        result['budget'] = int(budget_match.group(1))

    days_match = re.search(r'(?:日数|days|日)[：:]?\s*(\d+)', content)
    if days_match:
        result['days'] = int(days_match.group(1))

    notes_match = re.search(r'(?:メモ|備考|memo|note)[：:]\s*(.+)', content)
    if notes_match:
        result['notes'] = notes_match.group(1).strip()

    if not result['title']:
        for key in ['目的地', 'destination', '場所', '開始', 'start', 'from', '終了', 'end', 'to', 'until', '予算', 'budget', '費用', 'cost', '日数', 'days', '日', 'メモ', '備考', 'memo', 'note']:
            match = re.search(rf'{key}[：:]', content)
            if match:
                result['title'] = content[:match.start()].strip()
                break
        else:
            result['title'] = content.strip()

    return result

def parse_add_booking(content):
    result = {'action': 'add_booking', 'type': None, 'provider': None, 'cost': None,
              'currency': 'JPY', 'booking_date': None, 'confirmation_number': None, 'notes': None}

    type_match = re.search(r'(?:タイプ|type)[：:]\s*(flight|hotel|car_rental|activity|other|フライト|ホテル|車|アクティビティ|その他)', content)
    if type_match:
        type_map = {
            'flight': 'flight', 'フライト': 'flight',
            'hotel': 'hotel', 'ホテル': 'hotel',
            'car_rental': 'car_rental', '車': 'car_rental',
            'activity': 'activity', 'アクティビティ': 'activity',
            'other': 'other', 'その他': 'other'
        }
        result['type'] = type_map.get(type_match.group(1).lower())

    provider_match = re.search(r'(?:プロバイダ|provider|業者)[：:]\s*([^、,]+)', content)
    if provider_match:
        result['provider'] = provider_match.group(1).strip()

    cost_match = re.search(r'(?:金額|cost|費用)[：:]?\s*(\d+)', content)
    if cost_match:
        result['cost'] = int(cost_match.group(1))

    booking_match = re.search(r'(?:予約日|booking|book)[：:]\s*([^、,]+)', content)
    if booking_match:
        result['booking_date'] = parse_date(booking_match.group(1).strip())

    conf_match = re.search(r'(?:確認番|confirmation|conf|番号)[：:]?\s*([^、,]+)', content)
    if conf_match:
        result['confirmation_number'] = conf_match.group(1).strip()

    notes_match = re.search(r'(?:メモ|備考|memo|note)[：:]\s*(.+)', content)
    if notes_match:
        result['notes'] = notes_match.group(1).strip()

    return result

def parse_update(content):
    result = {'action': 'update', 'title': None, 'destination': None,
              'start_date': None, 'end_date': None, 'budget': None, 'status': None, 'notes': None}

    title_match = re.search(r'(?:タイトル|title|名前)[：:]\s*([^、,]+)', content)
    if title_match:
        result['title'] = title_match.group(1).strip()

    dest_match = re.search(r'(?:目的地|destination|場所)[：:]\s*([^、,]+)', content)
    if dest_match:
        result['destination'] = dest_match.group(1).strip()

    start_match = re.search(r'(?:開始|start|from)[：:]\s*([^、,]+)', content)
    if start_match:
        result['start_date'] = parse_date(start_match.group(1).strip())

    end_match = re.search(r'(?:終了|end|to|until)[：:]\s*([^、,]+)', content)
    if end_match:
        result['end_date'] = parse_date(end_match.group(1).strip())

    budget_match = re.search(r'(?:予算|budget)[：:]?\s*(\d+)', content)
    if budget_match:
        result['budget'] = int(budget_match.group(1))

    status_match = re.search(r'(?:ステータス|status|状態)[：:]\s*(planning|planning|booked|booked|completed|completed|cancelled|cancelled)', content)
    if status_match:
        status_map = {
            'planning': 'planning', 'planning': 'planning',
            'booked': 'booked', 'booked': 'booked',
            'completed': 'completed', 'completed': 'completed',
            'cancelled': 'cancelled', 'cancelled': 'cancelled'
        }
        result['status'] = status_map.get(status_match.group(1).lower())

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
    if '来月' in date_str:
        return (today.replace(day=1) + timedelta(days=32)).replace(day=1).strftime("%Y-%m-%d")

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

        holiday_id = add_holiday(
            parsed['title'],
            parsed['destination'],
            parsed['start_date'],
            parsed['end_date'],
            parsed['budget'],
            parsed['status'],
            parsed['notes']
        )

        response = f"✈️ 休暇 #{holiday_id} 追加完了\n"
        response += f"タイトル: {parsed['title']}\n"
        if parsed['destination']:
            response += f"目的地: {parsed['destination']}\n"
        if parsed['start_date']:
            response += f"開始: {parsed['start_date']}\n"
        if parsed['end_date']:
            response += f"終了: {parsed['end_date']}\n"
        if parsed['days']:
            response += f"日数: {parsed['days']}日\n"
        if parsed['budget']:
            response += f"予算: ¥{parsed['budget']:,}\n"
        if parsed['notes']:
            response += f"メモ: {parsed['notes']}"

        return response

    elif action == 'add_booking':
        if not parsed['type'] or not parsed['cost']:
            return "❌ タイプと金額を入力してください"

        booking_id = add_booking(
            parsed['holiday_id'],
            parsed['type'],
            parsed['provider'],
            parsed['cost'],
            parsed['currency'],
            parsed['booking_date'],
            parsed['confirmation_number'],
            parsed['notes']
        )

        type_text = {'flight': '✈️ フライト', 'hotel': '🏨 ホテル', 'car_rental': '🚗 レンタカー', 'activity': '🎯 アクティビティ', 'other': '🎡 その他'}.get(parsed['type'])

        return f"✅ 予約 #{booking_id} 追加完了: {type_text} ¥{parsed['cost']:,}"

    elif action == 'update':
        update_holiday(
            parsed['holiday_id'],
            title=parsed.get('title'),
            destination=parsed.get('destination'),
            start_date=parsed.get('start_date'),
            end_date=parsed.get('end_date'),
            budget=parsed.get('budget'),
            status=parsed.get('status'),
            notes=parsed.get('notes')
        )

        status_text = {'planning': '計画中', 'booked': '予約済み', 'completed': '完了', 'cancelled': 'キャンセル'}.get(parsed.get('status'))

        return f"✅ 休暇 #{parsed['holiday_id']} 更新完了: {status_text}"

    elif action == 'list':
        holidays = list_holidays()

        if not holidays:
            return "✈️ 休暇がありません"

        response = f"✈️ 休暇一覧 ({len(holidays)}件):\n"
        for holiday in holidays:
            response += format_holiday(holiday)

        return response

    elif action == 'list_bookings':
        bookings = list_bookings(parsed['holiday_id'])

        if not bookings:
            return f"📅 休暇 #{parsed['holiday_id']} の予約はありません"

        response = f"📅 休暇 #{parsed['holiday_id']} の予約 ({len(bookings)}件):\n"
        for booking in bookings:
            response += format_booking(booking)

        return response

    elif action == 'list_by_status':
        holidays = list_holidays(status=parsed['status'])

        status_text = {'planning': '計画中', 'booked': '予約済み', 'completed': '完了', 'cancelled': 'キャンセル'}.get(parsed['status'], parsed['status'])

        if not holidays:
            return f"✈️ {status_text}の休暇はありません"

        response = f"✈️ {status_text}の休暇 ({len(holidays)}件):\n"
        for holiday in holidays:
            response += format_holiday(holiday)

        return response

    return None

def format_holiday(holiday):
    id, title, destination, start_date, end_date, days, budget, status, notes, created_at = holiday

    status_icons = {'planning': '📅', 'booked': '✅', 'completed': '✈️', 'cancelled': '❌'}
    status_icon = status_icons.get(status, '✈️')

    response = f"{status_icon} [{id}] {title}\n"

    parts = []
    if destination:
        parts.append(f"🌍 {destination}")
    if start_date:
        parts.append(f"📅 {start_date}")
        if end_date:
            parts[-1] += f" - {end_date}"
    if days:
        parts.append(f"📆 {days}日")
    if budget:
        parts.append(f"💰 ¥{budget:,}")

    if parts:
        response += f"  {' '.join(parts)}\n"

    if notes:
        response += f"  📝 {notes[:50]}{'...' if len(notes) > 50 else ''}\n"

    return response

def format_booking(booking):
    id, holiday_id, type, provider, cost, currency, booking_date, confirmation_number, notes, created_at = booking

    type_icons = {'flight': '✈️', 'hotel': '🏨', 'car_rental': '🚗', 'activity': '🎯', 'other': '🎡'}
    type_icon = type_icons.get(type, '📦')

    response = f"{type_icon} [{id}] {provider if provider else 'その他'} - ¥{cost:,}\n"

    if booking_date:
        response += f"  📅 {booking_date}\n"
    if confirmation_number:
        response += f"  📝 確認番: {confirmation_number}\n"

    return response

if __name__ == '__main__':
    init_db()

    test_messages = [
        "休暇: オキナワ, 目的地: オキナワ, 開始: 2026-08-01, 終了: 2026-08-07, 予算: 200000",
        "予約: 1 タイプ: hotel, プロバイダ: ホテルA, 金額: 50000",
        "休暇一覧",
    ]

    for msg in test_messages:
        print(f"\n入力: {msg}")
        result = handle_message(msg)
        if result:
            print(result)
