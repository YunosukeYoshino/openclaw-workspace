#!/usr/bin/env python3
"""
Cleanup Agent - Discord連携
"""

import re
from datetime import datetime, timedelta
from db import *

def parse_message(message):
    """メッセージを解析"""
    # タスク追加
    add_match = re.match(r'(?:クリーンアップ|cleanup)[:：]\s*(.+)', message, re.IGNORECASE)
    if add_match:
        return parse_add(add_match.group(1))

    # タスク一覧
    list_match = re.match(r'(?:(?:クリーンアップ|cleanup)(?:一覧|list)|list_cleanup)', message, re.IGNORECASE)
    if list_match:
        return {'action': 'list'}

    # 有効タスク一覧
    if message.strip() in ['有効クリーンアップ', 'active_cleanup', 'enabled_cleanup']:
        return {'action': 'list_enabled'}

    # 履歴
    history_match = re.match(r'(?:履歴|history)[:：]?\s*(\d+)?', message, re.IGNORECASE)
    if history_match:
        limit = int(history_match.group(1)) if history_match.group(1) else 10
        return {'action': 'history', 'limit': limit}

    # タスク詳細
    detail_match = re.match(r'(?:詳細|detail)[:：]\s*(\d+)', message, re.IGNORECASE)
    if detail_match:
        return {'action': 'detail', 'task_id': int(detail_match.group(1))}

    # 削除
    delete_match = re.match(r'(?:削除|delete)[:：]\s*(\d+)', message, re.IGNORECASE)
    if delete_match:
        return {'action': 'delete', 'task_id': int(delete_match.group(1))}

    # 有効/無効切り替え
    toggle_match = re.match(r'(?:切り替え|toggle|enable|disable)[:：]\s*(\d+)', message, re.IGNORECASE)
    if toggle_match:
        return {'action': 'toggle', 'task_id': int(toggle_match.group(1))}

    # 除外ルール追加
    exclude_match = re.match(r'(?:除外|exclude)[:：]\s*(\d+)\s*,\s*(.+)', message, re.IGNORECASE)
    if exclude_match:
        return {'action': 'add_exclusion', 'task_id': int(exclude_match.group(1)), 'pattern': exclude_match.group(2)}

    # 除外ルール一覧
    exclude_list_match = re.match(r'(?:除外(?:一覧|list)|list_exclusion)[:：]\s*(\d+)', message, re.IGNORECASE)
    if exclude_list_match:
        return {'action': 'list_exclusion', 'task_id': int(exclude_list_match.group(1))}

    # 統計
    if message.strip() in ['統計', 'stats', 'クリーンアップ統計', 'cleanup_stats']:
        return {'action': 'stats'}

    return None

def parse_add(content):
    """タスク追加を解析"""
    result = {'action': 'add', 'name': None, 'description': None, 'target_path': None,
              'cleanup_type': None, 'retention_days': None, 'pattern': None, 'schedule': None}

    # 名前 (最初の部分)
    name_match = re.match(r'^([^,，【（\(]+)', content)
    if name_match:
        result['name'] = name_match.group(1).strip()

    # タイプ
    type_match = re.search(r'タイプ[:：]\s*(files|folders|temp|logs|cache|custom|ファイル|フォルダ|一時|ログ|キャッシュ)', content, re.IGNORECASE)
    if type_match:
        type_val = type_match.group(1).lower()
        type_map = {
            'files': 'files', 'ファイル': 'files',
            'folders': 'folders', 'フォルダ': 'folders',
            'temp': 'temp', '一時': 'temp',
            'logs': 'logs', 'ログ': 'logs',
            'cache': 'cache', 'キャッシュ': 'cache',
            'custom': 'custom'
        }
        result['cleanup_type'] = type_map.get(type_val, 'files')

    # ターゲットパス
    path_match = re.search(r'パス[:：]\s*([^,，]+)', content, re.IGNORECASE)
    if path_match:
        result['target_path'] = path_match.group(1).strip()

    # 保持期間
    retention_match = re.search(r'保持期間[:：]\s*(\d+)\s*(日|days?)', content, re.IGNORECASE)
    if retention_match:
        result['retention_days'] = int(retention_match.group(1))

    # パターン
    pattern_match = re.search(r'パターン[:：]\s*([^,，]+)', content, re.IGNORECASE)
    if pattern_match:
        result['pattern'] = pattern_match.group(1).strip()

    # スケジュール
    schedule_match = re.search(r'スケジュール[:：]\s*([^,，]+)', content, re.IGNORECASE)
    if schedule_match:
        schedule_str = schedule_match.group(1).strip()
        result['schedule'] = parse_schedule(schedule_str)

    # 説明
    desc_match = re.search(r'説明[:：]\s*(.+)', content)
    if desc_match:
        result['description'] = desc_match.group(1).strip()

    # 名前がまだない場合、パスより前を名前とする
    if not result['name']:
        path_match = re.search(r'パス[:：]', content)
        if path_match:
            result['name'] = content[:path_match.start()].strip()
        else:
            result['name'] = content.strip()

    return result

def parse_schedule(schedule_str):
    """スケジュールを解析"""
    # 毎日
    daily_match = re.match(r'毎日\s*(\d{1,2}:\d{2})?', schedule_str)
    if daily_match:
        time = daily_match.group(1) if daily_match.group(1) else "00:00"
        return f"daily:{time}"

    # 毎週
    weekly_match = re.match(r'毎週\s*([月火水木金土日])\s*(\d{1,2}:\d{2})?', schedule_str)
    if weekly_match:
        weekday = weekly_match.group(1)
        time = weekly_match.group(2) if weekly_match.group(2) else "00:00"
        return f"weekly:{weekday}:{time}"

    # 毎月
    monthly_match = re.match(r'毎月\s*(\d{1,2})日\s*(\d{1,2}:\d{2})?', schedule_str)
    if monthly_match:
        day = monthly_match.group(1)
        time = monthly_match.group(2) if monthly_match.group(2) else "00:00"
        return f"monthly:{day}:{time}"

    # 時間間隔
    interval_match = re.match(r'(\d+)\s*(時間|分|hour|minute)', schedule_str)
    if interval_match:
        value = int(interval_match.group(1))
        unit = interval_match.group(2)
        if unit in ['時間', 'hour']:
            return f"interval:{value}h"
        elif unit in ['分', 'minute']:
            return f"interval:{value}m"

    return schedule_str

def handle_message(message):
    """メッセージを処理"""
    parsed = parse_message(message)

    if not parsed:
        return None

    action = parsed['action']

    if action == 'add':
        if not parsed['name']:
            return "❌ 名前を入力してください"

        task_id = add_cleanup_task(
            parsed['name'],
            parsed['description'],
            parsed['target_path'],
            parsed['cleanup_type'] or 'files',
            parsed['retention_days'],
            parsed['pattern'],
            parsed['schedule']
        )

        response = f"✅ クリーンアップタスク #{task_id} 追加完了\n"
        response += f"名前: {parsed['name']}\n"
        if parsed['description']:
            response += f"説明: {parsed['description']}\n"
        if parsed['target_path']:
            response += f"パス: {parsed['target_path']}\n"
        if parsed['cleanup_type']:
            type_text = {
                'files': 'ファイル', 'folders': 'フォルダ', 'temp': '一時ファイル',
                'logs': 'ログ', 'cache': 'キャッシュ', 'custom': 'カスタム'
            }.get(parsed['cleanup_type'], parsed['cleanup_type'])
            response += f"タイプ: {type_text}\n"
        if parsed['retention_days']:
            response += f"保持期間: {parsed['retention_days']}日\n"
        if parsed['pattern']:
            response += f"パターン: {parsed['pattern']}\n"
        if parsed['schedule']:
            response += f"スケジュール: {parsed['schedule']}"

        return response

    elif action == 'list':
        tasks = list_cleanup_tasks()

        if not tasks:
            return "📋 クリーンアップタスクがありません"

        response = f"📋 クリーンアップタスク一覧 ({len(tasks)}件):\n"
        for task in tasks:
            response += format_task(task)

        return response

    elif action == 'list_enabled':
        tasks = list_cleanup_tasks(enabled_only=True)

        if not tasks:
            return "📋 有効なクリーンアップタスクはありません"

        response = f"📋 有効なクリーンアップタスク ({len(tasks)}件):\n"
        for task in tasks:
            response += format_task(task)

        return response

    elif action == 'detail':
        task = get_cleanup_task(parsed['task_id'])

        if not task:
            return f"❌ タスク #{parsed['task_id']} が見つかりません"

        response = format_task_detail(task)

        # 除外ルールも表示
        rules = list_exclusion_rules(parsed['task_id'])
        if rules:
            response += "\n🚫 除外ルール:\n"
            for rule in rules:
                response += f"  • {rule[1]} ({rule[2]})\n"

        return response

    elif action == 'history':
        limit = parsed.get('limit', 10)
        history = get_cleanup_history(limit=limit)

        if not history:
            return "📜 実行履歴がありません"

        response = f"📜 実行履歴 (直近{limit}件):\n"
        for entry in history:
            response += format_history(entry)

        return response

    elif action == 'delete':
        delete_cleanup_task(parsed['task_id'])
        return f"🗑️ タスク #{parsed['task_id']} 削除完了"

    elif action == 'toggle':
        toggle_cleanup_task(parsed['task_id'])
        return f"🔄 タスク #{parsed['task_id']} 有効/無効切り替え"

    elif action == 'add_exclusion':
        rule_id = add_exclusion_rule(parsed['task_id'], parsed['pattern'])
        return f"🚫 除外ルール #{rule_id} 追加完了 (タスク #{parsed['task_id']})\nパターン: {parsed['pattern']}"

    elif action == 'list_exclusion':
        rules = list_exclusion_rules(parsed['task_id'])

        if not rules:
            return f"📋 タスク #{parsed['task_id']} の除外ルールはありません"

        response = f"📋 タスク #{parsed['task_id']} の除外ルール ({len(rules)}件):\n"
        for rule in rules:
            response += f"  [{rule[0]}] {rule[1]} ({rule[2]})\n"
            if rule[3]:
                response += f"       {rule[3]}\n"

        return response

    elif action == 'stats':
        stats = get_cleanup_stats()

        response = "📊 クリーンアップ統計:\n"
        response += f"タスク数: {stats['total_tasks']}件 (有効: {stats['enabled_tasks']}件)\n"
        response += f"実行回数: {stats['total_runs']}回\n"
        response += f"成功: {stats['success_runs']}回 / 失敗: {stats['failed_runs']}回\n"
        response += f"削除アイテム数: {stats['total_items_deleted']}件\n"
        if stats['total_space_freed'] > 0:
            space_mb = stats['total_space_freed'] / (1024 * 1024)
            response += f"解放スペース: {space_mb:.2f} MB\n"
        if stats['last_successful_run']:
            response += f"最後の成功実行: {stats['last_successful_run']}"

        return response

    return None

def format_task(task):
    """タスクをフォーマット"""
    id, name, description, cleanup_type, schedule, enabled, last_run, next_run = task

    # ステータス表示
    status_icon = "✅" if enabled else "⏸️"

    # タイプ表示
    type_text = {
        'files': '📄', 'folders': '📁', 'temp': '🗑️',
        'logs': '📝', 'cache': '💾', 'custom': '⚙️'
    }.get(cleanup_type, '📄')

    # スケジュール表示
    schedule_str = f"🕐 {schedule}" if schedule else ""

    response = f"\n{status_icon} [{id}] {type_text} {name}\n"
    if cleanup_type:
        response += f"    タイプ: {cleanup_type}\n"
    if schedule_str:
        response += f"    {schedule_str}\n"

    return response

def format_task_detail(task):
    """タスク詳細をフォーマット"""
    id, name, description, target_path, cleanup_type, retention_days, pattern, \
    schedule, enabled, last_run, next_run, created_at, updated_at = task

    response = f"📋 タスク詳細 #{id}:\n"
    response += f"名前: {name}\n"
    if description:
        response += f"説明: {description}\n"
    if target_path:
        response += f"パス: {target_path}\n"
    if cleanup_type:
        response += f"タイプ: {cleanup_type}\n"
    if retention_days:
        response += f"保持期間: {retention_days}日\n"
    if pattern:
        response += f"パターン: {pattern}\n"
    if schedule:
        response += f"スケジュール: {schedule}\n"
    response += f"状態: {'有効' if enabled else '無効'}\n"
    if last_run:
        response += f"最後の実行: {last_run}\n"
    if next_run:
        response += f"次回の実行: {next_run}\n"
    response += f"作成日時: {created_at}"

    return response

def format_history(entry):
    """履歴をフォーマット"""
    id, task_id, task_name, run_at, status, items_processed, items_deleted, space_freed, duration, error = entry

    # ステータス表示
    status_icons = {'success': '✅', 'partial': '⚠️', 'failed': '❌'}
    status_icon = status_icons.get(status, '❓')

    response = f"{status_icon} [{id}] {task_name} - {run_at}\n"
    if items_processed > 0:
        response += f"    処理: {items_processed}件"
    if items_deleted > 0:
        response += f" / 削除: {items_deleted}件"
    if items_processed > 0 or items_deleted > 0:
        response += "\n"
    if space_freed > 0:
        space_mb = space_freed / (1024 * 1024)
        response += f"    解放: {space_mb:.2f} MB\n"
    if duration > 0:
        response += f"    時間: {duration}秒\n"
    if error:
        response += f"    エラー: {error}\n"

    return response

if __name__ == '__main__':
    # テスト
    init_db()

    test_messages = [
        "クリーンアップ: temp_files_cleanup, パス: /tmp, タイプ: temp, 保持期間: 7日",
        "クリーンアップ: log_cleanup, パス: /var/log, タイプ: logs, 保持期間: 30日, スケジュール: 毎日 02:00",
        "クリーンアップ: cache_cleanup, タイプ: cache, スケジュール: 毎週 日曜日 03:00",
        "詳細: 1",
        "履歴",
        "有効クリーンアップ",
        "統計",
    ]

    for msg in test_messages:
        print(f"\n入力: {msg}")
        result = handle_message(msg)
        if result:
            print(result)
