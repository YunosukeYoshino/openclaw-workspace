#!/usr/bin/env python3
"""
Ticket Agent #23 - Discord Integration
"""

import re
from db import *

def parse_message(message):
    """Parse message"""
    # Add ticket
    add_match = re.match(r'(?:追加|add|new)[:：]\s*(.+)', message, re.IGNORECASE)
    if add_match:
        return parse_add(add_match.group(1))

    # Update status
    status_match = re.match(r'(?:ステータス|status)[:：]\s*(\d+)\s*[,，]\s*(\w+)', message, re.IGNORECASE)
    if status_match:
        return {'action': 'update_status', 'ticket_id': int(status_match.group(1)), 'status': status_match.group(2)}

    # Add comment
    comment_match = re.match(r'(?:コメント|comment)[:：]\s*(\d+)\s*[,，]\s*(.+)', message, re.IGNORECASE)
    if comment_match:
        return {'action': 'add_comment', 'ticket_id': int(comment_match.group(1)), 'comment': comment_match.group(2)}

    # Assign
    assign_match = re.match(r'(?:担当|assign)[:：]\s*(\d+)\s*[,，]\s*(.+)', message, re.IGNORECASE)
    if assign_match:
        return {'action': 'assign', 'ticket_id': int(assign_match.group(1)), 'assignee': assign_match.group(2)}

    # List
    list_match = re.match(r'(?:一覧|list)(?:[:：]\s*(\w+))?', message, re.IGNORECASE)
    if list_match:
        status = list_match.group(1) if list_match.group(1) else None
        return {'action': 'list', 'status': status}

    # Search
    search_match = re.match(r'(?:検索|search)[:：]\s*(.+)', message, re.IGNORECASE)
    if search_match:
        return {'action': 'search', 'keyword': search_match.group(1)}

    # View comments
    view_match = re.match(r'(?:詳細|view|comments)[:：]\s*(\d+)', message, re.IGNORECASE)
    if view_match:
        return {'action': 'view_comments', 'ticket_id': int(view_match.group(1))}

    # Stats
    if message.strip() in ['統計', 'stats']:
        return {'action': 'stats'}

    return None

def parse_add(content):
    """Parse add content"""
    result = {'action': 'add', 'title': None, 'description': None, 'category': None, 'priority': 1}

    # Title
    title_match = re.match(r'^([^、,]+)', content)
    if title_match:
        result['title'] = title_match.group(1).strip()

    # Priority
    pri_match = re.search(r'優先[:：]\s*(\d)', content)
    if pri_match:
        result['priority'] = int(pri_match.group(1))

    # Category
    cat_match = re.search(r'カテゴリ[:：]\s*(.+?)(?:[、,]|$)', content)
    if cat_match:
        result['category'] = cat_match.group(1).strip()

    # Description
    desc_match = re.search(r'説明[:：]\s*(.+)', content)
    if desc_match:
        result['description'] = desc_match.group(1).strip()

    return result

def handle_message(message):
    """Handle message"""
    parsed = parse_message(message)

    if not parsed:
        return None

    action = parsed['action']

    if action == 'add':
        if not parsed['title']:
            return "❌ タイトルを入力してください"

        ticket_id = add_ticket(
            parsed['title'],
            parsed['description'],
            parsed['category'],
            parsed['priority']
        )

        response = f"🎫 チケット #{ticket_id} 作成完了\n"
        response += f"タイトル: {parsed['title']}\n"
        if parsed['category']:
            response += f"カテゴリ: {parsed['category']}\n"
        response += f"優先度: {parsed['priority']}"

        return response

    elif action == 'update_status':
        status_map = {'open': 'open', 'in_progress': 'in_progress', 'progress': 'in_progress', 'resolved': 'resolved', 'closed': 'closed'}
        status = status_map.get(parsed['status'].lower(), parsed['status'])
        update_status(parsed['ticket_id'], status)
        return f"✅ チケット #{parsed['ticket_id']} のステータスを {status} に更新"

    elif action == 'add_comment':
        add_comment(parsed['ticket_id'], parsed['comment'])
        return f"💬 チケット #{parsed['ticket_id']} にコメント追加"

    elif action == 'assign':
        assign_ticket(parsed['ticket_id'], parsed['assignee'])
        return f"👤 チケット #{parsed['ticket_id']} を {parsed['assignee']} に担当割り当て"

    elif action == 'list':
        tickets = list_tickets(status=parsed['status'])

        if not tickets:
            return f"🎫 チケットがありません"

        status_text = f" ({parsed['status']})" if parsed['status'] else ""
        response = f"🎫 一覧{status_text} ({len(tickets)}件):\n"
        for ticket in tickets:
            response += format_ticket(ticket)

        return response

    elif action == 'search':
        tickets = search_tickets(parsed['keyword'])

        if not tickets:
            return f"🔍 「{parsed['keyword']}」の検索結果: 見つかりませんでした"

        response = f"🔍 「{parsed['keyword']}」の検索結果 ({len(tickets)}件):\n"
        for ticket in tickets:
            response += format_ticket(ticket)

        return response

    elif action == 'view_comments':
        comments = get_ticket_comments(parsed['ticket_id'])

        if not comments:
            return f"💬 チケット #{parsed['ticket_id']} にコメントはありません"

        response = f"💬 チケット #{parsed['ticket_id']} のコメント ({len(comments)}件):\n"
        for comment in comments:
            response += format_comment(comment)

        return response

    elif action == 'stats':
        stats = get_stats()

        response = "📊 チケット統計:\n"
        response += f"全チケット: {stats['total']}件\n"
        response += f"未対応: {stats['open']}件\n"
        response += f"処理中: {stats['in_progress']}件\n"
        response += f"解決済み: {stats['resolved']}件\n"
        response += f"クローズ: {stats['closed']}件"

        return response

    return None

def format_ticket(ticket):
    """Format ticket"""
    id, title, description, category, priority, status, assignee, created_at, updated_at = ticket

    status_map = {'open': '🔴', 'in_progress': '🟡', 'resolved': '🟢', 'closed': '✅'}
    status_icon = status_map.get(status, '❓')

    response = f"\n{status_icon} [{id}] {title}\n"
    if assignee:
        response += f"    担当: {assignee}\n"
    if category:
        response += f"    カテゴリ: {category}\n"

    return response

def format_comment(comment):
    """Format comment"""
    id, comment_text, author, created_at = comment
    response = f"\n    💭 {comment_text}"
    if author:
        response += f" - {author}"

    return response

if __name__ == '__main__':
    init_db()

    test_messages = [
        "追加: バグ報告, 優先: 3, 説明: ログインできない",
        "追加: 新機能リクエスト, カテゴリ: 機能",
        "一覧",
        "一覧: open",
        "ステータス: 1, in_progress",
        "コメント: 1, 調査中です",
        "担当: 1, 田中",
        "検索: バグ",
        "統計",
    ]

    for msg in test_messages:
        print(f"\n入力: {msg}")
        result = handle_message(msg)
        if result:
            print(result)
