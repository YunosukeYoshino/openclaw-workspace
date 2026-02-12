#!/usr/bin/env python3
"""
リマインダーエージェント #10 - Discord連携
"""

import re
from datetime import datetime, timedelta
from db import *

def parse_message(message):
    """メッセージを解析"""
    # リマインダー追加
    reminder_match = re.match(r'(?:リマインダー|reminder)[:：]\s*(.+)', message, re.IGNORECASE)
    if reminder_match:
        return parse_reminder(reminder_match.group(1))

    # 完了
    complete_match = re.match(r'(?:完了|done)[:：]\s*(\d+)', message, re.IGNORECASE)
    if complete_match:
        return {'action': 'complete', 'reminder_id': int(complete_match.group(1))}

    # 無視
    dismiss_match = re.match(r'(?:無視|dismiss)[:：]\s*(\d+)', message, re.IGNORECASE)
    if dismiss_match:
        return {'action': 'dismiss', 'reminder_id': int(dismiss_match.group(1))}

    # 一覧
    if message.strip() in ['リマインダー一覧', '一覧', 'list', 'reminders']:
        return {'action': 'list'}

    return None

def parse_reminder(content):
    """リマインダーを解析"""
    result = {'action': 'add', 'title': None, 'reminder_time': None, 'memo': None}

    # タイトル
    title_match = re.match(r'^([^、,（\(【♪]+)', content)
    if title_match:
        result['title'] = title_match.group(1).strip()
        content = content.replace(title_match.group(0), '').strip()

    # 時間
    time_match = re.search(r'時間[:：]\s*([^、,]+)', content)
    if time_match:
        result['reminder_time'] = parse_time(time_match.group(1).strip())
        content = content.replace(time_match.group(0), '').strip()

    # メモ
    memo_match = re.search(r'メモ[:：]\s*(.+)', content)
    if memo_match:
        result['memo'] = memo_match.group(1).strip()

    # タイトルがまだない場合、時間より前をタイトルとする
    if not result['title']:
        time_match = re.search(r'時間[:：]', content)
        if time_match:
            result['title'] = content[:time_match.start()].strip()
        else:
            result['title'] = content.strip()

    return result

def parse_time(time_str):
    """時間を解析"""
    now = datetime.now()

    # 今日
    if '今日' in time_str:
        time_match = re.search(r'(\d{1,2}):(\d{2})', time_str)
        if time_match:
            return datetime(now.year, now.month, now.day, int(time_match.group(1)), int(time_match.group(2))).strftime("%Y-%m-%d %H:%M")

    # 明日
    if '明日' in time_str:
        time_match = re.search(r'(\d{1,2}):(\d{2})', time_str)
        if time_match:
            return (now + timedelta(days=1)).replace(hour=int(time_match.group(1)), minute=int(time_match.group(2))).strftime("%Y-%m-%d %H:%M")

    # 時間形式
    time_match = re.search(r'(\d{1,2}):(\d{2})', time_str)
    if time_match:
        hour = int(time_match.group(1))
        minute = int(time_match.group(2))

        # 今日/明日判定
        if hour < now.hour or (hour == now.hour and minute <= now.minute):
            return (now + timedelta(days=1)).replace(hour=hour, minute=minute).strftime("%Y-%m-%d %H:%M")
        return now.replace(hour=hour, minute=minute).strftime("%Y-%m-%d %H:%M")

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

        reminder_id = add_reminder(
            parsed['title'],
            parsed['reminder_time'] or datetime.now().strftime("%Y-%m-%d %H:%M"),
            parsed['memo']
        )

        response = f"🔔 リマインダー #{reminder_id} 追加完了\n"
        response += f"タイトル: {parsed['title']}\n"
        if parsed['reminder_time']:
            response += f"時間: {parsed['reminder_time']}"
        if parsed['memo']:
            response += f"\nメモ: {parsed['memo']}"

        return response

    elif action == 'complete':
        complete_reminder(parsed['reminder_id'])
        return f"✅ リマインダー #{parsed['reminder_id']} 完了！"

    elif action == 'dismiss':
        dismiss_reminder(parsed['reminder_id'])
        return f"🚫 リマインダー #{parsed['reminder_id']} 無視"

    elif action == 'list':
        reminders = list_reminders()

        if not reminders:
            return "🔔 リマインダーがありません"

        response = f"🔔 リマインダー一覧 ({len(reminders)}件):\n"
        for reminder in reminders:
            response += format_reminder(reminder)

        return response

    return None

def format_reminder(reminder):
    """リマインダーをフォーマット"""
    id, title, reminder_time, memo, status = reminder

    status_icon = "✅" if status == 'completed' else "⏰"

    response = f"\n{status_icon} [{id}] {title}\n"
    response += f"    時間: {reminder_time}"
    if memo:
        response += f"\n    メモ: {memo}"

    return response

if __name__ == '__main__':
    # テスト
    init_db()

    test_messages = [
        "リマインダー: 会議, 時間: 明日10:00, メモ: 重要",
        "リマインダー: 誕生日, 時間: 2026-02-14 09:00",
        "完了: 1",
        "リマインダー一覧",
    ]

    for msg in test_messages:
        print(f"\n入力: {msg}")
        result = handle_message(msg)
        if result:
            print(result)
