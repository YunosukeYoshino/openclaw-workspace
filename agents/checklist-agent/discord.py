#!/usr/bin/env python3
"""
Checklist Agent #3 - Discord Integration
"""

import re
from db import *

def parse_message(message):
    """Parse message"""
    # Create checklist
    create_match = re.match(r'(?:作成|create)[:：]\s*(.+)', message, re.IGNORECASE)
    if create_match:
        return parse_create(create_match.group(1))

    # Add item
    item_match = re.match(r'(?:項目|item)[:：]\s*(\d+)\s*[,，]\s*(.+)', message, re.IGNORECASE)
    if item_match:
        return {'action': 'add_item', 'checklist_id': int(item_match.group(1)), 'text': item_match.group(2)}

    # Toggle item
    toggle_match = re.match(r'(?:チェック|toggle|check)[:：]\s*(\d+)', message, re.IGNORECASE)
    if toggle_match:
        return {'action': 'toggle', 'item_id': int(toggle_match.group(1))}

    # Delete item
    delete_item_match = re.match(r'(?:項目削除|delete item)[:：]\s*(\d+)', message, re.IGNORECASE)
    if delete_item_match:
        return {'action': 'delete_item', 'item_id': int(delete_item_match.group(1))}

    # Delete checklist
    delete_match = re.match(r'(?:削除|delete)[:：]\s*(\d+)', message, re.IGNORECASE)
    if delete_match:
        return {'action': 'delete', 'checklist_id': int(delete_match.group(1))}

    # List checklists
    list_match = re.match(r'(?:一覧|list)(?:[:：]\s*(.+))?', message, re.IGNORECASE)
    if list_match:
        category = list_match.group(1).strip() if list_match.group(1) else None
        return {'action': 'list', 'category': category}

    # View checklist
    view_match = re.match(r'(?:表示|view)[:：]\s*(\d+)', message, re.IGNORECASE)
    if view_match:
        return {'action': 'view', 'checklist_id': int(view_match.group(1))}

    # Progress
    progress_match = re.match(r'(?:進捗|progress)[:：]\s*(\d+)', message, re.IGNORECASE)
    if progress_match:
        return {'action': 'progress', 'checklist_id': int(progress_match.group(1))}

    # Template
    template_match = re.match(r'(?:テンプレート|template)[:：]\s*(.+)', message, re.IGNORECASE)
    if template_match:
        return parse_template(template_match.group(1))

    # Stats
    if message.strip() in ['統計', 'stats']:
        return {'action': 'stats'}

    return None

def parse_create(content):
    """Parse create content"""
    result = {'action': 'create', 'title': None, 'description': None, 'category': None}

    result['title'] = content.split(',')[0].strip()

    desc_match = re.search(r'(?:説明|description)[:：]\s*(.+?)(?:[、,]|$)', content)
    if desc_match:
        result['description'] = desc_match.group(1).strip()

    category_match = re.search(r'(?:カテゴリ|category)[:：]\s*(.+)', content)
    if category_match:
        result['category'] = category_match.group(1).strip()

    return result

def parse_template(content):
    """Parse template content"""
    # Create template
    create_template_match = re.match(r'作成|create\s+(.+)', content, re.IGNORECASE)
    if create_template_match:
        result = {'action': 'create_template', 'name': None, 'description': None}
        result['name'] = create_template_match.group(1).split(',')[0].strip()

        desc_match = re.search(r'(?:説明|description)[:：]\s*(.+)', create_template_match.group(1))
        if desc_match:
            result['description'] = desc_match.group(1).strip()

        return result

    # Use template
    use_match = re.match(r'使用|use\s+(\d+)\s*,\s*(.+)', content, re.IGNORECASE)
    if use_match:
        return {'action': 'use_template', 'template_id': int(use_match.group(1)), 'title': use_match.group(2)}

    # Add template item
    add_template_match = re.match(r'項目|item\s+(\d+)\s*,\s*(.+)', content, re.IGNORECASE)
    if add_template_match:
        return {'action': 'add_template_item', 'template_id': int(add_template_match.group(1)), 'text': add_template_match.group(2)}

    return None

def handle_message(message):
    """Handle message"""
    parsed = parse_message(message)

    if not parsed:
        return None

    action = parsed['action']

    if action == 'create':
        if not parsed['title']:
            return "❌ タイトルを入力してください / Please enter a title"

        checklist_id = create_checklist(parsed['title'], parsed['description'], parsed['category'])
        return f"✅ チェックリスト #{checklist_id} '{parsed['title']}' を作成しました / Checklist #{checklist_id} created"

    elif action == 'add_item':
        add_item(parsed['checklist_id'], parsed['text'])
        return f"✅ チェックリスト #{parsed['checklist_id']} に項目を追加しました / Item added"

    elif action == 'toggle':
        new_status = toggle_item(parsed['item_id'])
        status_text = "完了" if new_status else "未完了"
        return f"✅ 項目 #{parsed['item_id']} を{status_text}にしました / Item {status_text}"

    elif action == 'delete_item':
        delete_item(parsed['item_id'])
        return f"✅ 項目 #{parsed['item_id']} を削除しました / Item deleted"

    elif action == 'delete':
        delete_checklist(parsed['checklist_id'])
        return f"✅ チェックリスト #{parsed['checklist_id']} を削除しました / Checklist deleted"

    elif action == 'list':
        checklists = list_checklists(category=parsed['category'])

        if not checklists:
            category_text = f" ({parsed['category']})" if parsed['category'] else ""
            return f"📋 チェックリスト{category_text} がありません / No checklists found"

        category_text = f" ({parsed['category']})" if parsed['category'] else ""
        response = f"📋 チェックリスト一覧{category_text} ({len(checklists)}件):\n"
        for cl in checklists:
            response += format_checklist_summary(cl)

        return response

    elif action == 'view':
        items = get_checklist_items(parsed['checklist_id'])

        if not items:
            return f"📋 チェックリスト #{parsed['checklist_id']} に項目がありません / No items in checklist"

        response = f"📋 チェックリスト #{parsed['checklist_id']} ({len(items)}件):\n"
        for item in items:
            response += format_item(item)

        return response

    elif action == 'progress':
        progress = get_progress(parsed['checklist_id'])

        response = f"📊 進捗 #{parsed['checklist_id']}:\n"
        response += f"{progress['completed']}/{progress['total']} 項目完了\n"
        response += f"完了率: {progress['percentage']}%"

        return response

    elif action == 'create_template':
        template_id = create_template(parsed['name'], parsed['description'])
        return f"✅ テンプレート #{template_id} '{parsed['name']}' を作成しました / Template created"

    elif action == 'add_template_item':
        add_template_item(parsed['template_id'], parsed['text'])
        return f"✅ テンプレート #{parsed['template_id']} に項目を追加しました / Item added to template"

    elif action == 'use_template':
        checklist_id = create_from_template(parsed['template_id'], parsed['title'])
        return f"✅ テンプレートからチェックリスト #{checklist_id} '{parsed['title']}' を作成しました / Checklist created from template"

    elif action == 'stats':
        stats = get_stats()

        response = "📊 チェックリスト統計 / Stats:\n"
        response += f"チェックリスト: {stats['total_checklists']}個\n"
        response += f"総項目: {stats['total_items']}件\n"
        response += f"完了: {stats['completed_items']}件"

        return response

    return None

def format_checklist_summary(cl):
    """Format checklist summary"""
    id, title, description, category, created_at = cl

    response = f"\n📋 [{id}] {title}"
    if category:
        response += f" ({category})"
    return response + "\n"

def format_item(item):
    """Format item"""
    id, text, completed, position = item

    status = "✅" if completed else "⬜"
    return f"\n{status} [{id}] {text}\n"

if __name__ == '__main__':
    init_db()
