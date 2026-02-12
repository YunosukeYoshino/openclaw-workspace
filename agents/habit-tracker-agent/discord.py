#!/usr/bin/env python3
"""
習慣トラッカーエージェント #51 - Discord連携
"""

import re
from datetime import datetime
from db import *

def parse_message(message):
    """メッセージを解析"""
    # 習慣追加
    habit_match = re.match(r'(?:習慣|habit)[：:]\s*(.+)', message, re.IGNORECASE)
    if habit_match:
        return parse_add_habit(habit_match.group(1))

    # 記録
    log_match = re.match(r'(?:記録|log|check-in)[：:]\s*(\d+)', message, re.IGNORECASE)
    if log_match:
        parsed = parse_add_log(message)
        parsed['habit_id'] = int(log_match.group(1))
        return parsed

    # 一覧
    list_match = re.match(r'(?:(?:習慣|habit)(?:一覧|list)|list|habits)', message, re.IGNORECASE)
    if list_match:
        return {'action': 'list'}

    # 履歴
    history_match = re.match(r'(?:履歴|history|logs)[：:]\s*(\d+)', message, re.IGNORECASE)
    if history_match:
        return {'action': 'history', 'habit_id': int(history_match.group(1))}

    # 統計
    if message.strip() in ['統計', 'stats', '習慣統計']:
        return {'action': 'stats'}

    return None

def parse_add_habit(content):
    """習慣追加を解析"""
    result = {'action': 'add', 'name': None, 'category': None, 'target_days': None}

    # 名前 (最初の部分)
    name_match = re.match(r'^([^、,（\(【]+)', content)
    if name_match:
        result['name'] = name_match.group(1).strip()

    # カテゴリ
    category_match = re.search(r'(?:カテゴリ|category)[：:]\s*([^、,]+)', content)
    if category_match:
        result['category'] = category_match.group(1).strip()

    # 目標日数
    target_match = re.search(r'(?:目標|target|日数)[：:]?\s*(\d+)', content)
    if target_match:
        result['target_days'] = int(target_match.group(1))

    # 名前がまだない場合、最初の項目より前を名前とする
    if not result['name']:
        for key in ['カテゴリ', 'category', '目標', 'target', '日数']:
            match = re.search(rf'{key}[：:]', content)
            if match:
                result['name'] = content[:match.start()].strip()
                break
        else:
            result['name'] = content.strip()

    return result

def parse_add_log(content):
    """記録追加を解析"""
    result = {'action': 'log', 'date': None, 'status': 'completed', 'notes': None}

    # 日付
    date_match = re.search(r'(?:日付|date)[：:]\s*([^、,]+)', content)
    if date_match:
        result['date'] = parse_date(date_match.group(1).strip())
    else:
        # デフォルトは今日
        result['date'] = datetime.now().strftime("%Y-%m-%d")

    # ステータス
    status_match = re.search(r'(?:ステータス|status|状態)[：:]\s*(完了|completed|完了した|スキップ|skipped|スキップした|missed|ミスした)', content)
    if status_match:
        status_map = {
            '完了': 'completed', 'completed': 'completed', '完了した': 'completed',
            'スキップ': 'skipped', 'skipped': 'skipped', 'スキップした': 'skipped',
            'missed': 'missed', 'ミスした': 'missed'
        }
        result['status'] = status_map.get(status_match.group(1).lower())

    # メモ
    notes_match = re.search(r'(?:メモ|備考|memo|note)[：:]\s*(.+)', content)
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
        from datetime import timedelta
        return (today - timedelta(days=1)).strftime("%Y-%m-%d")

    # 明日
    if '明日' in date_str:
        from datetime import timedelta
        return (today + timedelta(days=1)).strftime("%Y-%m-%d")

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
        if not parsed['name']:
            return "❌ 習慣名を入力してください"

        habit_id = add_habit(
            parsed['name'],
            parsed['category'],
            parsed['target_days']
        )

        response = f"✅ 習慣 #{habit_id} 追加完了\n"
        response += f"習慣: {parsed['name']}\n"
        if parsed['category']:
            response += f"カテゴリ: {parsed['category']}\n"
        if parsed['target_days']:
            response += f"目標日数: {parsed['target_days']}日"

        return response

    elif action == 'log':
        log_id = log_habit(
            parsed['habit_id'],
            parsed['date'],
            parsed['status'],
            parsed['notes']
        )

        habit_id = parsed['habit_id']
        habit_name = f"習慣#{habit_id}"
        habits = list_habits()
        for h in habits:
            if h[0] == habit_id:
                habit_name = h[1]
                break

        status_text = {'completed': '✅ 完了', 'skipped': '⏭️ スキップ', 'missed': '❌ ミス'}.get(parsed['status'], parsed['status'])

        return f"{status_text} {habit_name} ({parsed['date']})"

    elif action == 'list':
        habits = list_habits()

        if not habits:
            return "📋 習慣がありません"

        response = f"📋 習慣一覧 ({len(habits)}件):\n"
        for habit in habits:
            response += format_habit(habit)

        return response

    elif action == 'history':
        logs = list_logs(parsed['habit_id'])

        habit_id = parsed['habit_id']
        habit_name = f"習慣#{habit_id}"
        habits = list_habits()
        for h in habits:
            if h[0] == habit_id:
                habit_name = h[1]
                break

        if not logs:
            return f"📅 {habit_name}の記録がありません"

        response = f"📅 {habit_name}の記録 ({len(logs)}件):\n"
        for log in logs:
            response += format_log(log)

        return response

    elif action == 'stats':
        habits = list_habits()

        if not habits:
            return "📊 習慣がありません"

        response = "📊 習慣統計:\n"
        for habit in habits:
            habit_id = habit[0]
            habit_name = habit[1]
            streak = get_streak(habit_id)
            rate = get_completion_rate(habit_id, 7)

            streak_text = f"🔥 {streak}日連続" if streak > 0 else "💨 連続なし"

            response += f"\n{habit_name}\n"
            response += f"  {streak_text} | 達成率: {rate:.0f}% (7日間)\n"

        return response

    return None

def format_habit(habit):
    """習慣をフォーマット"""
    id, name, category, target_days, created_at = habit

    response = f"\n[{id}] {name}\n"

    parts = []
    if category:
        parts.append(f"📁 {category}")
    if target_days:
        parts.append(f"🎯 {target_days}日目標")

    if parts:
        response += f"  {' '.join(parts)}\n"

    return response

def format_log(log):
    """記録をフォーマット"""
    id, habit_id, date, status, notes, created_at = log

    status_icons = {'completed': '✅', 'skipped': '⏭️', 'missed': '❌'}
    status_icon = status_icons.get(status, '❓')

    response = f"{status_icon} {date}"

    if notes:
        response += f" - {notes[:50]}{'...' if len(notes) > 50 else ''}"

    response += "\n"

    return response

if __name__ == '__main__':
    # テスト
    init_db()

    test_messages = [
        "習慣: 毎朝の散歩, カテゴリ: 健康, 目標: 30",
        "記録: 1, 日付: 今日, ステータス: 完了",
        "習慣一覧",
        "履歴: 1",
        "統計",
    ]

    for msg in test_messages:
        print(f"\n入力: {msg}")
        result = handle_message(msg)
        if result:
            print(result)
