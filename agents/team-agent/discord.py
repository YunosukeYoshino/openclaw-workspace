#!/usr/bin/env python3
"""
Team Agent #25 - Discord Integration
"""

import re
from db import *

def parse_message(message):
    """Parse message"""
    # Add member
    add_match = re.match(r'(?:追加|add|新規|new)[:：]\s*(.+)', message, re.IGNORECASE)
    if add_match:
        return parse_add(add_match.group(1))

    # Update status
    status_match = re.match(r'(?:ステータス|status)[:：]\s*(\d+)\s*[,，]\s*(\w+)', message, re.IGNORECASE)
    if status_match:
        return {'action': 'update_status', 'member_id': int(status_match.group(1)), 'status': status_match.group(2)}

    # Assign task
    task_match = re.match(r'(?:タスク|task|担当)[:：]\s*(\d+)\s*[,，]\s*(.+)', message, re.IGNORECASE)
    if task_match:
        return {'action': 'assign_task', 'member_id': int(task_match.group(1)), 'task': task_match.group(2)}

    # List
    list_match = re.match(r'(?:一覧|list)(?:[:：]\s*(\w+))?', message, re.IGNORECASE)
    if list_match:
        dept = list_match.group(1) if list_match.group(1) else None
        return {'action': 'list', 'department': dept}

    # Search
    search_match = re.match(r'(?:検索|search)[:：]\s*(.+)', message, re.IGNORECASE)
    if search_match:
        return {'action': 'search', 'keyword': search_match.group(1)}

    # View tasks
    view_match = re.match(r'(?:タスク一覧|tasks|view)[:：]\s*(\d+)', message, re.IGNORECASE)
    if view_match:
        return {'action': 'view_tasks', 'member_id': int(view_match.group(1))}

    # Complete task
    complete_match = re.match(r'(?:完了|done|complete)[:：]\s*(\d+)', message, re.IGNORECASE)
    if complete_match:
        return {'action': 'complete_task', 'task_id': int(complete_match.group(1))}

    # Stats
    if message.strip() in ['統計', 'stats']:
        return {'action': 'stats'}

    return None

def parse_add(content):
    """Parse add content"""
    result = {'action': 'add', 'name': None, 'role': None, 'email': None, 'phone': None, 'department': None, 'skills': None, 'notes': None}

    # Name
    name_match = re.match(r'^([^、,]+)', content)
    if name_match:
        result['name'] = name_match.group(1).strip()

    # Role
    role_match = re.search(r'役割|ロール|role[:：]\s*(.+?)(?:[、,]|$)', content)
    if role_match:
        result['role'] = role_match.group(1).strip()

    # Department
    dept_match = re.search(r'部署|department[:：]\s*(.+?)(?:[、,]|$)', content)
    if dept_match:
        result['department'] = dept_match.group(1).strip()

    # Email
    email_match = re.search(r'メール|email[:：]\s*([\w\.-@]+)', content)
    if email_match:
        result['email'] = email_match.group(1).strip()

    # Phone
    phone_match = re.search(r'電話|phone[:：]\s*([\d-]+)', content)
    if phone_match:
        result['phone'] = phone_match.group(1).strip()

    # Skills
    skills_match = re.search(r'スキル|skills[:：]\s*(.+)', content)
    if skills_match:
        result['skills'] = skills_match.group(1).strip()

    # Notes
    note_match = re.search(r'メモ|notes[:：]\s*(.+)', content)
    if note_match:
        result['notes'] = note_match.group(1).strip()

    return result

def handle_message(message):
    """Handle message"""
    parsed = parse_message(message)

    if not parsed:
        return None

    action = parsed['action']

    if action == 'add':
        if not parsed['name']:
            return "❌ 名前を入力してください"

        member_id = add_member(
            parsed['name'],
            parsed['role'],
            parsed['email'],
            parsed['phone'],
            parsed['department'],
            parsed['skills'],
            notes=parsed['notes']
        )

        response = f"✅ メンバー #{member_id} 追加完了\n"
        response += f"名前: {parsed['name']}\n"
        if parsed['role']:
            response += f"役割: {parsed['role']}\n"
        if parsed['department']:
            response += f"部署: {parsed['department']}"

        return response

    elif action == 'update_status':
        status_map = {'active': 'active', 'inactive': 'inactive', 'on_leave': 'on_leave', 'leave': 'on_leave'}
        status = status_map.get(parsed['status'].lower(), parsed['status'])
        update_status(parsed['member_id'], status)
        return f"✅ メンバー #{parsed['member_id']} のステータスを {status} に更新"

    elif action == 'assign_task':
        task_id = assign_task(parsed['member_id'], parsed['task'])
        return f"📋 メンバー #{parsed['member_id']} にタスク #{task_id} を割り当て: {parsed['task']}"

    elif action == 'complete_task':
        complete_task(parsed['task_id'])
        return f"✅ タスク #{parsed['task_id']} 完了！"

    elif action == 'list':
        members = list_members(department=parsed['department'])

        if not members:
            return f"👥 メンバーがいません"

        dept_text = f" ({parsed['department']})" if parsed['department'] else ""
        response = f"👥 一覧{dept_text} ({len(members)}件):\n"
        for member in members:
            response += format_member(member)

        return response

    elif action == 'search':
        members = search_members(parsed['keyword'])

        if not members:
            return f"🔍 「{parsed['keyword']}」の検索結果: 見つかりませんでした"

        response = f"🔍 「{parsed['keyword']}」の検索結果 ({len(members)}件):\n"
        for member in members:
            response += format_member(member)

        return response

    elif action == 'view_tasks':
        tasks = get_member_tasks(parsed['member_id'])

        if not tasks:
            return f"📋 メンバー #{parsed['member_id']} のタスクはありません"

        response = f"📋 メンバー #{parsed['member_id']} のタスク ({len(tasks)}件):\n"
        for task in tasks:
            response += format_task(task)

        return response

    elif action == 'stats':
        stats = get_stats()

        response = "📊 チーム統計:\n"
        response += f"全メンバー: {stats['total_members']}人\n"
        response += f"アクティブ: {stats['active']}人\n"
        response += f"非アクティブ: {stats['inactive']}人\n"
        response += f"休暇中: {stats['on_leave']}人\n"
        response += f"保留タスク: {stats['pending_tasks']}件\n"
        response += f"完了タスク: {stats['completed_tasks']}件"

        return response

    return None

def format_member(member):
    """Format member"""
    id, name, role, email, phone, department, status, skills, joined_at, created_at = member

    status_map = {'active': '🟢', 'inactive': '⚪', 'on_leave': '🟡'}
    status_icon = status_map.get(status, '❓')

    response = f"\n{status_icon} [{id}] {name}\n"
    if role:
        response += f"    役割: {role}\n"
    if department:
        response += f"    部署: {department}\n"

    return response

def format_task(task):
    """Format task"""
    id, task_text, status, due_date, created_at, completed_at = task

    status_map = {'pending': '⏳', 'in_progress': '🔄', 'completed': '✅'}
    status_icon = status_map.get(status, '❓')

    response = f"\n{status_icon} [{id}] {task_text}"
    if due_date:
        response += f" (期限: {due_date})"
    response += "\n"

    return response

if __name__ == '__main__':
    init_db()

    test_messages = [
        "追加: 田中太郎, 役割: エンジニア, 部署: 開発",
        "追加: 佐藤花子, 役割: デザイナー, 部署: デザイン",
        "一覧",
        "一覧: 開発",
        "タスク: 1, 新機能の実装",
        "タスク一覧: 1",
        "完了: 1",
        "検索: エンジニア",
        "統計",
    ]

    for msg in test_messages:
        print(f"\n入力: {msg}")
        result = handle_message(msg)
        if result:
            print(result)
