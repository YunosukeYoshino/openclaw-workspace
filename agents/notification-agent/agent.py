#!/usr/bin/env python3
"""
Notification Agent - Discord Integration
Natural Language Processing for Notification Management
"""

import re
from datetime import datetime, timedelta
from db import *

def parse_message(message):
    """Parse message and determine action"""
    # Add notification
    add_match = re.match(r'(?:通知|notification|notify)[：:]\s*(.+)', message, re.IGNORECASE)
    if add_match:
        return {'action': 'add_notification', 'content': add_match.group(1)}

    # List notifications
    list_match = re.match(r'(?:一覧|list|notifications)[：:]?\s*(.+)?', message, re.IGNORECASE)
    if list_match:
        filter_str = list_match.group(1) or ''
        return {'action': 'list_notifications', 'filter': filter_str}

    # Mark read
    read_match = re.match(r'(?:既読|read|mark read)[：:]\s*通知\s*(\d+)?', message, re.IGNORECASE)
    if read_match:
        if read_match.group(1):
            return {'action': 'mark_read', 'notification_id': int(read_match.group(1))}
        else:
            return {'action': 'mark_all_read'}

    # Archive
    archive_match = re.match(r'(?:アーカイブ|archive)[：:]\s*通知\s*(\d+)', message, re.IGNORECASE)
    if archive_match:
        return {'action': 'archive', 'notification_id': int(archive_match.group(1))}

    # Dismiss
    dismiss_match = re.match(r'(?:却下|dismiss|clear)[：:]\s*通知\s*(\d+)', message, re.IGNORECASE)
    if dismiss_match:
        return {'action': 'dismiss', 'notification_id': int(dismiss_match.group(1))}

    # Create schedule
    schedule_match = re.match(r'(?:スケジュール|schedule)[：:]\s*(?:通知|notification)[：:]\s*(.+)', message, re.IGNORECASE)
    if schedule_match:
        return {'action': 'create_schedule', 'content': schedule_match.group(1)}

    # List schedules
    if re.match(r'(?:スケジュール一覧|list schedules|schedules)', message, re.IGNORECASE):
        return {'action': 'list_schedules'}

    # Create rule
    rule_match = re.match(r'(?:ルール|rule)[：:]\s*(?:追加|add|create)[：:]\s*(.+)', message, re.IGNORECASE)
    if rule_match:
        return {'action': 'create_rule', 'content': rule_match.group(1)}

    # Stats
    if re.match(r'(?:統計|stats)', message, re.IGNORECASE):
        return {'action': 'stats'}

    return None

def parse_notification_content(content, user_id=None):
    """Parse notification addition content"""
    result = {'source': 'discord', 'title': None, 'message': None, 'type': 'info', 'priority': 'normal', 'target_user': user_id, 'scheduled_at': None, 'expires_at': None}

    # Type
    type_match = re.search(r'(?:タイプ|type)[：:]\s*(info|warning|error|success|reminder|情報|警告|エラー|成功|リマインダー)', content, re.IGNORECASE)
    if type_match:
        t = type_match.group(1).lower()
        type_map = {'info': 'info', '情報': 'info', 'warning': 'warning', '警告': 'warning', 'error': 'error', 'エラー': 'error', 'success': 'success', '成功': 'success', 'reminder': 'reminder', 'リマインダー': 'reminder'}
        result['type'] = type_map.get(t, 'info')

    # Priority
    priority_match = re.search(r'(?:優先|priority)[：:]\s*(low|normal|high|urgent|低|通常|高|緊急)', content, re.IGNORECASE)
    if priority_match:
        p = priority_match.group(1).lower()
        priority_map = {'low': 'low', '低': 'low', 'normal': 'normal', '通常': 'normal', 'high': 'high', '高': 'high', 'urgent': 'urgent', '緊急': 'urgent'}
        result['priority'] = priority_map.get(p, 'normal')

    # Target user
    user_match = re.search(r'(?:宛先|to|target|user)[：:]\s*(.+)', content, re.IGNORECASE)
    if user_match:
        result['target_user'] = user_match.group(1).strip()

    # Scheduled at
    schedule_match = re.search(r'(?:予定|schedule|at)[：:]\s*(.+)', content, re.IGNORECASE)
    if schedule_match and 'タイトル' not in schedule_match.group(0).lower():
        result['scheduled_at'] = parse_date(schedule_match.group(1).strip())

    # Message
    msg_match = re.search(r'(?:メッセージ|message|本文|body)[：:]\s*(.+)', content, re.IGNORECASE)
    if msg_match:
        result['message'] = msg_match.group(1).strip()
        # Title is before message
        idx = content.find(msg_match.group(0))
        title = content[:idx].strip()
        for key in ['タイプ', 'type', '優先', 'priority', '宛先', 'to', 'target', 'user', '予定', 'schedule', 'at']:
            match = re.search(rf'{key}[×:：]', title)
            if match:
                title = title[:match.start()].strip()
        result['title'] = title or 'No title'
    else:
        # Everything is the title
        for key in ['タイプ', 'type', '優先', 'priority', '宛先', 'to', 'target', 'user', '予定', 'schedule', 'at']:
            match = re.search(rf'{key}[×:：]', content)
            if match:
                result['title'] = content[:match.start()].strip()
                break
        else:
            result['title'] = content.strip()
        result['message'] = None

    return result

def parse_schedule_content(content):
    """Parse schedule creation content"""
    result = {'name': None, 'schedule_type': 'daily', 'schedule_value': None, 'notification_template': None, 'priority': 'normal', 'active': True}

    # Type
    type_match = re.search(r'(?:タイプ|type)[：:]\s*(daily|weekly|monthly|cron|毎日|毎週|毎月)', content, re.IGNORECASE)
    if type_match:
        t = type_match.group(1).lower()
        type_map = {'daily': 'daily', '毎日': 'daily', 'weekly': 'weekly', '毎週': 'weekly', 'monthly': 'monthly', '毎月': 'monthly', 'cron': 'cron'}
        result['schedule_type'] = type_map.get(t, 'daily')

    # Value (e.g., day of week, time)
    value_match = re.search(r'(?:値|value|at|on)[：:]\s*(.+)', content, re.IGNORECASE)
    if value_match and 'template' not in value_match.group(0).lower():
        result['schedule_value'] = value_match.group(1).strip()

    # Priority
    priority_match = re.search(r'(?:優先|priority)[：:]\s*(low|normal|high|urgent)', content, re.IGNORECASE)
    if priority_match:
        result['priority'] = priority_match.group(1).lower()

    # Template
    template_match = re.search(r'(?:テンプレート|template|通知内容|content)[：:]\s*(.+)', content, re.IGNORECASE)
    if template_match:
        result['notification_template'] = template_match.group(1).strip()

    # Name (everything before template)
    if template_match:
        idx = content.find(template_match.group(0))
        name = content[:idx].strip()
        for key in ['タイプ', 'type', '値', 'value', 'at', 'on', '優先', 'priority']:
            match = re.search(rf'{key}[×:：]', name)
            if match:
                name = name[:match.start()].strip()
        result['name'] = name or 'Unnamed schedule'
    else:
        result['name'] = content.strip()

    return result

def parse_rule_content(content):
    """Parse rule creation content"""
    result = {'name': None, 'condition_type': 'keyword', 'condition_value': None, 'action': 'promote', 'action_value': None, 'active': True}

    # Condition type
    cond_match = re.search(r'(?:条件|condition)[：:]\s*(source|type|priority|keyword|ソース|タイプ|優先|キーワード)', content, re.IGNORECASE)
    if cond_match:
        c = cond_match.group(1).lower()
        cond_map = {'source': 'source', 'ソース': 'source', 'type': 'type', 'タイプ': 'type', 'priority': 'priority', '優先': 'priority', 'keyword': 'keyword', 'キーワード': 'keyword'}
        result['condition_type'] = cond_map.get(c, 'keyword')

    # Condition value
    cond_value_match = re.search(r'(?:条件値|condition value|when|match)[：:]\s*(.+)', content, re.IGNORECASE)
    if cond_value_match:
        result['condition_value'] = cond_value_match.group(1).strip()

    # Action
    action_match = re.search(r'(?:アクション|action)[：:]\s*(block|promote|demote|forward|auto_read|ブロック|昇格|降格|転送|自動既読)', content, re.IGNORECASE)
    if action_match:
        a = action_match.group(1).lower()
        action_map = {'block': 'block', 'ブロック': 'block', 'promote': 'promote', '昇格': 'promote', 'demote': 'demote', '降格': 'demote', 'forward': 'forward', '転送': 'forward', 'auto_read': 'auto_read', '自動既読': 'auto_read'}
        result['action'] = action_map.get(a, 'promote')

    # Action value (for forward)
    action_value_match = re.search(r'(?:宛先|to|forward to)[：:]\s*(.+)', content, re.IGNORECASE)
    if action_value_match:
        result['action_value'] = action_value_match.group(1).strip()

    # Name (everything before condition)
    if cond_match:
        idx = content.find(cond_match.group(0))
        result['name'] = content[:idx].strip() or 'Unnamed rule'
    else:
        result['name'] = content.strip()

    return result

def parse_notification_filter(filter_str):
    """Parse notification list filter"""
    result = {'status': None, 'priority': None, 'type': None}

    f = filter_str.lower()

    if 'unread' in f or '未読' in f:
        result['status'] = 'unread'
    elif 'read' in f or '既読' in f:
        result['status'] = 'read'
    elif 'archived' in f or 'アーカイブ' in f:
        result['status'] = 'archived'

    if 'urgent' in f or '緊急' in f:
        result['priority'] = 'urgent'
    elif 'high' in f or '高' in f:
        result['priority'] = 'high'
    elif 'low' in f or '低' in f:
        result['priority'] = 'low'

    if 'error' in f or 'エラー' in f:
        result['type'] = 'error'
    elif 'warning' in f or '警告' in f:
        result['type'] = 'warning'
    elif 'success' in f or '成功' in f:
        result['type'] = 'success'

    return result

def parse_date(date_str):
    """Parse date string"""
    try:
        from datetime import datetime, timedelta

        # Try common formats
        for fmt in ['%Y-%m-%d %H:%M', '%Y-%m-%d', '%Y/%m/%d', '%H:%M']:
            try:
                dt = datetime.strptime(date_str.split()[0], fmt)
                return dt.strftime("%Y-%m-%d %H:%M:%S")
            except:
                continue

        # Handle relative times
        if 'tomorrow' in date_str.lower() or '明日' in date_str:
            dt = datetime.now() + timedelta(days=1)
            return dt.strftime("%Y-%m-%d 09:00:00")
        elif 'next hour' in date_str.lower() or '1時間後' in date_str:
            dt = datetime.now() + timedelta(hours=1)
            return dt.strftime("%Y-%m-%d %H:%M:%S")

        return None
    except:
        return None

def process_action(parsed, user_id):
    """Process the parsed action and return response"""
    try:
        if parsed['action'] == 'add_notification':
            notif_data = parse_notification_content(parsed['content'], user_id)
            # Apply rules
            notification = {
                'source': notif_data['source'],
                'title': notif_data['title'],
                'message': notif_data['message'],
                'type': notif_data['type'],
                'priority': notif_data['priority']
            }
            rule_actions = apply_rules(notification)

            for action_type, action_value in rule_actions:
                if action_type == 'priority':
                    notif_data['priority'] = action_value
                elif action_type == 'block':
                    return {
                        'status': 'blocked',
                        'message_ja': 'ルールにより通知がブロックされました',
                        'message_en': 'Notification blocked by rule'
                    }

            notif_id = add_notification(**notif_data)
            return {
                'status': 'success',
                'message_ja': f'通知 #{notif_id} を作成しました',
                'message_en': f'Notification #{notif_id} created',
                'notification_id': notif_id
            }

        elif parsed['action'] == 'list_notifications':
            filters = parse_notification_filter(parsed['filter'])
            notifications = get_notifications(**filters)
            items = '\n'.join([f"#{n[0]}: {n[2]} ({n[4]}, {n[5]}, {n[6]})" for n in notifications])
            return {
                'status': 'success',
                'message_ja': f'通知一覧:\n{items}',
                'message_en': f'Notification list:\n{items}'
            }

        elif parsed['action'] == 'mark_read':
            if parsed.get('notification_id'):
                mark_read(parsed['notification_id'])
                return {
                    'status': 'success',
                    'message_ja': f'通知 #{parsed["notification_id"]} を既読にしました',
                    'message_en': f'Notification #{parsed["notification_id"]} marked as read'
                }
            else:
                mark_all_read(user_id)
                return {
                    'status': 'success',
                    'message_ja': '全ての通知を既読にしました',
                    'message_en': 'All notifications marked as read'
                }

        elif parsed['action'] == 'archive':
            archive_notification(parsed['notification_id'])
            return {
                'status': 'success',
                'message_ja': f'通知 #{parsed["notification_id"]} をアーカイブしました',
                'message_en': f'Notification #{parsed["notification_id"]} archived'
            }

        elif parsed['action'] == 'dismiss':
            dismiss_notification(parsed['notification_id'])
            return {
                'status': 'success',
                'message_ja': f'通知 #{parsed["notification_id"]} を却下しました',
                'message_en': f'Notification #{parsed["notification_id"]} dismissed'
            }

        elif parsed['action'] == 'create_schedule':
            schedule_data = parse_schedule_content(parsed['content'])
            schedule_id = create_schedule(**schedule_data)
            return {
                'status': 'success',
                'message_ja': f'スケジュール #{schedule_id} を作成しました',
                'message_en': f'Schedule #{schedule_id} created',
                'schedule_id': schedule_id
            }

        elif parsed['action'] == 'list_schedules':
            schedules = get_schedules()
            schedule_list = '\n'.join([f"#{s[0]}: {s[1]} ({s[2]}, {s[5]})" for s in schedules])
            return {
                'status': 'success',
                'message_ja': f'スケジュール一覧:\n{schedule_list}',
                'message_en': f'Schedule list:\n{schedule_list}'
            }

        elif parsed['action'] == 'create_rule':
            rule_data = parse_rule_content(parsed['content'])
            rule_id = create_rule(**rule_data)
            return {
                'status': 'success',
                'message_ja': f'ルール #{rule_id} を作成しました',
                'message_en': f'Rule #{rule_id} created',
                'rule_id': rule_id
            }

        elif parsed['action'] == 'stats':
            stats = get_stats()
            return {
                'status': 'success',
                'message_ja': f'統計: ステータス={stats["status_counts"]}, 優先度={stats["priority_counts"]}, タイプ={stats["type_counts"]}',
                'message_en': f'Stats: Status={stats["status_counts"]}, Priority={stats["priority_counts"]}, Type={stats["type_counts"]}',
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
