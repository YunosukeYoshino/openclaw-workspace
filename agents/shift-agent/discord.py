#!/usr/bin/env python3
"""
Shift Agent #27 - Discord Integration
"""

import re
from datetime import datetime, timedelta
from db import *

def parse_message(message):
    """Parse message"""
    # Add shift
    add_match = re.match(r'(?:追加|add|new)[:：]\s*(.+)', message, re.IGNORECASE)
    if add_match:
        return parse_add(add_match.group(1))

    # Update status
    status_match = re.match(r'(?:ステータス|status)[:：]\s*(\d+)\s*[,，]\s*(\w+)', message, re.IGNORECASE)
    if status_match:
        return {'action': 'update_status', 'shift_id': int(status_match.group(1)), 'status': status_match.group(2)}

    # Request time off
    off_match = re.match(r'(?:休暇|timeoff|off)[:：]\s*(.+?)\s*[,，]\s*(.+)', message, re.IGNORECASE)
    if off_match:
        return {'action': 'request_time_off', 'member_name': off_match.group(1), 'request_date': off_match.group(2)}

    # Approve request
    approve_match = re.match(r'(?:承認|approve)[:：]\s*(\d+)', message, re.IGNORECASE)
    if approve_match:
        return {'action': 'approve', 'request_id': int(approve_match.group(1))}

    # Deny request
    deny_match = re.match(r'(?:拒否|deny)[:：]\s*(\d+)', message, re.IGNORECASE)
    if deny_match:
        return {'action': 'deny', 'request_id': int(deny_match.group(1))}

    # List shifts
    list_match = re.match(r'(?:シフト一覧|shifts|list)(?:[:：]\s*(.+))?', message, re.IGNORECASE)
    if list_match:
        date_str = list_match.group(1) if list_match.group(1) else None
        if date_str:
            date_str = parse_date(date_str)
        return {'action': 'list_shifts', 'date': date_str}

    # List requests
    if message.strip() in ['申請一覧', 'requests']:
        return {'action': 'list_requests'}

    # Stats
    if message.strip() in ['統計', 'stats']:
        return {'action': 'stats'}

    return None

def parse_add(content):
    """Parse add content"""
    result = {'action': 'add', 'member_name': None, 'shift_date': None, 'start_time': None, 'end_time': None, 'role': None, 'notes': None}

    # Member name (first part)
    parts = content.split(',|、')
    if parts:
        result['member_name'] = parts[0].strip()

    # Date
    date_match = re.search(r'(\d{4}-\d{1,2}-\d{1,2}|\d{1,2}/\d{1,2}|今日|明日)', content)
    if date_match:
        result['shift_date'] = parse_date(date_match.group(1))

    # Time range
    time_match = re.search(r'(\d{1,2}:\d{2})\s*[-~～]\s*(\d{1,2}:\d{2})', content)
    if time_match:
        result['start_time'] = time_match.group(1)
        result['end_time'] = time_match.group(2)

    # Role
    role_match = re.search(r'役割|role[:：]\s*(.+?)(?:[、,]|$)', content)
    if role_match:
        result['role'] = role_match.group(1).strip()

    # Notes
    note_match = re.search(r'メモ|notes[:：]\s*(.+)', content)
    if note_match:
        result['notes'] = note_match.group(1).strip()

    return result

def parse_date(date_str):
    """Parse date string"""
    today = datetime.now()

    if date_str == '今日':
        return today.strftime("%Y-%m-%d")
    elif date_str == '明日':
        return (today + timedelta(days=1)).strftime("%Y-%m-%d")

    # YYYY-MM-DD
    if '-' in date_str:
        parts = date_str.split('-')
        if len(parts) == 3:
            return f"{parts[0]}-{parts[1].zfill(2)}-{parts[2].zfill(2)}"

    # MM/DD
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
        if not parsed['member_name'] or not parsed['shift_date'] or not parsed['start_time'] or not parsed['end_time']:
            return "❌ メンバー名、日付、開始時間、終了時間を入力してください"

        shift_id = add_shift(
            parsed['member_name'],
            parsed['shift_date'],
            parsed['start_time'],
            parsed['end_time'],
            parsed['role'],
            parsed['notes']
        )

        response = f"✅ シフト #{shift_id} 追加完了\n"
        response += f"メンバー: {parsed['member_name']}\n"
        response += f"日付: {parsed['shift_date']}\n"
        response += f"時間: {parsed['start_time']} - {parsed['end_time']}"

        return response

    elif action == 'update_status':
        status_map = {'scheduled': 'scheduled', 'completed': 'completed', 'cancelled': 'cancelled', 'no_show': 'no_show', 'noshow': 'no_show'}
        status = status_map.get(parsed['status'].lower(), parsed['status'])
        update_shift_status(parsed['shift_id'], status)
        return f"✅ シフト #{parsed['shift_id']} のステータスを {status} に更新"

    elif action == 'request_time_off':
        request_date = parse_date(parsed['request_date'])
        request_id = request_time_off(parsed['member_name'], request_date)
        return f"📅 {parsed['member_name']} の休暇申請 #{request_id} 作成 ({request_date})"

    elif action == 'approve':
        approve_request(parsed['request_id'])
        return f"✅ 申請 #{parsed['request_id']} を承認"

    elif action == 'deny':
        deny_request(parsed['request_id'])
        return f"❌ 申請 #{parsed['request_id']} を拒否"

    elif action == 'list_shifts':
        shifts = list_shifts(date=parsed['date'])

        if not shifts:
            date_text = f" ({parsed['date']})" if parsed['date'] else ""
            return f"📅 シフト{date_text} がありません"

        date_text = f" ({parsed['date']})" if parsed['date'] else ""
        response = f"📅 シフト一覧{date_text} ({len(shifts)}件):\n"
        for shift in shifts:
            response += format_shift(shift)

        return response

    elif action == 'list_requests':
        requests = list_requests()

        if not requests:
            return "📋 申請がありません"

        response = f"📋 申請一覧 ({len(requests)}件):\n"
        for req in requests:
            response += format_request(req)

        return response

    elif action == 'stats':
        stats = get_stats()

        response = "📊 シフト統計:\n"
        response += f"全シフト: {stats['total_shifts']}件\n"
        response += f"予定: {stats['scheduled']}件\n"
        response += f"完了: {stats['completed']}件\n"
        response += f"キャンセル: {stats['cancelled']}件\n"
        response += f"欠勤: {stats['no_show']}件\n"
        response += f"保留申請: {stats['pending_requests']}件"

        return response

    return None

def format_shift(shift):
    """Format shift"""
    id, member_name, shift_date, start_time, end_time, role, status, notes, created_at = shift

    status_map = {'scheduled': '📅', 'completed': '✅', 'cancelled': '❌', 'no_show': '⚠️'}
    status_icon = status_map.get(status, '❓')

    response = f"\n{status_icon} [{id}] {member_name}\n"
    response += f"    {shift_date} {start_time}-{end_time}\n"
    if role:
        response += f"    役割: {role}\n"

    return response

def format_request(req):
    """Format request"""
    id, member_name, request_date, request_type, reason, status, created_at = req

    status_map = {'pending': '⏳', 'approved': '✅', 'denied': '❌'}
    status_icon = status_map.get(status, '❓')

    type_map = {'time_off': '🏖️', 'swap': '🔄', 'extra': '➕'}
    type_icon = type_map.get(request_type, '❓')

    response = f"\n{status_icon} {type_icon} [{id}] {member_name}\n"
    response += f"    日付: {request_date}\n"
    if reason:
        response += f"    理由: {reason}\n"

    return response

if __name__ == '__main__':
    init_db()

    test_messages = [
        "追加: 田中太郎, 今日, 9:00-17:00",
        "追加: 佐藤花子, 2026-02-12, 10:00-18:00",
        "シフト一覧",
        "シフト一覧: 今日",
        "休暇: 田中太郎, 明日",
        "申請一覧",
        "承認: 1",
        "統計",
    ]

    for msg in test_messages:
        print(f"\n入力: {msg}")
        result = handle_message(msg)
        if result:
            print(result)
