#!/usr/bin/env python3
"""
Archive Agent - Discord連携
- アーカイブアイテムの登録・管理
- アーカイブカテゴリの管理
- アーカイブの検索・参照
- アーカイブのステータス管理（アクティブ/アーカイブ済み）
"""

import re
from datetime import datetime, timedelta
from db import *

def parse_message(message):
    """メッセージを解析"""
    # アイテム追加
    add_match = re.match(r'(?:アーカイブ|archive|追加|add)[:：]\s*(.+)', message, re.IGNORECASE)
    if add_match:
        return parse_add(add_match.group(1))

    # アイテム更新
    update_match = re.match(r'(?:更新|update)[:：]\s*(\d+)\s*,\s*(.+)', message, re.IGNORECASE)
    if update_match:
        return {'action': 'update', 'item_id': int(update_match.group(1)), 'content': update_match.group(2)}

    # アーカイブ（アイテムをアーカイブ済みに）
    archive_match = re.match(r'(?:アーカイブ実行|archive执行|to_archive)[:：]\s*(\d+)', message, re.IGNORECASE)
    if archive_match:
        return {'action': 'archive', 'item_id': int(archive_match.group(1))}

    # アーカイブ解除
    unarchive_match = re.match(r'(?:アーカイブ解除|unarchive|restore)[:：]\s*(\d+)', message, re.IGNORECASE)
    if unarchive_match:
        return {'action': 'unarchive', 'item_id': int(unarchive_match.group(1))}

    # 削除
    delete_match = re.match(r'(?:削除|delete|del)[:：]\s*(\d+)', message, re.IGNORECASE)
    if delete_match:
        return {'action': 'delete', 'item_id': int(delete_match.group(1))}

    # アイテム一覧
    list_match = re.match(r'(?:(?:アーカイブ|archive)(?:一覧|list)|list_archive)(?:[:：]\s*(.+))?', message, re.IGNORECASE)
    if list_match:
        options = list_match.group(1) if list_match.group(1) else None
        return parse_list_options(options)

    # 検索
    search_match = re.match(r'(?:検索|search|find)[:：]\s*(.+)', message, re.IGNORECASE)
    if search_match:
        keyword = search_match.group(1)
        return {'action': 'search', 'keyword': keyword}

    # アイテム詳細
    detail_match = re.match(r'(?:詳細|detail|view)[:：]\s*(\d+)', message, re.IGNORECASE)
    if detail_match:
        return {'action': 'detail', 'item_id': int(detail_match.group(1))}

    # カテゴリ追加
    cat_add_match = re.match(r'(?:カテゴリ|category)(?:追加|add|new)[:：]\s*(.+)', message, re.IGNORECASE)
    if cat_add_match:
        return parse_category_add(cat_add_match.group(1))

    # カテゴリ一覧
    if message.strip() in ['カテゴリ一覧', 'categories', 'cat_list', 'list_categories']:
        return {'action': 'list_categories'}

    # カテゴリ削除
    cat_del_match = re.match(r'(?:カテゴリ|category)(?:削除|delete|del)[:：]\s*(\d+)', message, re.IGNORECASE)
    if cat_del_match:
        return {'action': 'delete_category', 'category_id': int(cat_del_match.group(1))}

    # タグ一覧
    if message.strip() in ['タグ一覧', 'tags', 'tag_list', 'list_tags']:
        return {'action': 'list_tags'}

    # タグで検索
    tag_search_match = re.match(r'(?:タグ|tag)[:：]\s*(.+)', message, re.IGNORECASE)
    if tag_search_match:
        return {'action': 'search_tag', 'tag_name': tag_search_match.group(1)}

    # タグ追加
    tag_add_match = re.match(r'(?:タグ追加|add_tag)[:：]\s*(\d+)\s*,\s*(.+)', message, re.IGNORECASE)
    if tag_add_match:
        return {'action': 'add_tag', 'item_id': int(tag_add_match.group(1)), 'tag_name': tag_add_match.group(2)}

    # タグ削除
    tag_del_match = re.match(r'(?:タグ削除|remove_tag)[:：]\s*(\d+)\s*,\s*(.+)', message, re.IGNORECASE)
    if tag_del_match:
        return {'action': 'remove_tag', 'item_id': int(tag_del_match.group(1)), 'tag_name': tag_del_match.group(2)}

    # 統計
    if message.strip() in ['統計', 'stats', 'アーカイブ統計', 'archive_stats']:
        return {'action': 'stats'}

    return None

def parse_add(content):
    """追加コマンドを解析"""
    result = {'action': 'add', 'title': None, 'description': None, 'content': None,
              'category_id': None, 'category_name': None, 'status': 'active',
              'tags': None, 'priority': 0, 'url': None}

    # タイトル（最初の部分）
    parts = re.split(r'[,\uff0c]', content)
    if parts:
        result['title'] = parts[0].strip()

    # 説明
    desc_match = re.search(r'説明[:：]\s*([^,\uff0c]+)', content, re.IGNORECASE)
    if desc_match:
        result['description'] = desc_match.group(1).strip()

    # コンテンツ
    content_match = re.search(r'内容[:：]\s*(.+)', content, re.IGNORECASE)
    if content_match:
        result['content'] = content_match.group(1).strip()

    # カテゴリ（IDまたは名前）
    cat_match = re.search(r'カテゴリ[:：]\s*([^,\uff0c]+)', content, re.IGNORECASE)
    if cat_match:
        cat_val = cat_match.group(1).strip()
        # IDかどうか判定
        if cat_val.isdigit():
            result['category_id'] = int(cat_val)
        else:
            result['category_name'] = cat_val

    # ステータス
    status_match = re.search(r'ステータス[:：]\s*(active|archived|アクティブ|アーカイブ済み)', content, re.IGNORECASE)
    if status_match:
        status_val = status_match.group(1).lower()
        if status_val in ['archived', 'アーカイブ済み']:
            result['status'] = 'archived'

    # タグ
    tags_match = re.search(r'タグ[:：]\s*([^,\uff0c]+)', content, re.IGNORECASE)
    if tags_match:
        result['tags'] = tags_match.group(1).strip()

    # 優先度
    priority_match = re.search(r'優先度[:：]\s*(\d+)', content, re.IGNORECASE)
    if priority_match:
        result['priority'] = int(priority_match.group(1))

    # URL
    url_match = re.search(r'URL[:：]\s*(https?://\S+)', content, re.IGNORECASE)
    if url_match:
        result['url'] = url_match.group(1).strip()

    # タイトルがまだない場合、説明より前をタイトルとする
    if not result['title']:
        desc_match = re.search(r'説明[:：]', content)
        if desc_match:
            result['title'] = content[:desc_match.start()].strip()
        else:
            result['title'] = content.strip()

    return result

def parse_category_add(content):
    """カテゴリ追加を解析"""
    result = {'action': 'add_category', 'name': None, 'description': None, 'color': None}

    # 名前
    parts = re.split(r'[,\uff0c]', content)
    if parts:
        result['name'] = parts[0].strip()

    # 説明
    desc_match = re.search(r'説明[:：]\s*([^,\uff0c]+)', content, re.IGNORECASE)
    if desc_match:
        result['description'] = desc_match.group(1).strip()

    # 色
    color_match = re.search(r'色[:：]\s*([^,\uff0c]+)', content, re.IGNORECASE)
    if color_match:
        result['color'] = color_match.group(1).strip()

    # 名前がまだない場合、説明より前を名前とする
    if not result['name']:
        desc_match = re.search(r'説明[:：]', content)
        if desc_match:
            result['name'] = content[:desc_match.start()].strip()
        else:
            result['name'] = content.strip()

    return result

def parse_list_options(options):
    """一覧オプションを解析"""
    result = {'action': 'list', 'status': None, 'category_id': None, 'limit': 20}

    if not options:
        return result

    # ステータス
    status_match = re.search(r'(?:ステータス|status)[:：]\s*(active|archived|アクティブ|アーカイブ済み)', options, re.IGNORECASE)
    if status_match:
        status_val = status_match.group(1).lower()
        if status_val in ['archived', 'アーカイブ済み']:
            result['status'] = 'archived'
        else:
            result['status'] = 'active'

    # カテゴリID
    cat_match = re.search(r'(?:カテゴリ|category)[:：]\s*(\d+)', options, re.IGNORECASE)
    if cat_match:
        result['category_id'] = int(cat_match.group(1))

    # 件数
    limit_match = re.search(r'(?:件数|limit)[:：]\s*(\d+)', options, re.IGNORECASE)
    if limit_match:
        result['limit'] = int(limit_match.group(1))

    return result

def handle_message(message):
    """メッセージを処理"""
    parsed = parse_message(message)

    if not parsed:
        return None

    action = parsed['action']

    if action == 'add':
        if not parsed['title']:
            return "❌ タイトルを入力してください"

        # カテゴリ名からIDを取得
        category_id = parsed['category_id']
        if parsed['category_name']:
            categories = list_categories()
            for cat in categories:
                if cat[1] == parsed['category_name']:
                    category_id = cat[0]
                    break

        item_id = add_archive_item(
            parsed['title'],
            parsed['description'],
            parsed['content'],
            category_id,
            parsed['status'],
            parsed['tags'],
            parsed['priority'],
            parsed['url']
        )

        response = f"✅ アーカイブアイテム #{item_id} 追加完了\n"
        response += f"タイトル: {parsed['title']}\n"
        if parsed['description']:
            response += f"説明: {parsed['description']}\n"
        if category_id:
            response += f"カテゴリ: #{category_id}\n"
        if parsed['status'] == 'archived':
            response += f"ステータス: アーカイブ済み\n"
        if parsed['tags']:
            response += f"タグ: {parsed['tags']}\n"
        if parsed['priority']:
            response += f"優先度: {parsed['priority']}\n"
        if parsed['url']:
            response += f"URL: {parsed['url']}"

        return response

    elif action == 'update':
        # 更新オプションを解析
        updates = {}
        options = parsed['content']

        title_match = re.search(r'タイトル[:：]\s*(.+?)(?:[,\uff0c]|$)', options)
        if title_match:
            updates['title'] = title_match.group(1).strip()

        desc_match = re.search(r'説明[:：]\s*(.+?)(?:[,\uff0c]|$)', options)
        if desc_match:
            updates['description'] = desc_match.group(1).strip()

        content_match = re.search(r'内容[:：]\s*(.+)', options)
        if content_match:
            updates['content'] = content_match.group(1).strip()

        status_match = re.search(r'ステータス[:：]\s*(active|archived)', options, re.IGNORECASE)
        if status_match:
            updates['status'] = status_match.group(1).lower()

        priority_match = re.search(r'優先度[:：]\s*(\d+)', options)
        if priority_match:
            updates['priority'] = int(priority_match.group(1))

        if not updates:
            return "❌ 更新内容を指定してください"

        update_archive_item(parsed['item_id'], **updates)
        return f"✅ アイテム #{parsed['item_id']} 更新完了"

    elif action == 'archive':
        archive_item(parsed['item_id'])
        return f"📦 アイテム #{parsed['item_id']} をアーカイブしました"

    elif action == 'unarchive':
        unarchive_item(parsed['item_id'])
        return f"📤 アイテム #{parsed['item_id']} のアーカイブを解除しました"

    elif action == 'delete':
        delete_archive_item(parsed['item_id'])
        return f"🗑️ アイテム #{parsed['item_id']} 削除完了"

    elif action == 'list':
        items = list_archive_items(
            status=parsed.get('status'),
            category_id=parsed.get('category_id'),
            limit=parsed.get('limit', 20)
        )

        if not items:
            status_text = f" ({parsed.get('status')})" if parsed.get('status') else ""
            return f"📋 アーカイブアイテム{status_text} がありません"

        status_text = f" ({parsed.get('status')})" if parsed.get('status') else ""
        response = f"📋 アーカイブ一覧{status_text} ({len(items)}件):\n"
        for item in items:
            response += format_item(item)

        return response

    elif action == 'search':
        items = search_archive_items(parsed['keyword'])

        if not items:
            return f"🔍 '{parsed['keyword']}' に一致するアイテムがありません"

        response = f"🔍 検索結果: '{parsed['keyword']}' ({len(items)}件):\n"
        for item in items:
            response += format_item(item)

        return response

    elif action == 'detail':
        item = get_archive_item(parsed['item_id'])

        if not item:
            return f"❌ アイテム #{parsed['item_id']} が見つかりません"

        response = format_item_detail(item)

        # タグも表示
        tags = get_item_tags(parsed['item_id'])
        if tags:
            response += "\n🏷️ タグ: " + ", ".join([tag[1] for tag in tags])

        return response

    elif action == 'add_category':
        if not parsed['name']:
            return "❌ カテゴリ名を入力してください"

        category_id = add_category(parsed['name'], parsed['description'], parsed['color'])

        if category_id is None:
            return "❌ そのカテゴリ名は既に存在します"

        response = f"✅ カテゴリ #{category_id} 追加完了\n"
        response += f"名前: {parsed['name']}\n"
        if parsed['description']:
            response += f"説明: {parsed['description']}\n"
        if parsed['color']:
            response += f"色: {parsed['color']}"

        return response

    elif action == 'list_categories':
        categories = list_categories()

        if not categories:
            return "📁 カテゴリがありません"

        response = f"📁 カテゴリ一覧 ({len(categories)}件):\n"
        for cat in categories:
            response += f"  [{cat[0]}] {cat[1]}"
            if cat[2]:
                response += f" - {cat[2]}"
            response += "\n"

        return response

    elif action == 'delete_category':
        delete_category(parsed['category_id'])
        return f"🗑️ カテゴリ #{parsed['category_id']} 削除完了"

    elif action == 'list_tags':
        tags = get_all_tags()

        if not tags:
            return "🏷️ タグがありません"

        response = f"🏷️ タグ一覧 ({len(tags)}件):\n"
        for tag in tags:
            response += f"  [{tag[0]}] {tag[1]} ({tag[2]}件)\n"

        return response

    elif action == 'search_tag':
        items = get_items_by_tag(parsed['tag_name'])

        if not items:
            return f"🏷️ タグ '{parsed['tag_name']}' のアイテムがありません"

        response = f"🏷️ タグ '{parsed['tag_name']}' のアイテム ({len(items)}件):\n"
        for item in items:
            response += format_item(item)

        return response

    elif action == 'add_tag':
        add_tag_to_item(parsed['item_id'], parsed['tag_name'])
        return f"✅ タグ '{parsed['tag_name']}' をアイテム #{parsed['item_id']} に追加"

    elif action == 'remove_tag':
        remove_tag_from_item(parsed['item_id'], parsed['tag_name'])
        return f"✅ タグ '{parsed['tag_name']}' をアイテム #{parsed['item_id']} から削除"

    elif action == 'stats':
        stats = get_archive_stats()

        response = "📊 アーカイブ統計:\n"
        response += f"カテゴリ: {stats['total_categories']}件\n"
        response += f"全アイテム: {stats['total_items']}件\n"
        response += f"アクティブ: {stats['active_items']}件\n"
        response += f"アーカイブ済み: {stats['archived_items']}件\n"
        response += f"タグ: {stats['total_tags']}件\n"
        response += f"今日追加: {stats['today_added']}件\n"
        response += f"今月アーカイブ: {stats['month_archived']}件"

        if stats['by_category']:
            response += "\n\n📁 カテゴリ別:\n"
            for cat_name, count in stats['by_category']:
                response += f"  • {cat_name}: {count}件\n"

        return response

    return None

def format_item(item):
    """アイテムをフォーマット"""
    id, title, description, category_id, status, tags, priority, url, archived_at, created_at, updated_at = item

    # ステータス表示
    status_icon = "📦" if status == 'archived' else "📄"
    if status == 'active':
        status_icon = "📋"

    # 優先度表示
    priority_text = f" ⭐{priority}" if priority > 0 else ""

    response = f"\n{status_icon} [{id}] {title}{priority_text}\n"
    if description:
        desc_preview = description[:50] + "..." if len(description) > 50 else description
        response += f"    {desc_preview}\n"
    if category_id:
        response += f"    📁 カテゴリ: #{category_id}\n"
    if tags:
        response += f"    🏷️ {tags}\n"
    if url:
        response += f"    🔗 {url}\n"
    response += f"    📅 {created_at[:10]}"

    return response

def format_item_detail(item):
    """アイテム詳細をフォーマット"""
    id, title, description, content, category_id, status, tags, priority, url, file_path, metadata, archived_at, created_at, updated_at = item

    response = f"📋 アイテム詳細 #{id}:\n"
    response += f"タイトル: {title}\n"
    if description:
        response += f"説明: {description}\n"
    if content:
        response += f"内容: {content}\n"
    if category_id:
        response += f"カテゴリ: #{category_id}\n"
    response += f"ステータス: {'アーカイブ済み' if status == 'archived' else 'アクティブ'}\n"
    if priority:
        response += f"優先度: {priority}\n"
    if url:
        response += f"URL: {url}\n"
    if file_path:
        response += f"ファイル: {file_path}\n"
    if archived_at:
        response += f"アーカイブ日: {archived_at}\n"
    response += f"作成日時: {created_at}\n"
    response += f"更新日時: {updated_at}"

    return response

if __name__ == '__main__':
    # テスト
    init_db()

    test_messages = [
        "カテゴリ追加: ドキュメント, 説明: 重要なドキュメント",
        "アーカイブ: プロジェクト計画書, 説明: Q1の計画, カテゴリ: ドキュメント, 優先度: 3",
        "アーカイブ: 会議メモ 2025-02-12, タグ: 会議, メモ",
        "アーカイブ一覧",
        "詳細: 1",
        "検索: 計画",
        "タグ: 会議",
        "統計",
        "アーカイブ実行: 1",
    ]

    for msg in test_messages:
        print(f"\n入力: {msg}")
        result = handle_message(msg)
        if result:
            print(result)
