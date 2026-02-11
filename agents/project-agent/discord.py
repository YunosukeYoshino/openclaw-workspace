#!/usr/bin/env python3
"""
プロジェクト管理エージェント #12 - Discord連携
"""

import re
from db import *

def parse_message(message):
    """メッセージを解析"""
    # プロジェクト追加
    project_match = re.match(r'(?:プロジェクト|project)[:：]\s*(.+)', message, re.IGNORECASE)
    if project_match:
        return parse_project(project_match.group(1))

    # タスク追加
    task_match = re.match(r'(?:タスク|task)[:：]\s*(.+)', message, re.IGNORECASE)
    if task_match:
        return parse_task(task_match.group(1))

    # プロジェクト完了
    complete_proj_match = re.match(r'(?:プロジェクト完了|project done)[:：]\s*(\d+)', message, re.IGNORECASE)
    if complete_proj_match:
        return {'action': 'complete_project', 'project_id': int(complete_proj_match.group(1))}

    # タスク完了
    complete_task_match = re.match(r'(?:タスク完了|task done)[:：]\s*(\d+)', message, re.IGNORECASE)
    if complete_task_match:
        return {'action': 'complete_task', 'task_id': int(complete_task_match.group(1))}

    # プロジェクト一覧
    if message.strip() in ['プロジェクト一覧', '一覧', 'list', 'projects']:
        return {'action': 'list_projects'}

    # プロジェクト詳細
    detail_match = re.match(r'(?:詳細|detail)[:：]\s*(\d+)', message, re.IGNORECASE)
    if detail_match:
        return {'action': 'detail', 'project_id': int(detail_match.group(1))}

    return None

def parse_project(content):
    """プロジェクトを解析"""
    result = {'action': 'add_project', 'name': None, 'description': None}

    # 名前 (最初の部分)
    name_match = re.match(r'^([^、,（\(【♪]+)', content)
    if name_match:
        result['name'] = name_match.group(1).strip()
        content = content.replace(name_match.group(0), '').strip()

    # 説明
    desc_match = re.search(r'説明[:：]\s*(.+)', content)
    if desc_match:
        result['description'] = desc_match.group(1).strip()

    return result

def parse_task(content):
    """タスクを解析"""
    result = {'action': 'add_task', 'project_id': None, 'title': None, 'priority': 2, 'due_date': None}

    # プロジェクトID
    proj_match = re.match(r'^(\d+)', content)
    if proj_match:
        result['project_id'] = int(proj_match.group(1))
        content = content.replace(proj_match.group(0), '').strip()

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
    due_match = re.search(r'期限[:：]\s*([^、,]+)', content)
    if due_match:
        result['due_date'] = due_match.group(1).strip()

    # タイトル
    if not result['title']:
        due_match = re.search(r'期限[:：]', content)
        if due_match:
            result['title'] = content[:due_match.start()].strip()
        else:
            result['title'] = content.strip()

    return result

def handle_message(message):
    """メッセージを処理"""
    parsed = parse_message(message)

    if not parsed:
        return None

    action = parsed['action']

    if action == 'add_project':
        if not parsed['name']:
            return "❌ プロジェクト名を入力してください"

        project_id = add_project(parsed['name'], parsed['description'])

        response = f"📊 プロジェクト #{project_id} 追加完了\n"
        response += f"名前: {parsed['name']}"
        if parsed['description']:
            response += f"\n説明: {parsed['description']}"

        return response

    elif action == 'add_task':
        if not parsed['project_id'] or not parsed['title']:
            return "❌ プロジェクトIDとタスク名を入力してください"

        task_id = add_task(parsed['project_id'], parsed['title'], parsed['priority'], parsed['due_date'])

        response = f"✅ タスク #{task_id} 追加完了\n"
        response += f"プロジェクト #{parsed['project_id']}\n"
        response += f"タイトル: {parsed['title']}"
        if parsed['due_date']:
            response += f"\n期限: {parsed['due_date']}"

        return response

    elif action == 'complete_project':
        update_project_status(parsed['project_id'], 'completed')
        return f"🎉 プロジェクト #{parsed['project_id']} 完了！"

    elif action == 'complete_task':
        update_task_status(parsed['task_id'], 'completed')
        return f"✅ タスク #{parsed['task_id']} 完了！"

    elif action == 'list_projects':
        projects = list_projects()

        if not projects:
            return "📊 プロジェクトがありません"

        response = f"📊 プロジェクト一覧 ({len(projects)}件):\n"
        for project in projects:
            response += format_project(project)

        return response

    elif action == 'detail':
        project = get_project_tasks(parsed['project_id'])

        if not project:
            return f"❌ プロジェクト #{parsed['project_id']} のタスクがありません"

        response = f"📊 プロジェクト #{parsed['project_id']} タスク ({len(project)}件):\n"
        for task in project:
            response += format_task(task)

        return response

    return None

def format_project(project):
    """プロジェクトをフォーマット"""
    id, name, description, status, progress, created_at = project

    status_icons = {'active': '🟢', 'paused': '🟡', 'completed': '✅', 'cancelled': '❌'}
    status_icon = status_icons.get(status, '❓')

    response = f"\n{status_icon} [{id}] {name}\n"
    if description:
        response += f"    説明: {description}\n"
    response += f"    進捗: {progress}%"

    return response

def format_task(task):
    """タスクをフォーマット"""
    id, title, status, priority, due_date, created_at = task

    status_icons = {'pending': '⏳', 'in_progress': '🔄', 'completed': '✅', 'cancelled': '❌'}
    priority_icons = ["", "🟢", "🟡", "🔴"]

    response = f"\n{status_icons.get(status, '❓')} [{id}] {title}"
    if priority_icons[priority]:
        response += f" {priority_icons[priority]}"
    if due_date:
        response += f"\n    期限: {due_date}"

    return response

if __name__ == '__main__':
    # テスト
    init_db()

    test_messages = [
        "プロジェクト: 新しいアプリ開発, 説明: AIエージェント100個作る",
        "タスク: 1 ようやく, 優先:高, 期限: 明日",
        "プロジェクト一覧",
        "詳細: 1",
        "タスク完了: 1",
    ]

    for msg in test_messages:
        print(f"\n入力: {msg}")
        result = handle_message(msg)
        if result:
            print(result)
