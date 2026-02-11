#!/usr/bin/env python3
"""
Automation Agent - Discord Integration
"""

import re
from datetime import datetime
from db import AutomationDB

db = AutomationDB()

def parse_message(message):
    """Parse message"""
    # Create task
    task_match = re.match(r'(?:タスク|task|add-task)[:：]\s*(.+)', message, re.IGNORECASE)
    if task_match:
        return parse_task(task_match.group(1))

    # Create workflow
    workflow_match = re.match(r'(?:ワークフロー|workflow|add-workflow)[:：]\s*(.+)', message, re.IGNORECASE)
    if workflow_match:
        return {'action': 'create_workflow', 'name': workflow_match.group(1).strip()}

    # Create trigger
    trigger_match = re.match(r'(?:トリガー|trigger|add-trigger)[:：]\s*(.+)', message, re.IGNORECASE)
    if trigger_match:
        return parse_trigger(trigger_match.group(1))

    # Toggle task
    toggle_match = re.match(r'(?:有効|無効|enable|disable|toggle)[:：]\s*task\s*[:：]\s*(\d+)', message, re.IGNORECASE)
    if toggle_match:
        return {'action': 'toggle_task', 'task_id': int(toggle_match.group(1)), 'enable': 'enable' in message.lower()}

    # List tasks
    if message.strip() in ['タスク一覧', 'tasks', 'list-tasks']:
        return {'action': 'list_tasks'}

    # List workflows
    if message.strip() in ['ワークフロー一覧', 'workflows', 'list-workflows']:
        return {'action': 'list_workflows'}

    # List triggers
    if message.strip() in ['トリガー一覧', 'triggers', 'list-triggers']:
        return {'action': 'list_triggers'}

    # List executions
    list_exec_match = re.match(r'(?:実行履歴|executions|history)(?:[:：]\s*(\d+))?', message, re.IGNORECASE)
    if list_exec_match:
        limit = int(list_exec_match.group(1)) if list_exec_match.group(1) else 20
        return {'action': 'list_executions', 'limit': limit}

    # Stats
    if message.strip() in ['統計', 'stats']:
        return {'action': 'stats'}

    return None

def parse_task(content):
    """Parse task content"""
    result = {'action': 'create_task', 'name': None, 'task_type': None, 'config': {}, 'description': None}

    # Name (first part)
    name_match = re.match(r'^([^,、（\(【♪]+)', content)
    if name_match:
        result['name'] = name_match.group(1).strip()

    # Task type
    type_match = re.search(r'タイプ|type[:：]\s*(.+?)(?:[,，]|$)', content)
    if type_match:
        result['task_type'] = type_match.group(1).strip()

    # Description
    desc_match = re.search(r'説明|description[:：]\s*(.+)', content)
    if desc_match:
        result['description'] = desc_match.group(1).strip()

    # If name not set, use first part
    if not result['name']:
        parts = content.split(',')
        if parts:
            result['name'] = parts[0].strip()

    return result

def parse_trigger(content):
    """Parse trigger content"""
    result = {'action': 'create_trigger', 'name': None, 'trigger_type': None, 'config': {}, 'target_task': None, 'target_workflow': None}

    # Name
    name_match = re.match(r'^([^,、]+)', content)
    if name_match:
        result['name'] = name_match.group(1).strip()

    # Trigger type
    type_match = re.search(r'タイプ|type[:：]\s*(.+?)(?:[,，]|$)', content)
    if type_match:
        result['trigger_type'] = type_match.group(1).strip()

    # Target task
    task_match = re.search(r'タスク|task[:：]\s*(\d+)', content)
    if task_match:
        result['target_task'] = int(task_match.group(1))

    # Target workflow
    wf_match = re.search(r'ワークフロー|workflow[:：]\s*(\d+)', content)
    if wf_match:
        result['target_workflow'] = int(wf_match.group(1))

    return result

def handle_message(message):
    """Handle message"""
    parsed = parse_message(message)

    if not parsed:
        return None

    action = parsed['action']

    if action == 'create_task':
        task_id = db.create_task(
            parsed.get('name') or 'Unnamed Task',
            parsed.get('task_type') or 'manual',
            parsed.get('config', {}),
            parsed.get('description')
        )

        response = f"✅ タスク #{task_id} 作成完了\n"
        response += f"名前: {parsed.get('name', 'Unnamed Task')}\n"
        if parsed.get('task_type'):
            response += f"タイプ: {parsed['task_type']}"
        if parsed.get('description'):
            response += f"\n説明: {parsed['description']}"

        return response

    elif action == 'create_workflow':
        import json
        workflow_id = db.create_workflow(
            parsed['name'],
            [],
            f"Workflow created on {datetime.now().strftime('%Y-%m-%d')}"
        )

        return f"✅ ワークフロー #{workflow_id} 作成完了: {parsed['name']}"

    elif action == 'create_trigger':
        import json
        trigger_id = db.create_trigger(
            parsed.get('name') or 'Unnamed Trigger',
            parsed.get('trigger_type') or 'manual',
            parsed.get('config', {}),
            parsed.get('target_task'),
            parsed.get('target_workflow')
        )

        return f"✅ トリガー #{trigger_id} 作成完了: {parsed.get('name', 'Unnamed Trigger')}"

    elif action == 'toggle_task':
        db.update_task(parsed['task_id'], enabled=parsed['enable'])
        status = "有効" if parsed['enable'] else "無効"
        return f"✅ タスク #{parsed['task_id']} を{status}に変更"

    elif action == 'list_tasks':
        tasks = db.get_tasks()

        if not tasks:
            return "📋 タスクがありません"

        response = f"📋 タスク一覧 ({len(tasks)}件):\n"
        for i, task in enumerate(tasks[:20], 1):
            status = "✅" if task['enabled'] else "❌"
            response += f"\n{i}. {status} [{task['id']}] {task['name']} ({task['task_type']})"

        return response

    elif action == 'list_workflows':
        workflows = db.get_workflows()

        if not workflows:
            return "🔄 ワークフローがありません"

        response = f"🔄 ワークフロー一覧 ({len(workflows)}件):\n"
        for i, wf in enumerate(workflows[:20], 1):
            status = "✅" if wf['enabled'] else "❌"
            response += f"\n{i}. {status} [{wf['id']}] {wf['name']}"

        return response

    elif action == 'list_triggers':
        triggers = db.get_triggers()

        if not triggers:
            return "⏰ トリガーがありません"

        response = f"⏰ トリガー一覧 ({len(triggers)}件):\n"
        for i, trig in enumerate(triggers[:20], 1):
            status = "✅" if trig['enabled'] else "❌"
            response += f"\n{i}. {status} [{trig['id']}] {trig['name']} ({trig['trigger_type']})"

        return response

    elif action == 'list_executions':
        executions = db.get_executions(limit=parsed.get('limit', 20))

        if not executions:
            return "📜 実行履歴がありません"

        response = f"📜 実行履歴 (最新{len(executions)}件):\n"
        for i, exec in enumerate(executions[:20], 1):
            status_icon = "✅" if exec['status'] == 'completed' else ("❌" if exec['status'] == 'failed' else "⏳")
            target = f"Task {exec['task_id']}" if exec['task_id'] else f"Workflow {exec['workflow_id']}"
            response += f"\n{i}. {status_icon} [{exec['id']}] {target} - {exec['status']}"

        return response

    elif action == 'stats':
        stats = db.get_statistics()

        response = "📊 自動化統計:\n"
        response += f"タスク: {stats['tasks']['total']}件 (有効: {stats['tasks']['enabled']}件)\n"
        response += f"ワークフロー: {stats['workflows']}件\n"
        response += f"トリガー: {stats['triggers']}件\n"
        response += f"実行状況: {stats.get('executions', {})}"

        return response

    return None

if __name__ == '__main__':
    db.init_db()

    test_messages = [
        "タスク: Daily Backup, タイプ:scheduled",
        "ワークフロー: Data Processing Pipeline",
        "トリガー: Morning Backup, タイプ:cron, タスク:1",
        "有効: task : 1",
        "タスク一覧",
        "ワークフロー一覧",
        "実行履歴",
        "統計",
    ]

    for msg in test_messages:
        print(f"\n入力: {msg}")
        result = handle_message(msg)
        if result:
            print(result)
