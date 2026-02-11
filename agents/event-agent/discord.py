#!/usr/bin/env python3
"""
イベント管理エージェント #57 - Discord連携
"""

import re
from datetime import datetime
from db import *

def parse_message(message):
    event_match = re.match(r'(?:イベント|event)[：:]\s*(.+)', message, re.IGNORECASE)
    if event_match:
        return parse_add(event_match.group(1))

    invite_match = re.match(r'(?:招待|invite|inv)[：:]\s*(\d+)\s*(.+)', message, re.IGNORECASE)
    if invite_match:
        parsed = parse_add_invite(invite_match.group(2))
        parsed['event_id'] = int(invite_match.group(1))
        return parsed

    rsvp_match = re.match(r'(?:rsvp)[：:]\s*(\d+)\s*(pending|accepted|declined|tentative)', message, re.IGNORECASE)
    if rsvp_match:
        return {'action': 'update_rsvp', 'invite_id': int(rsvp_match.group(1)), 'rsvp_status': rsvp_match.group(2)}

    update_match = re.match(r'(?:更新|update)[：:]\s*(\d+)\s*(.+)', message, re.IGNORECASE)
    if update_match:
        parsed = parse_update(event_match.group(2))
        parsed['event_id'] = int(update_match.group(1))
        return parsed

    list_match = re.match(r'(?:(?:イベント|event)(?:一覧|list)|list|events)', message, re.IGNORECASE)
    if list_match:
        return {'action': 'list'}

    invites_match = re.match(r'(?:招待|inv|invites)[：:]\s*(\d+)', message, re.IGNORECASE)
    if invites_match:
        return {'action': 'list_invites', 'event_id': int(invites_match.group(1))}

    status_match = re.match(r'(?:ステータス|status|状態)[：:]\s*(upcoming|ongoing|completed|cancelled)', message, re.IGNORECASE)
    if status_match:
        return {'action': 'list_by_status', 'status': status_match.group(1)}

    return None

def parse_add(content):
    result = {'action': 'add', 'title': None, 'description': None, 'location': None,
              'start_date': None, 'start_time': None, 'end_date': None, 'end_time': None,
              'category': None, 'notes': None}

    title_match = re.match(r'^([^、,（\(【]+)', content)
    if title_match:
        result['title'] = title_match.group(1).strip()

    desc_match = re.search(r'(?:説明|description|desc)[：:]\s*(.+)', content)
    if desc_match:
        result['description'] = desc_match.group(1).strip()

    location_match = re.search(r'(?:場所|location|場所)[：:]\s*([^、,]+)', content)
    if location_match:
        result['location'] = location_match.group(1).strip()

    start_date_match = re.search(r'(?:開始日|start|開始)[：:]\s*([^、,]+)', content)
    if start_date_match:
        result['start_date'] = parse_date(start_date_match.group(1).strip())

    start_time_match = re.search(r'(?:開始時間|start time|開始時)[：:]?\s*(\d{1,2}:\d{2})', content)
    if start_time_match:
        result['start_time'] = start_time_match.group(1)

    end_date_match = re.search(r'(?:終了日|end|終了)[：:]\s*([^、,]+)', content)
    if end_date_match:
        result['end_date'] = parse_date(end_date_match.group(1).strip())

    end_time_match = re.search(r'(?:終了時間|end time|終了時)[：:]?\s*(\d{1,2}:\d{2})', content)
    if end_time_match:
        result['end_time'] = end_time_match.group(1)

    category_match = re.search(r'(?:カテゴリ|category)[：:]\s*([^、,]+)', content)
    if category_match:
        result['category'] = category_match.group(1).strip()

    notes_match = re.search(r'(?:メモ|備考|memo|note)[：:]\s*(.+)', content)
    if notes_match:
        result['notes'] = notes_match.group(1).strip()

    if not result['title']:
        for key in ['説明', 'description', 'desc', '場所', 'location', '開始日', 'start', '開始',
                    '開始時間', 'start time', '終了日', 'end', '終了', '終了時間', 'end time', '終了時',
                    'カテゴリ', 'category', 'メモ', '備考', 'memo', 'note']:
            match = re.search(rf'{key}[：:]', content)
            if match:
                result['title'] = content[:match.start()].strip()
                break
        else:
            result['title'] = content.strip()

    return result

def parse_add_invite(content):
    result = {'action': 'add_invite', 'guest_name': None, 'email': None,
              'rsvp_status': 'pending', 'notes': None}

    name_match = re.match(r'^([^、,（\(【]+)', content)
    if name_match:
        result['guest_name'] = name_match.group(1).strip()

    email_match = re.search(r'(?:メール|email|アドレス)[：:]\s*([^、,]+)', content)
    if email_match:
        result['email'] = email_match.group(1).strip()

    notes_match = re.search(r'(?:メモ|備考|memo|note)[：:]\s*(.+)', content)
    if notes_match:
        result['notes'] = notes_match.group(1).strip()

    if not result['guest_name']:
        for key in ['メール', 'email', 'アドレス', 'メモ', '備考', 'memo', 'note']:
            match = re.search(rf'{key}[：:]', content)
            if match:
                result['guest_name'] = content[:match.start()].strip()
                break
        else:
            result['guest_name'] = content.strip()

    return result

def parse_update(content):
    result = {'action': 'update', 'status': None}

    status_match = re.search(r'(?:ステータス|status|状態)[：:]\s*(upcoming|ongoing|completed|cancelled)', content)
    if status_match:
        result['status'] = status_match.group(1)

    return result

def parse_date(date_str):
    today = datetime.now()

    if '今日' in date_str:
        return today.strftime("%Y-%m-%d")
    if '明日' in date_str:
        from datetime import timedelta
        return (today + timedelta(days=1)).strftime("%Y-%m-%d")
    if '来週' in date_str:
        from datetime import timedelta
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

        event_id = add_event(
            parsed['title'],
            parsed['description'],
            parsed['location'],
            parsed['start_date'],
            parsed['start_time'],
            parsed['end_date'],
            parsed['end_time'],
            parsed['category'],
            parsed['notes']
        )

        response = f"🎪 イベント #{event_id} 追加完了\n"
        response += f"タイトル: {parsed['title']}\n"
        if parsed['description']:
            response += f"説明: {parsed['description'][:100]}...\n"
        if parsed['location']:
            response += f"場所: {parsed['location']}\n"
        if parsed['start_date']:
            response += f"開始: {parsed['start_date']}"
            if parsed['start_time']:
                response += f" {parsed['start_time']}\n"
            else:
                response += "\n"
        if parsed['end_date']:
            response += f"終了: {parsed['end_date']}"
            if parsed['end_time']:
                response += f" {parsed['end_time']}\n"
            else:
                response += "\n"
        if parsed['category']:
            response += f"カテゴリ: {parsed['category']}\n"
        if parsed['notes']:
            response += f"メモ: {parsed['notes']}"

        return response

    elif action == 'add_invite':
        if not parsed['guest_name']:
            return "❌ ゲスト名を入力してください"

        invite_id = add_invitation(
            parsed['event_id'],
            parsed['guest_name'],
            parsed['email'],
            parsed['rsvp_status'],
            parsed['notes']
        )

        return f"📨 招待 #{invite_id} 追加完了: {parsed['guest_name']}"

    elif action == 'update_rsvp':
        update_rsvp(parsed['invite_id'], parsed['rsvp_status'])
        return f"✅ RSVP更新完了: {parsed['rsvp_status']}"

    elif action == 'update':
        if parsed['status']:
            update_event(parsed['event_id'], status=parsed['status'])
            status_text = {'upcoming': '開催予定', 'ongoing': '開催中', 'completed': '終了', 'cancelled': 'キャンセル'}.get(parsed['status'], parsed['status'])
            return f"✅ イベント #{parsed['event_id']} のステータスを {status_text} に更新しました"

        return "❌ 更新するステータスを入力してください"

    elif action == 'list':
        events = list_events()

        if not events:
            return "🎪 イベントがありません"

        response = f"🎪 イベント一覧 ({len(events)}件):\n"
        for event in events:
            response += format_event(event)

        return response

    elif action == 'list_invites':
        invites = list_invitations(parsed['event_id'])

        if not invites:
            return f"📨 招待記録がありません (イベント#{parsed['event_id']})"

        response = f"📨 招待記録 ({len(invites)}件):\n"
        for invite in invites:
            response += format_invite(invite)

        return response

    elif action == 'list_by_status':
        events = list_events(status=parsed['status'])

        if not events:
            return f"🎪 {parsed['status']}のイベントはありません"

        response = f"🎪 {parsed['status']}のイベント ({len(events)}件):\n"
        for event in events:
            response += format_event(event)

        return response

    return None

def format_event(event):
    id, title, description, location, start_date, start_time, end_date, end_time, category, status, notes, created_at = event

    status_icons = {'upcoming': '📅', 'ongoing': '🔴', 'completed': '✅', 'cancelled': '❌'}
    status_icon = status_icons.get(status, '📅')

    response = f"{status_icon} [{id}] {title}\n"

    parts = []
    if location:
        parts.append(f"📍 {location}")
    if start_date:
        parts.append(f"📅 {start_date}")
        if start_time:
            parts[-1] += f" {start_time}"
    if category:
        parts.append(f"🏷️ {category}")

    if parts:
        response += f"  {' '.join(parts)}\n"

    if description:
        response += f"  📝 {description[:80]}{'...' if len(description) > 80 else ''}\n"

    return response

def format_invite(invite):
    id, event_id, guest_name, email, rsvp_status, responded_at, notes, created_at = invite

    rsvp_icons = {'pending': '⏳', 'accepted': '✅', 'declined': '❌', 'tentative': '❓'}
    rsvp_icon = rsvp_icons.get(rsvp_status, '⏳')

    response = f"{rsvp_icon} [{id}] {guest_name}"

    if email:
        response += f" ({email})"

    response += "\n"

    return response

if __name__ == '__main__':
    init_db()

    test_messages = [
        "イベント: 誕生日パーティー, 場所: 公園, 開始: 2026-03-01 14:00, 終了: 2026-03-01 18:00",
        "招待: 1 田中, email: tanaka@example.com",
        "rsvp: 1 accepted",
        "ステータス: upcoming",
        "イベント一覧",
    ]

    for msg in test_messages:
        print(f"\n入力: {msg}")
        result = handle_message(msg)
        if result:
            print(result)
