#!/usr/bin/env python3
"""
ToDoエージェント #5 - Discord連携
"""

import re
from datetime import datetime, timedelta
from db import *

def parse_message(message):
    """メッセージを解析"""
    # タスク追加
    todo_match = re.match(r'(?:タスク|todo|to?do|todo)[:：]\s*(.+)', message, re.IGNORECASE)
    if todo_match:
        return parse_add(todo_match.group(1))

    # 完了
    complete_match = re.match(r'(?:完了|done|finish)[:：]\s*(\d+)', message, re.IGNORECASE)
    if complete_match:
        return {'action': 'complete', 'todo_id': int(complete_match.group(1))}

    # 検索
    search_match = re.match(r'(?:検索|search)[:：]\s*(.+)', message, re.IGNORECASE)
    if search_match:
        return {'action': 'search', 'keyword': search_match.group(1)}

    # 一覧
    list_match = re.match(r'(?:(?:タスク|todo|to?do)(?:一覧|list)|list|todos)', message, re.IGNORECASE)
    if list_match:
        return {'action': 'list'}

    # 未完了
    if message.strip() in ['未完了', 'pending', '未完了一覧']:
        return {'action': 'list_pending'}

    # 統計
    if message.strip() in ['統計', 'stats', 'タスク統計']:
        return {'action': 'stats'}

    return None

def parse_add(content):
    """タスク追加を解析"""
    result = {'action': 'add', 'title': None, 'description': None, 'priority': None, 'due_date': None}

    # タイトル (最初の部分)
    title_match = re.match(r'^([^、,（\(【♪]+)', content)
    if title_match:
        result['title'] = title_match.group(1).strip()

    # 優先順位
    priority_match = re.search(r'優先(?:度|順位)?[:：]\s*(高|中|低|\d)', content)
    if priority_match:
        priority = priority_match.group(1)
        if priority == '高' or priority == '3':
            result['priority'] = 3
        elif priority == '中' or priority == '2':
            result['priority'] = 2
        elif priority == '低' or priority == '1':
            result['priority'] = 1

    # 期限
    due_match = re.search(r'期限[:：]\s*([^、,]+)', content)
    if due_match:
        due_str = due_match.group(1).strip()
        result['due_date'] = parse_due_date(due_str)

    # 説明
    desc_match = re.search(r'説明[:：]\s*(.+)', content)
    if desc_match:
        result['description'] = desc_match.group(1).strip()

    # タイトルがまだない場合、期限より前をタイトルとする
    if not result['title']:
        due_match = re.search(r'期限[:：]', content)
        if due_match:
            result['title'] = content[:due_match.start()].strip()
        else:
            result['title'] = content.strip()

    return result

def parse_due_date(due_str):
    """期限を解析"""
    today = datetime.now()

    # 今日
    if '今日' in due_str:
        return today.strftime("%Y-%m-%d")

    # 明日
    if '明日' in due_str:
        return (today + timedelta(days=1)).strftime("%Y-%m-%d")

    # 日付形式
    date_match = re.match(r'(\d{4})-(\d{1,2})-(\d{1,2})', due_str)
    if date_match:
        return f"{date_match.group(1)}-{date_match.group(2).zfill(2)}-{date_match.group(3).zfill(2)}"

    date_match = re.match(r'(\d{1,2})/(\d{1,2})', due_str)
    if date_match:
        month = int(date_match.group(1))
        day = int(date_match.group(2))
        return datetime(today.year, month, day).strftime("%Y-%m-%d")

    # 数字 + 日
    days_match = re.match(r'(\d+)日後', due_str)
    if days_match:
        days = int(days_match.group(1))
        return (today + timedelta(days=days)).strftime("%Y-%m-%d")

    # 日曜/月曜など
    weekday_map = {'日': 0, '月': 1, '火': 2, '水': 3, '木': 4, '金': 5, '土': 6}
    for day_name, day_num in weekday_map.items():
        if day_name in due_str:
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

    if action == 'add':
        if not parsed['title']:
            return "❌ タイトルを入力してください"

        todo_id = add_todo(
            parsed['title'],
            parsed['description'],
            parsed['priority'],
            parsed['due_date']
        )

        response = f"✅ タスク #{todo_id} 追加完了\n"
        response += f"タイトル: {parsed['title']}\n"
        if parsed['description']:
            response += f"説明: {parsed['description']}\n"
        if parsed['priority']:
            priority_text = ['低', '中', '高'][parsed['priority'] - 1]
            response += f"優先度: {priority_text}\n"
        if parsed['due_date']:
            response += f"期限: {parsed['due_date']}"

        return response

    elif action == 'complete':
        complete_todo(parsed['todo_id'])
        return f"✅ タスク #{parsed['todo_id']} 完了完了！"

    elif action == 'search':
        keyword = parsed['keyword']
        todos = search_todos(keyword)

        if not todos:
            return f"🔍 「{keyword}」の検索結果: 見つかりませんでした"

        response = f"🔍 「{keyword}」の検索結果 ({len(todos)}件):\n"
        for todo in todos:
            response += format_todo(todo)

        return response

    elif action == 'list':
        todos = list_todos()

        if not todos:
            return "📋 タスクがありません"

        response = f"📋 タスク一覧 ({len(todos)}件):\n"
        for todo in todos:
            response += format_todo(todo)

        return response

    elif action == 'list_pending':
        todos = list_todos(status='pending')

        if not todos:
            return "📋 未完了タスクはありません"

        response = f"📋 未完了タスク ({len(todos)}件):\n"
        for todo in todos:
            response += format_todo(todo)

        return response

    elif action == 'stats':
        stats = get_stats()

        response = "📊 タスク統計:\n"
        response += f"全タスク数: {stats['total']}件\n"
        response += f"未完了: {stats['pending']}件\n"
        response += f"完了: {stats['completed']}件\n"
        response += f"期限切れ: {stats['overdue']}件"

        return response

    return None

def format_todo(todo):
    """タスクをフォーマット"""
    id, title, description, priority, due_date, status, created_at = todo

    # ステータス表示
    status_icon = "✅" if status == 'completed' else ("⏰" if due_date and datetime.strptime(due_date, "%Y-%m-%d") < datetime.now() else "⏳")

    # 優先度表示
    priority_icons = ["", "🟢", "🟡", "🔴"]
    priority_icon = priority_icons[priority] if priority else ""

    # 期限表示
    due_str = f"期限: {due_date}" if due_date else ""

    response = f"\n{status_icon} [{id}] {title} {priority_icon}\n"
    if description:
        response += f"    {description}\n"
    if due_str:
        response += f"    {due_str}\n"

    return response

if __name__ == '__main__':
    # テスト
    init_db()

    test_messages = [
        "タスク: 新機能開発, 優先:高, 期限:明日",
        "タスク: バグ修正, 説明: ログインエラーの修正",
        "タスク: ドキュメント更新, 優先:低",
        "完了: 1",
        "未完了",
        "検索: 機能",
        "統計",
    ]

    for msg in test_messages:
        print(f"\n入力: {msg}")
        result = handle_message(msg)
        if result:
            print(result)
