#!/usr/bin/env python3
"""
目標追跡エージェント #17 - Discord連携
"""

import re
from db import *

def parse_message(message):
    """メッセージを解析"""
    # 目標追加
    goal_match = re.match(r'(?:目標|goal)[:：]\s*(.+)', message, re.IGNORECASE)
    if goal_match:
        return parse_goal(goal_match.group(1))

    # 進捗更新
    progress_match = re.match(r'(?:進捗|progress)[:：]\s*(\d+)\s+(\d+)', message, re.IGNORECASE)
    if progress_match:
        return {'action': 'progress', 'goal_id': int(progress_match.group(1)), 'progress': int(progress_match.group(2))}

    # 完了
    complete_match = re.match(r'(?:完了|done)[:：]\s*(\d+)', message, re.IGNORECASE)
    if complete_match:
        return {'action': 'complete', 'goal_id': int(complete_match.group(1))}

    # 一覧
    if message.strip() in ['目標一覧', '一覧', 'list', 'goals']:
        return {'action': 'list'}

    # 統計
    if message.strip() in ['統計', 'stats', '目標統計']:
        return {'action': 'stats'}

    return None

def parse_goal(content):
    """目標を解析"""
    result = {'action': 'add_goal', 'title': None, 'description': None, 'deadline': None, 'priority': 2}

    # タイトル (最初の部分)
    title_match = re.match(r'^([^、,（\(【♪]+)', content)
    if title_match:
        result['title'] = title_match.group(1).strip()
        content = content.replace(title_match.group(0), '').strip()

    # 優先度
    priority_match = re.search(r'優先[:：]\s*(高|中|低|\d)', content)
    if priority_match:
        priority = priority_match.group(1)
        if priority == '高' or priority == '3':
            result['priority'] = 3
        elif priority == '中' or priority == '2':
            result['priority'] = 2
        elif priority == '低' or priority == '1':
            result['priority'] = 1

    # 期限
    deadline_match = re.search(r'期限[:：]\s*([^、,]+)', content)
    if deadline_match:
        result['deadline'] = parse_date(deadline_match.group(1).strip())

    # 説明
    desc_match = re.search(r'説明[:：]\s*(.+)', content)
    if desc_match:
        result['description'] = desc_match.group(1).strip()

    return result

def parse_date(date_str):
    """日付を解析"""
    from datetime import datetime, timedelta

    today = datetime.now()

    # 今日
    if '今日' in date_str:
        return today.strftime("%Y-%m-%d")

    # 明日
    if '明日' in date_str:
        return (today + timedelta(days=1)).strftime("%Y-%m-%d")

    # 日付形式
    date_match = re.match(r'(\d{4})-(\d{1,2})-(\d{1,2})', date_str)
    if date_match:
        return f"{date_match.group(1)}-{date_match.group(2).zfill(2)}-{date_match.group(3).zfill(2)}"

    # 数値 + 日後
    days_match = re.match(r'(\d+)日後', date_str)
    if days_match:
        days = int(days_match.group(1))
        return (today + timedelta(days=days)).strftime("%Y-%m-%d")

    # 日曜/月曜など
    weekday_map = {'日': 0, '月': 1, '火': 2, '水': 3, '木': 4, '金': 5, '土': 6}
    for day_name, day_num in weekday_map.items():
        if day_name in date_str:
            days_ahead = (day_num - today.weekday() + 7) % 7
            if days_ahead == 0:
                days_ahead = 7
            return (today + timedelta(days=days_ahead)).strftime("%Y-%m-%d")

    return None

def handle_message(message):
    """メッセージを処理"""
    parsed = parse_message(message)

    if not parsed:
        return None

    action = parsed['action']

    if action == 'add_goal':
        if not parsed['title']:
            return "❌ 目標タイトルを入力してください"

        goal_id = add_goal(
            parsed['title'],
            parsed['description'],
            parsed['deadline'],
            parsed['priority']
        )

        priority_icons = ["", "🟢", "🟡", "🔴"]
        priority_icon = priority_icons[parsed['priority']]

        response = f"🎯 目標 #{goal_id} 追加完了\n"
        response += f"タイトル: {parsed['title']} {priority_icon}"
        if parsed['description']:
            response += f"\n説明: {parsed['description']}"
        if parsed['deadline']:
            response += f"\n期限: {parsed['deadline']}"

        return response

    elif action == 'progress':
        update_goal_progress(parsed['goal_id'], parsed['progress'])
        return f"📈 目標 #{parsed['goal_id']} 進捗更新: {parsed['progress']}%"

    elif action == 'complete':
        complete_goal(parsed['goal_id'])
        return f"🎉 目標 #{parsed['goal_id']} 完了！"

    elif action == 'list':
        goals = list_goals()

        if not goals:
            return "🎯 目標がありません"

        response = f"🎯 目標一覧 ({len(goals)}件):\n"
        for goal in goals:
            response += format_goal(goal)

        return response

    elif action == 'stats':
        goals = list_goals()

        response = "📊 目標統計:\n"
        response += f"アクティブ目標: {len(goals)}件\n"
        response += f"平均進捗: {sum(g[5] for g in goals) // len(goals) if goals else 0}%"

        return response

    return None

def format_goal(goal):
    """目標をフォーマット"""
    id, title, description, deadline, priority, progress, status, created_at = goal

    status_icons = {'active': '🎯', 'paused': '⏸️', 'completed': '✅', 'cancelled': '❌'}
    priority_icons = ["", "🟢", "🟡", "🔴"]

    status_icon = status_icons.get(status, '❓')
    priority_icon = priority_icons[priority]

    progress_bar = '█' * (progress // 10) + '░' * (10 - progress // 10)

    response = f"\n{status_icon} [{id}] {title} {priority_icon}\n"
    response += f"    進捗: {progress}% {progress_bar}"
    if deadline:
        response += f"\n    期限: {deadline}"
    if description:
        response += f"\n    説明: {description}"

    return response

if __name__ == '__main__':
    # テスト
    init_db()

    test_messages = [
        "目標: 新しい言語を学ぶ, 優先:高, 期限: 2026-06-01",
        "目標: 体を鍛える, 優先:中, 期限: 3日後",
        "進捗: 1 50",
        "目標一覧",
        "完了: 1",
    ]

    for msg in test_messages:
        print(f"\n入力: {msg}")
        result = handle_message(msg)
        if result:
            print(result)
