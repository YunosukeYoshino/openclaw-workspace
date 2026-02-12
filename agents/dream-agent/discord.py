#!/usr/bin/env python3
"""
夢日記エージェント #16 - Discord連携
"""

import re
from db import *

def parse_message(message):
    """メッセージを解析"""
    # 夢追加
    dream_match = re.match(r'(?:夢|dream)[:：]\s*(.+)', message, re.IGNORECASE)
    if dream_match:
        return parse_dream(dream_match.group(1))

    # 検索
    search_match = re.match(r'検索[:：]\s*(.+)', message)
    if search_match:
        return {'action': 'search', 'keyword': search_match.group(1)}

    # 一覧
    if message.strip() in ['夢一覧', '一覧', 'list', 'dreams']:
        return {'action': 'list'}

    # 統計
    if message.strip() in ['統計', 'stats', '夢統計']:
        return {'action': 'stats'}

    return None

def parse_dream(content):
    """夢を解析"""
    result = {'action': 'add_dream', 'content': None, 'type': 'vague', 'mood': None, 'tags': None, 'note': None}

    # 種類
    type_map = {
        'はっきり': 'clear', '明晰': 'clear',
        'ぼや': 'vague', 'あや': 'vague',
        '悪夢': 'nightmare', '怖': 'nightmare',
        '夢': 'lucid',
        '再発': 'recurrent', '繰り返': 'recurrent',
    }

    for key, value in type_map.items():
        if key in content:
            result['type'] = value
            break

    # 感情
    mood_match = re.search(r'感情[:：]\s*([^、,タグメモ]+)', content)
    if mood_match:
        result['mood'] = mood_match.group(1).strip()

    # タグ
    tag_match = re.search(r'タグ[:：]\s*([^、,メモ]+)', content)
    if tag_match:
        tags_str = tag_match.group(1).strip()
        result['tags'] = [t.strip() for t in tags_str.split(',') if t.strip()]

    # メモ
    note_match = re.search(r'メモ[:：]\s*(.+)', content)
    if note_match:
        result['note'] = note_match.group(1).strip()

    # 内容 (残り全部)
    for key in ['感情', 'タグ', 'メモ']:
        content = re.sub(f'{key}[:：].*?(?=（タグ|メモ|$)', '', content)

    result['content'] = content.strip()

    return result

def handle_message(message):
    """メッセージを処理"""
    parsed = parse_message(message)

    if not parsed:
        return None

    action = parsed['action']

    if action == 'add_dream':
        if not parsed['content']:
            return "❌ 夢の内容を入力してください"

        dream_id = add_dream(
            parsed['content'],
            parsed['type'],
            parsed['mood'],
            parsed['tags'],
            parsed['note']
        )

        type_icons = {'clear': '😊', 'vague': '😐', 'nightmare': '😨', 'lucid': '🤩', 'recurrent': '🔄'}
        type_icon = type_icons.get(parsed['type'], '😐')

        response = f"🌙 夢 #{dream_id} 追加完了\n"
        response += f"{type_icon} 種類: {parsed['type']}\n"
        response += f"内容: {parsed['content'][:50]}..."
        if parsed['mood']:
            response += f"\n感情: {parsed['mood']}"
        if parsed['tags']:
            response += f"\nタグ: {', '.join(parsed['tags'])}"
        if parsed['note']:
            response += f"\nメモ: {parsed['note']}"

        return response

    elif action == 'list':
        dreams = list_dreams()

        if not dreams:
            return "🌙 夢がありません"

        response = f"🌙 夢一覧 ({len(dreams)}件):\n"
        for dream in dreams:
            response += format_dream(dream)

        return response

    elif action == 'stats':
        stats = get_dream_stats(days=7)

        type_icons = {'clear': '😊', 'vague': '😐', 'nightmare': '😨', 'lucid': '🤩', 'recurrent': '🔄'}

        response = "📊 週間夢統計:\n"
        response += f"合計: {stats['total']}件\n\n"

        if stats['by_type']:
            response += "種類別:\n"
            for dream_type, count in stats['by_type'].items():
                icon = type_icons.get(dream_type, '😐')
                response += f"  - {icon} {dream_type}: {count}件\n"

        if stats['by_mood']:
            response += "\n感情別:\n"
            for mood, count in stats['by_mood'].items():
                response += f"  - {mood}: {count}件\n"

        return response

    return None

def format_dream(dream):
    """夢をフォーマット"""
    id, content, dream_type, mood, tags, note, created_at = dream

    type_icons = {'clear': '😊', 'vague': '😐', 'nightmare': '😨', 'lucid': '🤩', 'recurrent': '🔄'}
    type_icon = type_icons.get(dream_type, '😐')

    response = f"\n{type_icon} [{id}] {content[:50]}..."
    if mood:
        response += f"\n    感情: {mood}"
    if tags:
        response += f"\n    タグ: {tags}"
    response += f"\n    日時: {created_at}"

    return response

if __name__ == '__main__':
    # テスト
    init_db()

    test_messages = [
        "夢: 空を飛んでいた, 感情: 嬉しい",
        "夢: 怪物に追われていた, 種類: 悪夢, 感情: 怖い",
        "夢: 再発夢、いつも同じ場所, 種類: 再発",
        "夢一覧",
        "統計",
    ]

    for msg in test_messages:
        print(f"\n入力: {msg}")
        result = handle_message(msg)
        if result:
            print(result)
