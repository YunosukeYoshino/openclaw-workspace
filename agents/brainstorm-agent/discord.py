#!/usr/bin/env python3
"""
ブレインストーミングエージェント #18 - Discord連携
"""

import re
from db import *

def parse_message(message):
    """メッセージを解析"""
    # セッション作成
    session_match = re.match(r'(?:セッション|session)[:：]\s*(.+)', message, re.IGNORECASE)
    if session_match:
        return {'action': 'create_session', 'topic': session_match.group(1)}

    # アイデア追加
    idea_match = re.match(r'(?:アイデア|idea)[:：]\s*(.+)', message, re.IGNORECASE)
    if idea_match:
        return parse_idea(idea_match.group(1))

    # アイデア評価
    rate_match = re.match(r'(?:評価|rate)[:：]\s*(\d+)\s+(\d+)', message, re.IGNORECASE)
    if rate_match:
        return {'action': 'rate', 'idea_id': int(rate_match.group(1)), 'rating': int(rate_match.group(2))}

    # セッション一覧
    if message.strip() in ['セッション一覧', '一覧', 'list', 'sessions']:
        return {'action': 'list_sessions'}

    # セッション詳細
    detail_match = re.match(r'(?:詳細|detail)[:：]\s*(\d+)', message, re.IGNORECASE)
    if detail_match:
        return {'action': 'detail', 'session_id': int(detail_match.group(1))}

    return None

def parse_idea(content):
    """アイデアを解析"""
    result = {'action': 'add_idea', 'session_id': None, 'idea': None, 'tags': None}

    # セッションID
    session_match = re.match(r'^(\d+)', content)
    if session_match:
        result['session_id'] = int(session_match.group(1))
        content = content.replace(session_match.group(0), '').strip()

    # タグ
    tag_match = re.search(r'タグ[:：]\s*([^、,]+)', content)
    if tag_match:
        tags_str = tag_match.group(1).strip()
        result['tags'] = [t.strip() for t in tags_str.split(',') if t.strip()]

    # アイデア (残り全部)
    if not result['idea']:
        result['idea'] = content.strip()

    return result

def handle_message(message):
    """メッセージを処理"""
    parsed = parse_message(message)

    if not parsed:
        return None

    action = parsed['action']

    if action == 'create_session':
        if not parsed['topic']:
            return "❌ トピックを入力してください"

        session_id = create_session(parsed['topic'])

        response = f"💡 セッション #{session_id} 作成完了\n"
        response += f"トピック: {parsed['topic']}\n"
        response += "アイデアを追加してください！"

        return response

    elif action == 'add_idea':
        if not parsed['session_id'] or not parsed['idea']:
            return "❌ セッションIDとアイデアを入力してください"

        idea_id = add_idea(parsed['session_id'], parsed['idea'], parsed['tags'])

        response = f"💡 アイデア #{idea_id} 追加完了\n"
        response += f"セッション #{parsed['session_id']}\n"
        response += f"アイデア: {parsed['idea']}"
        if parsed['tags']:
            response += f"\nタグ: {', '.join(parsed['tags'])}"

        return response

    elif action == 'rate':
        rate_idea(parsed['idea_id'], parsed['rating'])
        stars = "⭐" * parsed['rating']
        return f"⭐ アイデア #{parsed['idea_id']} 評価: {parsed['rating']}/5 {stars}"

    elif action == 'list_sessions':
        sessions = list_sessions()

        if not sessions:
            return "💡 セッションがありません"

        response = f"💡 セッション一覧 ({len(sessions)}件):\n"
        for session in sessions:
            response += format_session(session)

        return response

    elif action == 'detail':
        ideas = get_session_ideas(parsed['session_id'])

        if not ideas:
            return f"❌ セッション #{parsed['session_id']} のアイデアがありません"

        response = f"💡 セッション #{parsed['session_id']} アイデア ({len(ideas)}件):\n"
        for idea in ideas:
            response += format_idea(idea)

        return response

    return None

def format_session(session):
    """セッションをフォーマット"""
    id, topic, created_at = session
    return f"\n[{id}] {topic}\n    作成日: {created_at}"

def format_idea(idea):
    """アイデアをフォーマット"""
    id, idea_text, rating, tags, created_at = idea

    stars = "⭐" * rating
    response = f"\n💡 [{id}] {idea_text} {stars}"
    if tags:
        response += f"\n    タグ: {tags}"

    return response

if __name__ == '__main__':
    # テスト
    init_db()

    test_messages = [
        "セッション: 新しいアプリのアイデア出し",
        "アイデア: 1 AI要約機能, タグ: AI, 要約",
        "アイデア: 1 音声入力",
        "アイデア: 1 Slack連携",
        "評価: 1 5",
        "詳細: 1",
        "セッション一覧",
    ]

    for msg in test_messages:
        print(f"\n入力: {msg}")
        result = handle_message(msg)
        if result:
            print(result)
