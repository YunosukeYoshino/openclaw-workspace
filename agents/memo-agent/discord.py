#!/usr/bin/env python3
"""
メモエージェント #2 - Discord連携
"""

import re
from db import *

def format_stats(stats):
    """統計情報をフォーマット"""
    response = "📊 統計情報:\n"
    response += f"全メモ数: {stats['total_memos']}件\n\n"

    if stats['by_category']:
        response += "カテゴリ別:\n"
        for cat, count in stats['by_category'].items():
            response += f"  - {cat}: {count}件\n"

    if stats['by_tag']:
        response += "\nタグ別:\n"
        for tag, count in stats['by_tag'].items():
            response += f"  - {tag}: {count}件\n"

    return response

def parse_message(message):
    """メッセージを解析"""
    # メモ追加
    memo_match = re.match(r'メモして[:：]\s*(.+)', message)
    if memo_match:
        return parse_add(memo_match.group(1))

    # 検索
    search_match = re.match(r'検索して[:：]\s*(.+)', message)
    if search_match:
        return {'action': 'search', 'keyword': search_match.group(1)}

    # 一覧
    if message.strip() in ['メモ一覧', '一覧', 'list']:
        return {'action': 'list'}

    # カテゴリ
    if message.strip() in ['カテゴリ', 'カテゴリ一覧', 'categories']:
        return {'action': 'categories'}

    # タグ
    if message.strip() in ['タグ', 'タグ一覧', 'tags']:
        return {'action': 'tags'}

    # 統計
    if message.strip() in ['統計', 'stats']:
        return {'action': 'stats'}

    # エクスポート
    if message.strip() in ['エクスポート', 'export']:
        return {'action': 'export'}

    # 削除
    delete_match = re.match(r'削除[:：]\s*(\d+)', message)
    if delete_match:
        return {'action': 'delete', 'memo_id': int(delete_match.group(1))}

    return None

def parse_add(content):
    """メモ追加を解析"""
    result = {'action': 'add', 'title': None, 'content': content, 'category': None, 'tags': None}

    # カテゴリ抽出
    cat_match = re.search(r'カテゴリ[:：]\s*(.+?)(?:,|、|$)', content)
    if cat_match:
        result['category'] = cat_match.group(1).strip()
        content = content.replace(cat_match.group(0), '').strip()

    # タグ抽出
    tag_match = re.search(r'タグ[:：]\s*(.+?)(?:,|、|$)', content)
    if tag_match:
        tags_str = tag_match.group(1).strip()
        result['tags'] = [t.strip() for t in re.split(r'[、,]', tags_str) if t.strip()]
        content = content.replace(tag_match.group(0), '').strip()

    result['content'] = content
    return result

def handle_message(message):
    """メッセージを処理"""
    parsed = parse_message(message)

    if not parsed:
        return None

    action = parsed['action']

    if action == 'add':
        title = parsed['title']
        content = parsed['content']
        category = parsed['category']
        tags = parsed['tags']

        if not content:
            return "❌ 内容を入力してください"

        memo_id = add_memo(title, content, category, tags)

        response = f"✅ メモ #{memo_id} 追加完了\n"
        if title:
            response += f"タイトル: {title}\n"
        response += f"内容: {content}\n"
        if category:
            response += f"カテゴリ: {category}\n"
        if tags:
            response += f"タグ: {', '.join(tags)}"

        return response

    elif action == 'search':
        keyword = parsed['keyword']
        memos = search_memos(keyword)

        if not memos:
            return f"🔍 「{keyword}」の検索結果: 見つかりませんでした"

        response = f"🔍 「{keyword}」の検索結果 ({len(memos)}件):\n"
        for memo in memos:
            id, title, content, category, created_at = memo
            response += f"\n[{id}] {title or 'Untitled'}\n"
            response += f"    {content}...\n"
            if category:
                response += f"    カテゴリ: {category}\n"

        return response

    elif action == 'list':
        memos = list_memos()

        if not memos:
            return "📋 メモがありません"

        response = f"📋 メモ一覧 ({len(memos)}件):\n"
        for memo in memos:
            id, title, content, category, created_at = memo
            response += f"\n[{id}] {title or 'Untitled'}\n"
            response += f"    {content}...\n"
            response += f"    作成日: {created_at}\n"

        return response

    elif action == 'categories':
        categories = get_categories()

        if not categories:
            return "📁 カテゴリがありません"

        response = "📁 カテゴリ一覧:\n"
        for cat in categories:
            response += f"  - {cat[1]}\n"

        return response

    elif action == 'tags':
        tags = get_tags()

        if not tags:
            return "🏷️ タグがありません"

        response = "🏷️ タグ一覧:\n"
        for tag in tags:
            response += f"  - {tag[1]}\n"

        return response

    elif action == 'stats':
        stats = get_stats()
        return format_stats(stats)

    elif action == 'export':
        json_data = export_json()
        response = "📤 エクスポート (JSON):\n"
        response += f"```\n{json_data}\n```"
        return response

    elif action == 'delete':
        memo_id = parsed['memo_id']
        delete_memo(memo_id)
        return f"🗑️ メモ #{memo_id} 削除完了"

    return None

if __name__ == '__main__':
    # テスト
    init_db()

    test_messages = [
        "メモして: 新しいアプリのアイデア, タグ:app, カテゴリ:アイデア",
        "メモして: 学習記録, タグ:学習, カテゴリ:記録",
        "メモして: 野球の試合, タグ:野球, カテゴリ:趣味",
        "検索して: アプリ",
        "メモ一覧",
        "カテゴリ",
        "タグ",
        "統計",
        "エクスポート",
        "削除: 1",
    ]

    for msg in test_messages:
        print(f"\n入力: {msg}")
        result = handle_message(msg)
        if result:
            print(result)
