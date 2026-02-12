#!/usr/bin/env python3
"""
Skills Agent #26 - Discord Integration
"""

import re
from db import *

def parse_message(message):
    """Parse message"""
    # Add skill
    add_match = re.match(r'(?:追加|add|new)[:：]\s*(.+)', message, re.IGNORECASE)
    if add_match:
        return parse_add(add_match.group(1))

    # Update level
    level_match = re.match(r'(?:レベル|level)[:：]\s*(\d+)\s*[,，]\s*(\d)', message, re.IGNORECASE)
    if level_match:
        return {'action': 'update_level', 'skill_id': int(level_match.group(1)), 'level': int(level_match.group(2))}

    # Update status
    status_match = re.match(r'(?:ステータス|status)[:：]\s*(\d+)\s*[,，]\s*(\w+)', message, re.IGNORECASE)
    if status_match:
        return {'action': 'update_status', 'skill_id': int(status_match.group(1)), 'status': status_match.group(2)}

    # Log practice
    practice_match = re.match(r'(?:練習|practice|log)[:：]\s*(\d+)\s*[,，]\s*(.+)', message, re.IGNORECASE)
    if practice_match:
        return {'action': 'log_practice', 'skill_id': int(practice_match.group(1)), 'action': practice_match.group(2)}

    # List
    list_match = re.match(r'(?:一覧|list)(?:[:：]\s*(\w+))?', message, re.IGNORECASE)
    if list_match:
        status = list_match.group(1) if list_match.group(1) else None
        return {'action': 'list', 'status': status}

    # Search
    search_match = re.match(r'(?:検索|search)[:：]\s*(.+)', message, re.IGNORECASE)
    if search_match:
        return {'action': 'search', 'keyword': search_match.group(1)}

    # View logs
    view_match = re.match(r'(?:履歴|logs|view)[:：]\s*(\d+)', message, re.IGNORECASE)
    if view_match:
        return {'action': 'view_logs', 'skill_id': int(view_match.group(1))}

    # Stats
    if message.strip() in ['統計', 'stats']:
        return {'action': 'stats'}

    return None

def parse_add(content):
    """Parse add content"""
    result = {'action': 'add', 'name': None, 'category': None, 'description': None, 'level': 1, 'priority': 0, 'goal': None, 'resources': None, 'notes': None}

    # Name
    name_match = re.match(r'^([^、,]+)', content)
    if name_match:
        result['name'] = name_match.group(1).strip()

    # Level
    level_match = re.search(r'レベル|level[:：]\s*(\d)', content)
    if level_match:
        result['level'] = int(level_match.group(1))

    # Category
    cat_match = re.search(r'カテゴリ|category[:：]\s*(.+?)(?:[、,]|$)', content)
    if cat_match:
        result['category'] = cat_match.group(1).strip()

    # Goal
    goal_match = re.search(r'目標|goal[:：]\s*(.+)', content)
    if goal_match:
        result['goal'] = goal_match.group(1).strip()

    # Description
    desc_match = re.search(r'説明|description[:：]\s*(.+)', content)
    if desc_match:
        result['description'] = desc_match.group(1).strip()

    # Priority
    pri_match = re.search(r'優先|priority[:：]\s*(\d)', content)
    if pri_match:
        result['priority'] = int(pri_match.group(1))

    return result

def handle_message(message):
    """Handle message"""
    parsed = parse_message(message)

    if not parsed:
        return None

    action = parsed['action']

    if action == 'add':
        if not parsed['name']:
            return "❌ スキル名を入力してください"

        skill_id = add_skill(
            parsed['name'],
            parsed['category'],
            parsed['description'],
            parsed['level'],
            parsed['priority'],
            parsed['goal'],
            parsed['resources'],
            parsed['notes']
        )

        response = f"✅ スキル #{skill_id} 追加完了\n"
        response += f"スキル: {parsed['name']}\n"
        if parsed['category']:
            response += f"カテゴリ: {parsed['category']}\n"
        response += f"レベル: {parsed['level']}/5"

        return response

    elif action == 'update_level':
        level = parsed['level']
        if level < 1 or level > 5:
            return "❌ レベルは1-5で指定してください"

        update_level(parsed['skill_id'], level)
        status = "マスター！" if level == 5 else "更新"
        return f"✅ スキル #{parsed['skill_id']} のレベルを {level}/5 に{status}"

    elif action == 'update_status':
        status_map = {'learning': 'learning', 'practicing': 'practicing', 'mastered': 'mastered', 'abandoned': 'abandoned'}
        status = status_map.get(parsed['status'].lower(), parsed['status'])
        update_status(parsed['skill_id'], status)
        return f"✅ スキル #{parsed['skill_id']} のステータスを {status} に更新"

    elif action == 'log_practice':
        log_practice(parsed['skill_id'], parsed['action'])
        total_time = get_total_practice_time(parsed['skill_id'])
        response = f"📝 スキル #{parsed['skill_id']} に練習ログ追加: {parsed['action']}\n"
        response += f"    総練習時間: {total_time}分"

        return response

    elif action == 'list':
        skills = list_skills(status=parsed['status'])

        if not skills:
            return f"📚 スキルがありません"

        status_text = f" ({parsed['status']})" if parsed['status'] else ""
        response = f"📚 一覧{status_text} ({len(skills)}件):\n"
        for skill in skills:
            response += format_skill(skill)

        return response

    elif action == 'search':
        skills = search_skills(parsed['keyword'])

        if not skills:
            return f"🔍 「{parsed['keyword']}」の検索結果: 見つかりませんでした"

        response = f"🔍 「{parsed['keyword']}」の検索結果 ({len(skills)}件):\n"
        for skill in skills:
            response += format_skill(skill)

        return response

    elif action == 'view_logs':
        logs = get_skill_logs(parsed['skill_id'])

        if not logs:
            return f"📝 スキル #{parsed['skill_id']} の練習履歴はありません"

        response = f"📝 スキル #{parsed['skill_id']} の練習履歴 ({len(logs)}件):\n"
        for log in logs:
            response += format_log(log)

        return response

    elif action == 'stats':
        stats = get_stats()

        response = "📊 スキル統計:\n"
        response += f"全スキル: {stats['total_skills']}件\n"
        response += f"学習中: {stats['learning']}件\n"
        response += f"練習中: {stats['practicing']}件\n"
        response += f"マスター: {stats['mastered']}件\n"
        response += f"総練習時間: {stats['total_practice_minutes']}分"

        return response

    return None

def format_skill(skill):
    """Format skill"""
    id, name, category, description, level, status, priority, goal, resources, notes, started_at, created_at = skill

    status_map = {'learning': '📖', 'practicing': '💪', 'mastered': '🏆', 'abandoned': '❌'}
    status_icon = status_map.get(status, '❓')

    level_stars = '⭐' * level

    response = f"\n{status_icon} [{id}] {name} {level_stars}\n"
    if category:
        response += f"    カテゴリ: {category}\n"

    return response

def format_log(log):
    """Format log"""
    id, action, duration, notes, created_at = log

    response = f"\n    📝 {action}"
    if duration:
        response += f" ({duration}分)"
    if notes:
        response += f" - {notes}"

    return response

if __name__ == '__main__':
    init_db()

    test_messages = [
        "追加: Python, カテゴリ: プログラミング, レベル: 2",
        "追加: ギター, カテゴリ: 音楽, レベル: 1",
        "一覧",
        "一覧: learning",
        "レベル: 1, 3",
        "練習: 1, 基礎構文の復習",
        "履歴: 1",
        "検索: プログラミング",
        "統計",
    ]

    for msg in test_messages:
        print(f"\n入力: {msg}")
        result = handle_message(msg)
        if result:
            print(result)
