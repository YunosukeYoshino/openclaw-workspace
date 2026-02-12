#!/usr/bin/env python3
"""
Assistant Agent - Discord Integration
"""

import re
from db import AssistantDB

db = AssistantDB()

def parse_message(message):
    """Parse message"""
    # Set context
    context_match = re.match(r'(?:コンテキスト|context|set)[:：]\s*(.+?)\s*[:：]\s*(.+)', message, re.IGNORECASE)
    if context_match:
        return {'action': 'set_context', 'key': context_match.group(1).strip(), 'value': context_match.group(2).strip()}

    # Add command
    cmd_match = re.match(r'(?:コマンド|command|add-cmd)[:：]\s*(.+?)\s*[:：]\s*(.+?)(?:[:：]\s*(.+))?', message, re.IGNORECASE)
    if cmd_match:
        result = {'action': 'add_command', 'agent_name': cmd_match.group(1).strip(), 'command': cmd_match.group(2).strip()}
        if cmd_match.group(3):
            result['description'] = cmd_match.group(3).strip()
        return result

    # Add knowledge
    kb_match = re.match(r'(?:知識|knowledge|add-kb)[:：]\s*(.+?)\s*[:：]\s*(.+?)(?:[:：]\s*(.+))?', message, re.IGNORECASE)
    if kb_match:
        result = {'action': 'add_knowledge', 'category': kb_match.group(1).strip(), 'question': kb_match.group(2).strip()}
        if kb_match.group(3):
            result['answer'] = kb_match.group(3).strip()
        return result

    # Search knowledge
    search_match = re.match(r'(?:検索|search|kb)[:：]\s*(.+)', message, re.IGNORECASE)
    if search_match:
        return {'action': 'search_knowledge', 'query': search_match.group(1).strip()}

    # List commands
    list_cmd_match = re.match(r'(?:コマンド一覧|commands|list-cmd)(?:[:：]\s*(.+))?', message, re.IGNORECASE)
    if list_cmd_match:
        return {'action': 'list_commands', 'agent_name': list_cmd_match.group(1)}

    # List knowledge
    list_kb_match = re.match(r'(?:知識一覧|knowledge|list-kb)(?:[:：]\s*(.+))?', message, re.IGNORECASE)
    if list_kb_match:
        return {'action': 'list_knowledge', 'category': list_kb_match.group(1)}

    # Stats
    if message.strip() in ['統計', 'stats']:
        return {'action': 'stats'}

    return None

def handle_message(message):
    """Handle message"""
    parsed = parse_message(message)

    if not parsed:
        return None

    action = parsed['action']

    if action == 'set_context':
        # For demo, use a default conversation ID
        conv_id = 1
        db.set_context(conv_id, parsed['key'], parsed['value'])
        return f"✅ コンテキスト設定: {parsed['key']} = {parsed['value']}"

    elif action == 'add_command':
        db.add_agent_command(
            parsed['agent_name'],
            parsed['command'],
            parsed.get('description', '')
        )
        return f"✅ コマンド追加: {parsed['agent_name']} - {parsed['command']}"

    elif action == 'add_knowledge':
        db.add_knowledge(
            parsed['category'],
            parsed['question'],
            parsed.get('answer', '')
        )
        return f"✅ 知識追加: [{parsed['category']}] {parsed['question']}"

    elif action == 'search_knowledge':
        results = db.search_knowledge(parsed['query'], limit=5)

        if not results:
            return f"🔍 「{parsed['query']}」の検索結果: 見つかりませんでした"

        response = f"🔍 「{parsed['query']}」の検索結果 ({len(results)}件):\n"
        for i, item in enumerate(results, 1):
            response += f"\n{i}. [{item['category']}] {item['question']}\n   {item['answer'][:100]}..."

        return response

    elif action == 'list_commands':
        commands = db.get_agent_commands(agent_name=parsed.get('agent_name'))

        if not commands:
            agent_text = f" ({parsed['agent_name']})" if parsed.get('agent_name') else ""
            return f"📋 コマンド{agent_text} がありません"

        agent_text = f" ({parsed['agent_name']})" if parsed.get('agent_name') else ""
        response = f"📋 コマンド一覧{agent_text} ({len(commands)}件):\n"
        for i, cmd in enumerate(commands[:20], 1):
            response += f"\n{i}. [{cmd['agent_name']}] {cmd['command']}"
            if cmd['description']:
                response += f"\n   {cmd['description']}"

        return response

    elif action == 'list_knowledge':
        # Get all knowledge (simplified)
        import sqlite3
        conn = db.get_connection()
        cursor = conn.cursor()

        query = "SELECT id, category, question FROM knowledge"
        params = []

        if parsed.get('category'):
            query += " WHERE category = ?"
            params.append(parsed['category'])

        query += " ORDER BY id DESC LIMIT 20"
        cursor.execute(query, params)
        items = cursor.fetchall()
        conn.close()

        if not items:
            category_text = f" ({parsed['category']})" if parsed.get('category') else ""
            return f"📚 知識{category_text} がありません"

        category_text = f" ({parsed['category']})" if parsed.get('category') else ""
        response = f"📚 知識一覧{category_text} ({len(items)}件):\n"
        for i, item in enumerate(items, 1):
            response += f"\n{i}. [{item[1]}] {item[2]}"

        return response

    elif action == 'stats':
        stats = db.get_conversation_stats()

        response = "📊 アシスタント統計:\n"
        response += f"会話数: {stats['conversations']}\n"
        response += f"メッセージ数: {stats['messages']}\n"
        response += f"コマンド数: {stats['agent_commands']}\n"
        response += f"知識ベース: {stats['knowledge_entries']}件"

        return response

    return None

if __name__ == '__main__':
    db.init_db()

    test_messages = [
        "コンテキスト: user_name : John",
        "コマンド: todo-agent : add : タスクを追加",
        "知識: general : 天気は？ : 天気予報を確認してください",
        "検索: 天気",
        "コマンド一覧",
        "コマンド一覧: todo-agent",
        "統計",
    ]

    for msg in test_messages:
        print(f"\n入力: {msg}")
        result = handle_message(msg)
        if result:
            print(result)
