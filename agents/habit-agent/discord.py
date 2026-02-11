#!/usr/bin/env python3
"""
習慣トラッカーエージェント #11 - Discord連携
"""

import re
from datetime import datetime, timedelta
from db import *

def parse_message(message):
    """メッセージを解析"""
    # 習慣追加
    habit_match = re.match(r'(?:習慣|habit)[:：]\s*(.+)', message, re.IGNORECASE)
    if habit_match:
        return parse_habit(habit_match.group(1))

    # 記録
    log_match = re.match(r'(?:記録|log)[:：]\s*(\d+)', message, re.IGNORECASE)
    if log_match:
        return {'action': 'log', 'habit_id': int(log_match.group(1))}

    # 検索
    search_match = re.match(r'検索[:：]\s*(.+)', message)
    if search_match:
        return {'action': 'search', 'keyword': search_match.group(1)}

    # 一覧
    if message.strip() in ['習慣一覧', '一覧', 'list', 'habits']:
        return {'action': 'list'}

    return None

def parse_habit(content):
    """習慣を解析"""
    result = {'action': 'add', 'name': None, 'frequency': 'daily', 'goal_days': 30, 'memo': None}

    # 名前
    name_match = re.match(r'^([^、,（\(【♪]+)', content)
    if name_match:
        result['name'] = name_match.group(1).strip()
        content = content.replace(name_match.group(0), '').strip()

    # 頻度
    freq_match = re.search(r'頻度[:：]\s*([^、,]+)', content)
    if freq_match:
        freq = freq_match.group(1).strip()
        if '週' in freq:
            result['frequency'] = 'weekly'
        elif '月' in freq:
            result['frequency'] = 'monthly'
        else:
            result['frequency'] = 'daily'

    # 目標日数
    goal_match = re.search(r'目標[:：]\s*(\d+)\s*(日|days)?', content)
    if goal_match:
        result['goal_days'] = int(goal_match.group(1))

    # メモ
    memo_match = re.search(r'メモ[:：]\s*(.+)', content)
    if memo_match:
        result['memo'] = memo_match.group(1).strip()

    # 名前がまだない場合
    if not result['name']:
        freq_match = re.search(r'頻度[:：]', content)
        if freq_match:
            result['name'] = content[:freq_match.start()].strip()
        else:
            result['name'] = content.strip()

    return result

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
            parsed['frequency'],
            parsed['goal_days'],
            parsed['memo']
        )

        response = f"🔄 習慣 #{habit_id} 追加完了\n"
        response += f"名前: {parsed['name']}\n"
        response += f"頻度: {parsed['frequency']}\n"
        response += f"目標: {parsed['goal_days']}日"
        if parsed['memo']:
            response += f"\nメモ: {parsed['memo']}"

        return response

    elif action == 'log':
        log_id = log_habit(parsed['habit_id'])

        if log_id is None:
            return f"⚠️ 今日は既に記録されています"

        streak = get_habit_streak(parsed['habit_id'])

        response = f"✅ 習慣 #{parsed['habit_id']} 記録完了！\n"
        response += f"🔥 ストリーク: {streak}日連続！"

        return response

    elif action == 'list':
        habits = list_habits()

        if not habits:
            return "🔄 習慣がありません"

        response = f"🔄 習慣一覧 ({len(habits)}件):\n"
        for habit in habits:
            response += format_habit(habit)

        return response

    return None

def format_habit(habit):
    """習慣をフォーマット"""
    fire_icons = ["", "🔥", "🔥🔥", "🔥🔥🔥", "🔥🔥🔥🔥", "🔥🔥🔥🔥🔥"]
    fire = fire_icons[min(habit['streak'], 5)] if habit['streak'] > 0 else ""

    response = f"\n[{habit['id']}] {habit['name']}\n"
    response += f"    頻度: {habit['frequency']}\n"
    response += f"    目標: {habit['goal_days']}日\n"
    response += f"    ストリーク: {habit['streak']}日 {fire}"

    return response

if __name__ == '__main__':
    # テスト
    init_db()

    test_messages = [
        "習慣: 早起き, 目標: 30日",
        "習慣: 運動, 頻度: 週",
        "記録: 1",
        "習慣一覧",
    ]

    for msg in test_messages:
        print(f"\n入力: {msg}")
        result = handle_message(msg)
        if result:
            print(result)
