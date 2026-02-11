#!/usr/bin/env python3
"""
Communication Agent #28 - Discord Integration
"""

import re
from db import *

def parse_message(message):
    """Parse message"""
    # Add message
    add_match = re.match(r'(?:送信|send|add)[:：]\s*(.+)', message, re.IGNORECASE)
    if add_match:
        return parse_add(add_match.group(1))

    # List messages
    list_match = re.match(r'(?:一覧|list|messages)(?:[:：]\s*(.+))?', message, re.IGNORECASE)
    if list_match:
        param = list_match.group(1) if list_match.group(1) else None
        return {'action': 'list', 'param': param}

    # Search messages
    search_match = re.match(r'(?:検索|search)[:：]\s*(.+)', message, re.IGNORECASE)
    if search_match:
        return {'action': 'search', 'keyword': search_match.group(1)}

    # List conversations
    if message.strip() in ['会話', 'conversations']:
        return {'action': 'list_conversations'}

    # View conversation
    view_match = re.match(r'(?:詳細|view|history)[:：]\s*(.+)', message, re.IGNORECASE)
    if view_match:
        return {'action': 'view_conversation', 'participant': view_match.group(1)}

    # Archive conversation
    archive_match = re.match(r'(?:アーカイブ|archive)[:：]\s*(.+)', message, re.IGNORECASE)
    if archive_match:
        return {'action': 'archive', 'participant': archive_match.group(1)}

    # Stats
    if message.strip() in ['統計', 'stats']:
        return {'action': 'stats'}

    return None

def parse_add(content):
    """Parse add content"""
    result = {'action': 'add', 'sender': None, 'content': None, 'recipient': None, 'channel': None, 'direction': None, 'tags': None, 'notes': None}

    # Direction
    direction_match = re.match(r'^(受信|in|inbound|送信|out|outbound)[:：]\s*', content, re.IGNORECASE)
    if direction_match:
        direction = direction_match.group(1).lower()
        result['direction'] = 'inbound' if direction in ['受信', 'in', 'inbound'] else 'outbound'
        content = content[direction_match.end():]
    else:
        result['direction'] = 'inbound'

    # Extract sender/recipient and content
    if result['direction'] == 'inbound':
        # Format: From Name, message
        from_match = re.match(r'^(.+?)\s*[,，]\s*(.+)', content)
        if from_match:
            result['sender'] = from_match.group(1).strip()
            result['content'] = from_match.group(2).strip()
    else:
        # Format: To Name, message
        to_match = re.match(r'^(.+?)\s*[,，]\s*(.+)', content)
        if to_match:
            result['recipient'] = to_match.group(1).strip()
            result['content'] = to_match.group(2).strip()

    # Channel
    channel_match = re.search(r'チャンネル|channel[:：]\s*(.+?)(?:[、,]|$)', content)
    if channel_match:
        result['channel'] = channel_match.group(1).strip()

    # Tags
    tags_match = re.search(r'タグ|tags[:：]\s*(.+)', content)
    if tags_match:
        result['tags'] = tags_match.group(1).strip()

    # Notes
    note_match = re.search(r'メモ|notes[:：]\s*(.+)', content)
    if note_match:
        result['notes'] = note_match.group(1).strip()

    return result

def handle_message(message):
    """Handle message"""
    parsed = parse_message(message)

    if not parsed:
        return None

    action = parsed['action']

    if action == 'add':
        if not parsed['content']:
            return "❌ メッセージ内容を入力してください"
        if not parsed['sender'] and not parsed['recipient']:
            return "❌ 送信者または受信者を入力してください"

        message_id = add_message(
            parsed['sender'],
            parsed['content'],
            parsed['recipient'],
            parsed['channel'],
            direction=parsed['direction'],
            tags=parsed['tags'],
            notes=parsed['notes']
        )

        direction_text = "→" if parsed['direction'] == 'outbound' else "←"
        participant = parsed['recipient'] if parsed['direction'] == 'outbound' else parsed['sender']

        response = f"💬 メッセージ #{message_id} 記録完了\n"
        response += f"{direction_text} {participant}: {parsed['content'][:50]}{'...' if len(parsed['content']) > 50 else ''}"

        return response

    elif action == 'list':
        param = parsed['param']
        if param:
            messages = list_messages(sender=param) or list_messages(recipient=param)
        else:
            messages = list_messages()

        if not messages:
            return f"💬 メッセージがありません"

        response = f"💬 メッセージ一覧 ({len(messages)}件):\n"
        for msg in messages:
            response += format_message(msg)

        return response

    elif action == 'search':
        messages = search_messages(parsed['keyword'])

        if not messages:
            return f"🔍 「{parsed['keyword']}」の検索結果: 見つかりませんでした"

        response = f"🔍 「{parsed['keyword']}」の検索結果 ({len(messages)}件):\n"
        for msg in messages:
            response += format_message(msg)

        return response

    elif action == 'list_conversations':
        convos = list_conversations()

        if not convos:
            return "👥 会話がありません"

        response = f"👥 会話一覧 ({len(convos)}件):\n"
        for conv in convos:
            response += format_conversation(conv)

        return response

    elif action == 'view_conversation':
        messages = get_conversation_messages(parsed['participant'])

        if not messages:
            return f"💬 {parsed['participant']} との会話はありません"

        response = f"💬 {parsed['participant']} との会話 ({len(messages)}件):\n"
        for msg in messages:
            response += format_message(msg)

        return response

    elif action == 'archive':
        archive_conversation(parsed['participant'])
        return f"📦 {parsed['participant']} との会話をアーカイブ"

    elif action == 'stats':
        stats = get_stats()

        response = "📊 通信統計:\n"
        response += f"全メッセージ: {stats['total_messages']}件\n"
        response += f"全会話: {stats['total_conversations']}件\n"
        response += f"アクティブ会話: {stats['active_conversations']}件\n"
        response += f"受信: {stats['inbound']}件\n"
        response += f"送信: {stats['outbound']}件"

        return response

    return None

def format_message(msg):
    """Format message"""
    id, sender, recipient, channel, content, message_type, direction, status, tags, created_at = msg

    direction_icon = "→" if direction == 'outbound' else "←"
    participant = recipient if direction == 'outbound' else sender

    response = f"\n{direction_icon} [{id}] {participant}\n"
    response += f"    {content[:60]}{'...' if len(content) > 60 else ''}\n"

    return response

def format_conversation(conv):
    """Format conversation"""
    id, participant, topic, last_message_date, message_count, status, notes, created_at = conv

    status_icon = "🟢" if status == 'active' else "📦"

    response = f"\n{status_icon} [{id}] {participant} ({message_count}件)\n"
    if last_message_date:
        response += f"    最終: {last_message_date}\n"

    return response

if __name__ == '__main__':
    init_db()

    test_messages = [
        "受信: 田中太郎, 会議の日程を確認してください",
        "送信: 佐藤花子, 明日のミーティングの資料を送ります",
        "一覧",
        "検索: 会議",
        "会話",
        "詳細: 田中太郎",
        "統計",
    ]

    for msg in test_messages:
        print(f"\n入力: {msg}")
        result = handle_message(msg)
        if result:
            print(result)
