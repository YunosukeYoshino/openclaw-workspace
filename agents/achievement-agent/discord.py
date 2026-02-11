#!/usr/bin/env python3
"""
アチーブメントエージェント #45 - Discord連携
"""

import re
from datetime import datetime, timedelta
from db import *

def parse_message(message):
    """メッセージを解析"""
    # 追加
    add_match = re.match(r'(?:実績|achievement|達成|goal)[：:]\s*(.+)', message, re.IGNORECASE)
    if add_match:
        return {'action': 'add', 'content': add_match.group(1)}

    # 達成
    complete_match = re.match(r'(?:達成|complete|done)[：:]\s*(\d+)', message, re.IGNORECASE)
    if complete_match:
        return {'action': 'complete', 'achievement_id': int(complete_match.group(1))}

    # 更新
    update_match = re.match(r'(?:更新|update)[：:]\s*(\d+)\s*(.+)', message, re.IGNORECASE)
    if update_match:
        return {'action': 'update', 'achievement_id': int(update_match.group(1)), 'content': update_match.group(2)}

    # 削除
    delete_match = re.match(r'(?:削除|delete|remove)[：:]\s*(\d+)', message, re.IGNORECASE)
    if delete_match:
        return {'action': 'delete', 'achievement_id': int(delete_match.group(1))}

    # 検索
    search_match = re.match(r'(?:検索|search)[：:]\s*(.+)', message, re.IGNORECASE)
    if search_match:
        return {'action': 'search', 'keyword': search_match.group(1)}

    # 一覧
    list_match = re.match(r'(?:(?:実績|achievement|達成)(?:一覧|list)|list|achievements|goals)', message, re.IGNORECASE)
    if list_match:
        return {'action': 'list'}

    # 今日
    if message.strip() in ['今日', 'today']:
        return {'action': 'today'}

    # 昨日
    if message.strip() in ['昨日', 'yesterday']:
        return {'action': 'yesterday'}

    # 今月
    if message.strip() in ['今月', 'this month']:
        return {'action': 'this_month'}

    # 今年
    if message.strip() in ['今年', 'this year']:
        return {'action': 'this_year'}

    # 進行中
    if message.strip() in ['進行中', 'progress', 'in progress']:
        return {'action': 'list_by_status', 'status': 'progress'}

    # 計画中
    if message.strip() in ['計画', 'planned']:
        return {'action': 'list_by_status', 'status': 'planned'}

    # 達成済み
    if message.strip() in ['達成済み', 'completed', 'done']:
        return {'action': 'list_by_status', 'status': 'completed'}

    # カテゴリ
    if message.strip() in ['カテゴリ', 'categories']:
        return {'action': 'categories'}

    # 統計
    if message.strip() in ['統計', 'stats', '実績統計']:
        return {'action': 'stats'}

    return None

def parse_add(content):
    """追加内容を解析"""
    result = {'title': None, 'date': None, 'category': None, 'description': None,
              'notes': None, 'status': 'completed', 'priority': 0}

    # 日付
    date_match = re.search(r'(?:日付|date)[：:]\s*([^、,]+)', content, re.IGNORECASE)
    if date_match:
        result['date'] = parse_date(date_match.group(1).strip())
    else:
        # デフォルトは今日
        result['date'] = datetime.now().strftime("%Y-%m-%d")

    # タイトル (最初の項目より前)
    for key in ['カテゴリ', 'category', '説明', 'description', 'メモ', 'memo', 'note', '優先', 'priority']:
        match = re.search(rf'{key}[×:：]', content)
        if match:
            result['title'] = content[:match.start()].strip()
            break
    else:
        result['title'] = content.strip()

    # カテゴリ
    category_match = re.search(r'(?:カテゴリ|category)[：:]\s*([^、,]+)', content, re.IGNORECASE)
    if category_match:
        result['category'] = category_match.group(1).strip()

    # 説明
    description_match = re.search(r'(?:説明|description)[：:]\s*(.+)', content)
    if description_match:
        result['description'] = description_match.group(1).strip()

    # メモ
    notes_match = re.search(r'(?:メモ|memo|note)[：:]\s*(.+)', content)
    if notes_match:
        result['notes'] = notes_match.group(1).strip()

    # 優先度
    priority_match = re.search(r'(?:優先|priority)[：:]?\s*(\d)', content)
    if priority_match:
        result['priority'] = int(priority_match.group(1))

    return result

def parse_update(content):
    """更新内容を解析"""
    result = {}

    # 日付
    date_match = re.search(r'(?:日付|date)[：:]\s*([^、,]+)', content, re.IGNORECASE)
    if date_match:
        result['date'] = parse_date(date_match.group(1).strip())

    # タイトル
    title_match = re.search(r'(?:タイトル|title|実績)[：:]\s*(.+)', content, re.IGNORECASE)
    if title_match:
        result['title'] = title_match.group(1).strip()

    # カテゴリ
    category_match = re.search(r'(?:カテゴリ|category)[：:]\s*([^、,]+)', content, re.IGNORECASE)
    if category_match:
        result['category'] = category_match.group(1).strip()

    # 説明
    description_match = re.search(r'(?:説明|description)[：:]\s*(.+)', content)
    if description_match:
        result['description'] = description_match.group(1).strip()

    # メモ
    notes_match = re.search(r'(?:メモ|memo|note)[：:]\s*(.+)', content)
    if notes_match:
        result['notes'] = notes_match.group(1).strip()

    # ステータス
    status_match = re.search(r'(?:ステータス|status)[：:]\s*(\w+)', content)
    if status_match:
        status_str = status_match.group(1).lower()
        if status_str in ['completed', 'done', '達成']:
            result['status'] = 'completed'
        elif status_str in ['progress', 'inprogress', '進行中']:
            result['status'] = 'progress'
        elif status_str in ['planned', 'plan', '計画']:
            result['status'] = 'planned'

    return result

def parse_date(date_str):
    """日付を解析"""
    today = datetime.now()

    # 今日
    if '今日' in date_str:
        return today.strftime("%Y-%m-%d")

    # 昨日
    if '昨日' in date_str:
        return (today - timedelta(days=1)).strftime("%Y-%m-%d")

    # 明日
    if '明日' in date_str:
        return (today + timedelta(days=1)).strftime("%Y-%m-%d")

    # 日付形式
    date_match = re.match(r'(\d{4})-(\d{1,2})-(\d{1,2})', date_str)
    if date_match:
        return f"{date_match.group(1)}-{date_match.group(2).zfill(2)}-{date_match.group(3).zfill(2)}"

    date_match = re.match(r'(\d{1,2})/(\d{1,2})', date_str)
    if date_match:
        month = int(date_match.group(1))
        day = int(date_match.group(2))
        return datetime(today.year, month, day).strftime("%Y-%m-%d")

    return None

def handle_message(message):
    """メッセージを処理"""
    parsed = parse_message(message)

    if not parsed:
        return None

    action = parsed['action']

    if action == 'add':
        content = parse_add(parsed['content'])

        if not content['title']:
            return "❌ 実績を入力してください"

        achievement_id = add_achievement(
            content['title'],
            content['date'],
            content['category'],
            content['description'],
            content['notes'],
            content['status'],
            content['priority']
        )

        response = f"🏆 実績 #{achievement_id} 追加完了\n"
        response += f"タイトル: {content['title']}\n"
        response += f"日付: {content['date']}\n"
        if content['category']:
            response += f"カテゴリ: {content['category']}\n"
        if content['description']:
            response += f"説明: {content['description']}\n"
        if content['priority']:
            response += f"優先度: {content['priority']}"
        if content['notes']:
            response += f"\nメモ: {content['notes']}"

        return response

    elif action == 'complete':
        update_achievement(parsed['achievement_id'], status='completed')
        return f"🎉 実績 #{parsed['achievement_id']} 達成完了！"

    elif action == 'update':
        updates = parse_update(parsed['content'])

        if not updates:
            return "❌ 更新内容がありません"

        update_achievement(parsed['achievement_id'], **updates)

        response = f"✅ 実績 #{parsed['achievement_id']} 更新完了"

        return response

    elif action == 'delete':
        delete_achievement(parsed['achievement_id'])
        return f"🗑️ 実績 #{parsed['achievement_id']} 削除完了"

    elif action == 'search':
        keyword = parsed['keyword']
        achievements = search_achievements(keyword)

        if not achievements:
            return f"🔍 「{keyword}」の検索結果: 見つかりませんでした"

        response = f"🔍 「{keyword}」の検索結果 ({len(achievements)}件):\n"
        for achievement in achievements:
            response += format_achievement(achievement)

        return response

    elif action == 'list':
        achievements = list_achievements()

        if not achievements:
            return "🏆 実績がありません"

        response = f"🏆 実績一覧 ({len(achievements)}件):\n"
        for achievement in achievements:
            response += format_achievement(achievement)

        return response

    elif action == 'today':
        date = datetime.now().strftime("%Y-%m-%d")
        achievements = get_by_date(date)

        if not achievements:
            return f"🏆 今日の実績はまだありません"

        response = f"🏆 今日の実績 ({len(achievements)}件):\n"
        for achievement in achievements:
            response += format_achievement(achievement, show_date=False)

        return response

    elif action == 'yesterday':
        date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        achievements = get_by_date(date)

        if not achievements:
            return f"🏆 昨日の実績はありません"

        response = f"🏆 昨日の実績 ({len(achievements)}件):\n"
        for achievement in achievements:
            response += format_achievement(achievement, show_date=False)

        return response

    elif action == 'this_month':
        current_month = datetime.now().strftime("%Y-%m")
        first_day = f"{current_month}-01"
        next_month = datetime(datetime.now().year, datetime.now().month + 1, 1).strftime("%Y-%m-%d") if datetime.now().month < 12 else f"{datetime.now().year + 1}-01-01"

        achievements = list_achievements(date_from=first_day, date_to=next_month)

        if not achievements:
            return f"🏆 今月の実績はありません"

        response = f"🏆 今月の実績 ({len(achievements)}件):\n"
        for achievement in achievements:
            response += format_achievement(achievement)

        return response

    elif action == 'this_year':
        current_year = datetime.now().strftime("%Y")
        first_day = f"{current_year}-01-01"
        next_year = f"{int(current_year) + 1}-01-01"

        achievements = list_achievements(date_from=first_day, date_to=next_year)

        if not achievements:
            return f"🏆 今年の実績はありません"

        response = f"🏆 今年の実績 ({len(achievements)}件):\n"
        for achievement in achievements:
            response += format_achievement(achievement)

        return response

    elif action == 'list_by_status':
        achievements = list_achievements(status=parsed['status'])

        if not achievements:
            status_text = {
                'completed': '達成済み',
                'progress': '進行中',
                'planned': '計画中'
            }.get(parsed['status'], parsed['status'])
            return f"🏆 {status_text}の実績はありません"

        status_text = {
            'completed': '達成済み',
            'progress': '進行中',
            'planned': '計画中'
        }.get(parsed['status'], parsed['status'])
        response = f"🏆 {status_text}の実績 ({len(achievements)}件):\n"
        for achievement in achievements:
            response += format_achievement(achievement)

        return response

    elif action == 'categories':
        categories = get_categories()

        if not categories:
            return "🏆 カテゴリがありません"

        response = "📁 カテゴリ一覧:\n"
        for category, count in categories:
            response += f"  • {category} ({count}件)\n"

        return response

    elif action == 'stats':
        stats = get_stats()

        response = "📊 実績統計:\n"
        response += f"全実績: {stats['total']}件\n"
        if stats['by_status'].get('completed'):
            response += f"達成済み: {stats['by_status']['completed']}件\n"
        if stats['by_status'].get('progress'):
            response += f"進行中: {stats['by_status']['progress']}件\n"
        if stats['by_status'].get('planned'):
            response += f"計画中: {stats['by_status']['planned']}件\n"
        response += f"今日: {stats['today']}件\n"
        response += f"今月: {stats['this_month']}件\n"
        response += f"今年: {stats['this_year']}件"

        return response

    return None

def format_achievement(achievement, show_date=True):
    """実績をフォーマット"""
    id, title, date, category, description, notes, status, priority, created_at = achievement

    status_emoji = {
        'completed': '🏆',
        'progress': '🔜',
        'planned': '📋'
    }

    response = ""
    if show_date:
        response = f"\n{status_emoji.get(status, '🏆')} [{id}] {date} - {title}\n"
    else:
        response = f"\n{status_emoji.get(status, '🏆')} [{id}] {title}\n"

    parts = []
    if category:
        parts.append(f"カテゴリ: {category}")
    if priority:
        priority_text = '!' * priority
        parts.append(f"優先: {priority_text}")

    if parts:
        response += f"    {' | '.join(parts)}\n"

    if status != 'completed':
        status_text = {
            'completed': '達成済み',
            'progress': '進行中',
            'planned': '計画中'
        }.get(status, status)
        response += f"    📌 {status_text}\n"

    return response

if __name__ == '__main__':
    init_db()

    test_messages = [
        "実績: マラソン完走, カテゴリ: スポーツ, 日付: 2025-01-15",
        "実績: プロジェクト完了, 説明: 大規模なウェブアプリケーション",
        "達成: 1",
        "今日",
        "統計",
    ]

    for msg in test_messages:
        print(f"\n入力: {msg}")
        result = handle_message(msg)
        if result:
            print(result)
