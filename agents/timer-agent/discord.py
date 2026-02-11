#!/usr/bin/env python3
"""
タイマーエージェント #9 - Discord連携
"""

import re
from db import *

def parse_message(message):
    """メッセージを解析"""
    # タイマー追加
    timer_match = re.match(r'(?:タイマー|timer)[:：]\s*(.+)', message, re.IGNORECASE)
    if timer_match:
        return parse_timer(timer_match.group(1))

    # 開始
    start_match = re.match(r'(?:開始|start)[:：]\s*(\d+)', message, re.IGNORECASE)
    if start_match:
        return {'action': 'start', 'timer_id': int(start_match.group(1))}

    # 停止
    stop_match = re.match(r'(?:停止|stop)[:：]\s*(\d+)', message, re.IGNORECASE)
    if stop_match:
        return {'action': 'stop', 'timer_id': int(stop_match.group(1))}

    # 完了
    complete_match = re.match(r'(?:完了|done|complete)[:：]\s*(\d+)', message, re.IGNORECASE)
    if complete_match:
        return {'action': 'complete', 'timer_id': int(complete_match.group(1))}

    # 状況確認
    status_match = re.match(r'(?:状況|status)[:：]\s*(\d+)?', message, re.IGNORECASE)
    if status_match:
        timer_id = status_match.group(1)
        if timer_id:
            return {'action': 'status', 'timer_id': int(timer_id)}
        return {'action': 'status_all'}

    # Pomodoro
    pomodoro_match = re.match(r'ポモドーロ|pomodoro', message, re.IGNORECASE)
    if pomodoro_match:
        return {'action': 'pomodoro'}

    # アクティブタイマー一覧
    if message.strip() in ['タイマー一覧', '一覧', 'list', 'timers']:
        return {'action': 'list'}

    return None

def parse_timer(content):
    """タイマーを解析"""
    result = {'action': 'add', 'name': None, 'duration': None}

    # 時間
    duration_match = re.search(r'(\d+)\s*(分|時間|hour|h|min)', content)
    if duration_match:
        value, unit = duration_match.groups()
        if unit in ['時間', 'hour', 'h']:
            result['duration'] = int(value) * 60
        else:
            result['duration'] = int(value)
        content = content.replace(duration_match.group(0), '').strip()

    # タイトル
    if content:
        result['name'] = content.strip()

    return result

def handle_message(message):
    """メッセージを処理"""
    parsed = parse_message(message)

    if not parsed:
        return None

    action = parsed['action']

    if action == 'add':
        if not parsed['duration']:
            return "❌ 時間を指定してください（例: 25分、1時間）"

        timer_id = add_timer(parsed['name'], parsed['duration'])

        response = f"⏱️ タイマー #{timer_id} 追加完了\n"
        if parsed['name']:
            response += f"名前: {parsed['name']}\n"
        response += f"時間: {parsed['duration']}分"

        return response

    elif action == 'start':
        start_timer(parsed['timer_id'])
        return f"▶️ タイマー #{parsed['timer_id']} 開始！"

    elif action == 'stop':
        stop_timer(parsed['timer_id'])
        return f"⏸️ タイマー #{parsed['timer_id']} 停止"

    elif action == 'complete':
        complete_timer(parsed['timer_id'])
        return f"✅ タイマー #{parsed['timer_id']} 完了！"

    elif action == 'status':
        timer = get_timer_status(parsed['timer_id'])
        if not timer:
            return f"❌ タイマー #{parsed['timer_id']} が見つかりません"

        return format_timer_status(timer)

    elif action == 'status_all':
        timers = list_active_timers()

        if not timers:
            return "⏱️ アクティブなタイマーはありません"

        response = "⏱️ アクティブタイマー:\n"
        for timer in timers:
            response += format_timer_status(timer)

        return response

    elif action == 'list':
        timers = list_active_timers()

        if not timers:
            return "⏱️ アクティブなタイマーはありません"

        response = "⏱️ アクティブタイマー:\n"
        for timer in timers:
            response += f"\n[{timer['id']}] {timer['name'] or '無名'}\n"
            response += f"    状況: {timer['status']}\n"
            response += f"    残り: {timer['remaining'] // 60}分{timer['remaining'] % 60}秒"

        return response

    elif action == 'pomodoro':
        # Pomodoroタイマー作成
        timer_id = add_timer("Pomodoro作業", 25)
        start_timer(timer_id)

        return f"🍅 Pomodoro開始！\nタイマー #{timer_id}: 25分作業\n作業後、5分休憩しましょう！"

    return None

def format_timer_status(timer):
    """タイマー状況をフォーマット"""
    status_text = {
        'stopped': '停止',
        'running': '実行中',
        'paused': '一時停止',
        'completed': '完了'
    }

    remaining_min = timer['remaining'] // 60
    remaining_sec = timer['remaining'] % 60

    response = f"\n⏱️ タイマー #{timer['id']}"
    if timer['name']:
        response += f" ({timer['name']})"
    response += f"\n"
    response += f"    状況: {status_text.get(timer['status'], timer['status'])}\n"
    response += f"    残り: {remaining_min}分{remaining_sec}秒"

    if timer['status'] == 'running' and timer['end_time']:
        response += f"\n    終了予定: {timer['end_time']}"

    return response

if __name__ == '__main__':
    # テスト
    init_db()

    test_messages = [
        "タイマー: 25分",
        "開始: 1",
        "状況: 1",
        "タイマー一覧",
        "ポモドーロ",
    ]

    for msg in test_messages:
        print(f"\n入力: {msg}")
        result = handle_message(msg)
        if result:
            print(result)
