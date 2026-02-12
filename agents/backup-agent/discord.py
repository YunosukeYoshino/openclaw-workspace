#!/usr/bin/env python3
"""
Backup Agent - Discord Integration
"""

import re
from datetime import datetime, timedelta
from db import *

def parse_message(message):
    """Parse message"""
    # Create backup
    backup_match = re.match(r'(?:バックアップ|backup|create)[:：]\s*(.+)', message, re.IGNORECASE)
    if backup_match:
        return parse_backup(backup_match.group(1))

    # Restore backup
    restore_match = re.match(r'(?:復元|restore)[:：]\s*(\d+)\s*(?:to|:)\s*(.+)', message, re.IGNORECASE)
    if restore_match:
        return {'action': 'restore', 'backup_id': int(restore_match.group(1)), 'path': restore_match.group(2).strip()}

    # Create schedule
    schedule_match = re.match(r'(?:スケジュール|schedule)[:：]\s*(.+)', message, re.IGNORECASE)
    if schedule_match:
        return parse_schedule(schedule_match.group(1))

    # List backups
    list_backup_match = re.match(r'(?:バックアップ一覧|backups|list-backups)(?:[:：]\s*(.+))?', message, re.IGNORECASE)
    if list_backup_match:
        return {'action': 'list_backups', 'status': list_backup_match.group(1)}

    # List schedules
    if message.strip() in ['スケジュール一覧', 'schedules']:
        return {'action': 'list_schedules'}

    # Delete backup
    delete_match = re.match(r'(?:削除|delete)[:：]\s*backup\s*[:：]\s*(\d+)', message, re.IGNORECASE)
    if delete_match:
        return {'action': 'delete_backup', 'backup_id': int(delete_match.group(1))}

    # Stats
    if message.strip() in ['統計', 'stats']:
        return {'action': 'stats'}

    return None

def parse_backup(content):
    """Parse backup content"""
    result = {'action': 'create_backup', 'source': None, 'type': 'full', 'compression': 'gzip'}

    # Source
    source_match = re.match(r'^([^,、]+)', content)
    if source_match:
        result['source'] = source_match.group(1).strip()

    # Backup type
    type_match = re.search(r'タイプ|type[:：]\s*(.+?)(?:[,，]|$)', content)
    if type_match:
        result['type'] = type_match.group(1).strip()

    # Compression
    comp_match = re.search(r'圧縮|compression[:：]\s*(.+?)(?:[,，]|$)', content)
    if comp_match:
        result['compression'] = comp_match.group(1).strip()

    return result

def parse_schedule(content):
    """Parse schedule content"""
    result = {'action': 'create_schedule', 'name': None, 'source': None, 'type': 'daily', 'value': None}

    # Name
    name_match = re.match(r'^([^,、]+)', content)
    if name_match:
        result['name'] = name_match.group(1).strip()

    # Source
    source_match = re.search(r'ソース|source[:：]\s*(.+?)(?:[,，]|$)', content)
    if source_match:
        result['source'] = source_match.group(1).strip()

    # Schedule type
    type_match = re.search(r'タイプ|type[:：]\s*(.+?)(?:[,，]|$)', content)
    if type_match:
        result['type'] = type_match.group(1).strip()

    # Schedule value
    value_match = re.search(r'値|value[:：]\s*(.+?)(?:[,，]|$)', content)
    if value_match:
        result['value'] = value_match.group(1).strip()

    return result

def handle_message(message):
    """Handle message"""
    parsed = parse_message(message)

    if not parsed:
        return None

    action = parsed['action']

    if action == 'create_backup':
        try:
            backup_id, path, checksum = create_backup(
                parsed.get('source') or '.',
                parsed.get('type', 'full'),
                parsed.get('compression', 'gzip')
            )

            response = f"✅ バックアップ #{backup_id} 作成完了\n"
            response += f"ソース: {parsed.get('source', '.')}\n"
            response += f"タイプ: {parsed.get('type', 'full')}\n"
            response += f"パス: {path}"

            return response
        except Exception as e:
            return f"❌ バックアップ作成失敗: {str(e)}"

    elif action == 'restore':
        try:
            restore_id = restore_backup(parsed['backup_id'], parsed['path'])
            return f"✅ 復元 #{restore_id} 完了: バックアップ #{parsed['backup_id']} を {parsed['path']} に復元"
        except Exception as e:
            return f"❌ 復元失敗: {str(e)}"

    elif action == 'create_schedule':
        schedule_id = create_schedule(
            parsed.get('name') or 'Unnamed Schedule',
            parsed.get('source') or '.',
            parsed.get('type', 'daily'),
            parsed.get('value'),
            parsed.get('type', 'full'),
            'gzip'
        )

        response = f"✅ スケジュール #{schedule_id} 作成完了\n"
        response += f"名前: {parsed.get('name', 'Unnamed Schedule')}\n"
        response += f"タイプ: {parsed.get('type', 'daily')}"

        return response

    elif action == 'list_backups':
        backups = get_backups(status=parsed.get('status'))

        if not backups:
            status_text = f" ({parsed['status']})" if parsed.get('status') else ""
            return f"💾 バックアップ{status_text} がありません"

        status_text = f" ({parsed['status']})" if parsed.get('status') else ""
        response = f"💾 バックアップ一覧{status_text} ({len(backups)}件):\n"
        for backup in backups[:10]:
            size_mb = backup[4] / (1024 * 1024) if backup[4] else 0
            response += f"\n💾 [{backup[0]}] {backup[1]} - {backup[2]} ({size_mb:.2f}MB)\n   ファイル: {backup[3]}"

        return response

    elif action == 'list_schedules':
        schedules = get_schedules(active_only=True)

        if not schedules:
            return "📅 スケジュールがありません"

        response = f"📅 スケジュール一覧 ({len(schedules)}件):\n"
        for sched in schedules:
            response += f"\n📅 [{sched[0]}] {sched[1]} - {sched[2]} ({sched[3]})\n   次回: {sched[6]}"

        return response

    elif action == 'delete_backup':
        delete_backup(parsed['backup_id'])
        return f"🗑️ バックアップ #{parsed['backup_id']} を削除"

    elif action == 'stats':
        stats = get_stats()

        response = "📊 バックアップ統計:\n"
        response += f"ステータス別: {stats['status_counts']}\n"
        total_gb = stats['total_size_bytes'] / (1024**3)
        response += f"総サイズ: {total_gb:.2f}GB\n"
        response += f"アクティブなスケジュール: {stats['active_schedules']}件\n"
        response += f"最近の復元: {stats['recent_restores']}件"

        return response

    return None

if __name__ == '__main__':
    init_db()

    test_messages = [
        "バックアップ: /home/user/data, タイプ:full",
        "復元: 1 to /home/user/restore",
        "スケジュール: Daily Backup, ソース:/home/user/data, タイプ:daily, 値:02:00",
        "バックアップ一覧",
        "スケジュール一覧",
        "削除: backup : 1",
        "統計",
    ]

    for msg in test_messages:
        print(f"\n入力: {msg}")
        result = handle_message(msg)
        if result:
            print(result)
