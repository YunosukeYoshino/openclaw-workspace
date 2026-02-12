#!/usr/bin/env python3
"""
Backup Agent - Discord Integration
Natural Language Processing for Backup Management
"""

import re
from datetime import datetime, timedelta
from db import *

def parse_message(message):
    """Parse message and determine action"""
    # Create backup
    backup_match = re.match(r'(?:バックアップ|backup)[：:]\s*(?:作成|create)[：:]\s*(.+)', message, re.IGNORECASE)
    if backup_match:
        return {'action': 'create_backup', 'content': backup_match.group(1)}

    # Restore backup
    restore_match = re.match(r'(?:リストア|restore|復元)[：:]\s*バックアップ\s*(\d+)[：:]\s*(.+)', message, re.IGNORECASE)
    if restore_match:
        return {'action': 'restore_backup', 'backup_id': int(restore_match.group(1)), 'path': restore_match.group(2)}

    # Create schedule
    schedule_match = re.match(r'(?:スケジュール|schedule)[：:]\s*(?:バックアップ|backup)[：:]\s*(.+)', message, re.IGNORECASE)
    if schedule_match:
        return {'action': 'create_schedule', 'content': schedule_match.group(1)}

    # List backups
    list_match = re.match(r'(?:一覧|list|backups|バックアップ一覧)[：:]?\s*(.+)?', message, re.IGNORECASE)
    if list_match:
        filter_str = list_match.group(1) or ''
        return {'action': 'list_backups', 'filter': filter_str}

    # List schedules
    if re.match(r'(?:スケジュール一覧|list schedules|schedules)', message, re.IGNORECASE):
        return {'action': 'list_schedules'}

    # Delete backup
    delete_match = re.match(r'(?:削除|delete|remove)[：:]\s*バックアップ\s*(\d+)', message, re.IGNORECASE)
    if delete_match:
        return {'action': 'delete_backup', 'backup_id': int(delete_match.group(1))}

    # Cleanup
    cleanup_match = re.match(r'(?:クリーンアップ|cleanup|clean)[：:]?\s*(\d+)?', message, re.IGNORECASE)
    if cleanup_match:
        days = int(cleanup_match.group(1)) if cleanup_match.group(1) else 30
        return {'action': 'cleanup', 'days': days}

    # View restore history
    history_match = re.match(r'(?:履歴|history)[：:]\s*バックアップ\s*(\d+)?', message, re.IGNORECASE)
    if history_match:
        if history_match.group(1):
            return {'action': 'restore_history', 'backup_id': int(history_match.group(1))}
        else:
            return {'action': 'restore_history'}

    # Stats
    if re.match(r'(?:統計|stats)', message, re.IGNORECASE):
        return {'action': 'stats'}

    return None

def parse_backup_content(content):
    """Parse backup creation content"""
    result = {'source_path': None, 'backup_type': 'full', 'compression': 'gzip'}

    # Type
    type_match = re.search(r'(?:タイプ|type)[：:]\s*(full|incremental|differential|完全|増分|差分)', content, re.IGNORECASE)
    if type_match:
        t = type_match.group(1).lower()
        type_map = {'full': 'full', '完全': 'full', 'incremental': 'incremental', '増分': 'incremental', 'differential': 'differential', '差分': 'differential'}
        result['backup_type'] = type_map.get(t, 'full')

    # Compression
    comp_match = re.search(r'(?:圧縮|compression)[：:]\s*(gzip|zip|none|なし)', content, re.IGNORECASE)
    if comp_match:
        c = comp_match.group(1).lower()
        comp_map = {'gzip': 'gzip', 'zip': 'zip', 'none': 'none', 'なし': 'none'}
        result['compression'] = comp_map.get(c, 'gzip')

    # Source path (everything before type/compression)
    for key in ['タイプ', 'type', '圧縮', 'compression']:
        match = re.search(rf'{key}[×:：]', content)
        if match:
            result['source_path'] = content[:match.start()].strip()
            break
    else:
        result['source_path'] = content.strip()

    return result

def parse_schedule_content(content):
    """Parse schedule creation content"""
    result = {'name': None, 'source_path': None, 'schedule_type': 'daily', 'schedule_value': None, 'backup_type': 'full', 'compression': 'gzip', 'retention_days': 30}

    # Schedule type
    sched_match = re.search(r'(?:タイプ|type)[：:]\s*(daily|weekly|monthly|cron|毎日|毎週|毎月)', content, re.IGNORECASE)
    if sched_match:
        t = sched_match.group(1).lower()
        type_map = {'daily': 'daily', '毎日': 'daily', 'weekly': 'weekly', '毎週': 'weekly', 'monthly': 'monthly', '毎月': 'monthly', 'cron': 'cron'}
        result['schedule_type'] = type_map.get(t, 'daily')

    # Schedule value (time, day, etc.)
    value_match = re.search(r'(?:時間|time|value|曜日|day)[：:]\s*(.+)', content, re.IGNORECASE)
    if value_match and 'retention' not in value_match.group(0).lower():
        result['schedule_value'] = value_match.group(1).strip()

    # Retention days
    retention_match = re.search(r'(?:保持|retention|keep)[：:]\s*(\d+)', content, re.IGNORECASE)
    if retention_match:
        result['retention_days'] = int(retention_match.group(1))

    # Backup type
    backup_type_match = re.search(r'(?:バックアップタイプ|backup type)[：:]\s*(full|incremental|differential)', content, re.IGNORECASE)
    if backup_type_match:
        result['backup_type'] = backup_type_match.group(1).lower()

    # Compression
    comp_match = re.search(r'(?:圧縮|compression)[：:]\s*(gzip|zip|none)', content, re.IGNORECASE)
    if comp_match:
        result['compression'] = comp_match.group(1).lower()

    # Source path
    for key in ['タイプ', 'type', '時間', 'time', 'value', '曜日', 'day', '保持', 'retention', 'keep', 'バックアップタイプ', 'backup type', '圧縮', 'compression']:
        match = re.search(rf'{key}[×:：]', content)
        if match:
            result['source_path'] = content[:match.start()].strip()
            break
    else:
        result['source_path'] = content.strip()

    # Name (first part)
    result['name'] = result['source_path'].split()[0] if result['source_path'] else 'Backup Schedule'

    return result

def parse_backup_filter(filter_str):
    """Parse backup list filter"""
    result = {'status': None, 'source_path': None}

    f = filter_str.lower()

    if 'completed' in f or '完了' in f or '成功' in f:
        result['status'] = 'completed'
    elif 'failed' in f or '失敗' in f:
        result['status'] = 'failed'
    elif 'running' in f or '実行中' in f:
        result['status'] = 'running'

    # Extract path from filter
    path_match = re.search(r'(?:パス|path|from)[：:]\s*(.+)', filter_str, re.IGNORECASE)
    if path_match:
        result['source_path'] = path_match.group(1).strip()

    return result

def format_size(size_bytes):
    """Format size in human readable format"""
    if size_bytes is None:
        return "N/A"

    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"

def process_action(parsed, user_id):
    """Process the parsed action and return response"""
    try:
        if parsed['action'] == 'create_backup':
            backup_data = parse_backup_content(parsed['content'])
            backup_id, backup_path, checksum = create_backup(**backup_data)

            # Get backup info for display
            backups = get_backups()
            backup_info = next((b for b in backups if b[0] == backup_id), None)
            size_str = format_size(backup_info[4]) if backup_info else "N/A"

            return {
                'status': 'success',
                'message_ja': f'バックアップ #{backup_id} を作成しました\nサイズ: {size_str}\nチェックサム: {checksum[:16]}...',
                'message_en': f'Backup #{backup_id} created\nSize: {size_str}\nChecksum: {checksum[:16]}...',
                'backup_id': backup_id,
                'backup_path': backup_path
            }

        elif parsed['action'] == 'restore_backup':
            restore_id = restore_backup(parsed['backup_id'], parsed['path'])
            return {
                'status': 'success',
                'message_ja': f'バックアップ #{parsed["backup_id"]} を {parsed["path"]} にリストアしました',
                'message_en': f'Restored backup #{parsed["backup_id"]} to {parsed["path"]}',
                'restore_id': restore_id
            }

        elif parsed['action'] == 'create_schedule':
            schedule_data = parse_schedule_content(parsed['content'])
            schedule_id = create_schedule(**schedule_data)
            return {
                'status': 'success',
                'message_ja': f'バックアップスケジュール #{schedule_id} を作成しました',
                'message_en': f'Backup schedule #{schedule_id} created',
                'schedule_id': schedule_id
            }

        elif parsed['action'] == 'list_backups':
            filters = parse_backup_filter(parsed['filter'])
            backups = get_backups(**filters)

            items = []
            for b in backups:
                size_str = format_size(b[4])
                items.append(f"#{b[0]}: {b[1]} ({b[2]}, {b[3]}, {size_str}, {b[6]})")

            backup_list = '\n'.join(items)
            return {
                'status': 'success',
                'message_ja': f'バックアップ一覧:\n{backup_list}',
                'message_en': f'Backup list:\n{backup_list}'
            }

        elif parsed['action'] == 'list_schedules':
            schedules = get_schedules()
            schedule_list = '\n'.join([f"#{s[0]}: {s[1]} - {s[2]} ({s[3]}, {s[5]} → {s[6]})" for s in schedules])
            return {
                'status': 'success',
                'message_ja': f'バックアップスケジュール一覧:\n{schedule_list}',
                'message_en': f'Backup schedule list:\n{schedule_list}'
            }

        elif parsed['action'] == 'delete_backup':
            delete_backup(parsed['backup_id'])
            return {
                'status': 'success',
                'message_ja': f'バックアップ #{parsed["backup_id"]} を削除しました',
                'message_en': f'Backup #{parsed["backup_id"]} deleted'
            }

        elif parsed['action'] == 'cleanup':
            deleted = cleanup_old_backups(parsed['days'])
            return {
                'status': 'success',
                'message_ja': f'{parsed["days"]}日以前のバックアップ {deleted}件を削除しました',
                'message_en': f'Deleted {deleted} backups older than {parsed["days"]} days'
            }

        elif parsed['action'] == 'restore_history':
            restores = get_restores(parsed.get('backup_id'))
            history_list = '\n'.join([f"リストア #{r[0]}: バックアップ#{r[1]} → {r[2]} ({r[3]}, {r[4]})" for r in restores])
            return {
                'status': 'success',
                'message_ja': f'リストア履歴:\n{history_list}',
                'message_en': f'Restore history:\n{history_list}'
            }

        elif parsed['action'] == 'stats':
            stats = get_stats()
            size_str = format_size(stats['total_size_bytes'])
            return {
                'status': 'success',
                'message_ja': f'統計: ステータス={stats["status_counts"]}, 総サイズ={size_str}, アクティブなスケジュール={stats["active_schedules"]}, 最近のリストア={stats["recent_restores"]}',
                'message_en': f'Stats: Status={stats["status_counts"]}, Total size={size_str}, Active schedules={stats["active_schedules"]}, Recent restores={stats["recent_restores"]}',
                'stats': stats
            }

        return {
            'status': 'error',
            'message_ja': '不明なアクションです',
            'message_en': 'Unknown action'
        }

    except Exception as e:
        return {
            'status': 'error',
            'message_ja': f'エラーが発生しました: {str(e)}',
            'message_en': f'Error occurred: {str(e)}'
        }

if __name__ == '__main__':
    init_db()
