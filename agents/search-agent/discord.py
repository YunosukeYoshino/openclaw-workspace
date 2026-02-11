#!/usr/bin/env python3
"""
Search Agent - Discord Integration
"""

import re
from datetime import datetime
from db import *

def parse_message(message):
    """Parse message"""
    # Web search
    web_match = re.match(r'(?:ウェブ検索|web search|google)[:：]\s*(.+)', message, re.IGNORECASE)
    if web_match:
        return {'action': 'search', 'type': 'web', 'query': web_match.group(1)}

    # Local search
    local_match = re.match(r'(?:ローカル検索|local search|file search)[:：]\s*(.+)', message, re.IGNORECASE)
    if local_match:
        return {'action': 'search', 'type': 'local', 'query': local_match.group(1)}

    # File search
    file_match = re.match(r'(?:ファイル検索|search file)[:：]\s*(.+)', message, re.IGNORECASE)
    if file_match:
        return {'action': 'search', 'type': 'file', 'query': file_match.group(1)}

    # Search history
    if message.strip() in ['検索履歴', '履歴', 'history', 'search history']:
        return {'action': 'history'}

    # Saved searches
    if message.strip() in ['保存済み検索', 'saved searches', 'saved']:
        return {'action': 'saved'}

    # Save search
    save_match = re.match(r'(?:保存|save)[:：]\s*(\d+)(?:[:：]\s*(.+))?', message)
    if save_match:
        name = save_match.group(2).strip() if save_match.group(2) else None
        return {'action': 'save', 'search_id': int(save_match.group(1)), 'name': name}

    # Statistics
    if message.strip() in ['統計', 'stats', '検索統計']:
        return {'action': 'stats'}

    return None

def handle_message(message):
    """Handle message"""
    parsed = parse_message(message)

    if not parsed:
        return None

    action = parsed['action']

    if action == 'search':
        search_type = parsed['type']
        query = parsed['query']

        search_id = add_search(query, search_type)

        if search_type == 'web':
            return perform_web_search(query, search_id)
        elif search_type == 'local':
            return perform_local_search(query, search_id)
        elif search_type == 'file':
            return perform_file_search(query, search_id)

    elif action == 'history':
        history = get_search_history()

        if not history:
            return "📜 検索履歴がありません (No search history)"

        response = f"📜 検索履歴 ({len(history)}件):\n"
        for search in history:
            response += format_search_history(search)

        return response

    elif action == 'saved':
        saved = get_saved_searches()

        if not saved:
            return "⭐ 保存済み検索がありません (No saved searches)"

        response = f"⭐ 保存済み検索 ({len(saved)}件):\n"
        for search in saved:
            response += format_saved_search(search)

        return response

    elif action == 'save':
        search_id = parsed['search_id']
        name = parsed.get('name')

        if not name:
            # Get query from search history
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute('SELECT query FROM search_history WHERE id = ?', (search_id,))
            result = cursor.fetchone()
            conn.close()

            if result:
                name = result[0]
            else:
                return "❌ 検索が見つかりません (Search not found)"

        saved_id = save_search(search_id, name)

        if saved_id:
            return f"✅ 検索 #{search_id} を保存しました (Saved search #{search_id})"
        else:
            return "❌ 既に保存されています (Already saved)"

    elif action == 'stats':
        stats = get_stats()

        response = "📊 検索統計 / Search Statistics:\n"
        response += f"総検索回数: {stats['total_searches']}回 / Total searches: {stats['total_searches']}\n"
        response += f"保存済み検索: {stats['saved_searches']}件 / Saved searches: {stats['saved_searches']}\n"
        response += f"インデックス済みファイル: {stats['indexed_files']}件 / Indexed files: {stats['indexed_files']}\n"
        response += f"直近7日間の検索: {stats['recent_searches']}回 / Last 7 days: {stats['recent_searches']}\n"

        if stats['by_type']:
            response += f"\n種類別 / By type:\n"
            for stype, count in stats['by_type'].items():
                response += f"  {stype}: {count}回\n"

        return response

    return None

def perform_web_search(query, search_id):
    """Perform web search (placeholder)"""
    # In a real implementation, you would integrate with a search API
    # For now, return a placeholder response

    response = f"🔍 ウェブ検索: {query}\n"
    response += f"検索ID: #{search_id}\n\n"
    response += "⚠️ 注: これはデモバージョンです。\n"
    response += "実際のウェブ検索には、Google Search APIやBing Search APIとの統合が必要です。\n\n"
    response += "検索履歴に保存されました。「保存: {search_id}」で保存できます。"

    # Mock some results
    add_search_result(search_id, "Example Result 1", "https://example.com/1", "This is a sample search result.", 1)
    add_search_result(search_id, "Example Result 2", "https://example.com/2", "Another sample result.", 2)

    return response

def perform_local_search(query, search_id):
    """Perform local search"""
    results = search_local_files(query)

    if not results:
        return f"🔍 ローカル検索「{query}」: 結果なし (No results)"

    response = f"🔍 ローカル検索: {query}\n"
    response += f"検索ID: #{search_id}\n\n"
    response += f"結果 ({len(results)}件):\n"
    for file in results:
        response += format_local_file(file)

    return response

def perform_file_search(query, search_id):
    """Perform file search (same as local search)"""
    return perform_local_search(query, search_id)

def format_search_history(search):
    """Format search history entry"""
    id, query, search_type, result_count, timestamp, saved = search

    response = f"\n[{id}] {query}\n"
    response += f"    タイプ: {search_type} / Type: {search_type}\n"
    response += f"    日時: {timestamp}\n"
    if result_count:
        response += f"    結果数: {result_count}件\n"
    if saved:
        response += "    ⭐ 保存済み / Saved"

    return response

def format_saved_search(search):
    """Format saved search entry"""
    id, name, description, created_at, query, search_type = search

    response = f"\n[#{id}] {name}\n"
    response += f"    クエリ: {query}\n"
    if description:
        response += f"    説明: {description}\n"
    response += f"    保存日時: {created_at}"

    return response

def format_local_file(file):
    """Format local file entry"""
    id, filepath, filename, content_preview, indexed_at, last_modified, file_type = file

    response = f"\n[{id}] {filename}\n"
    response += f"    パス: {filepath}\n"
    if file_type:
        response += f"    タイプ: {file_type}\n"
    if content_preview:
        preview = content_preview[:100] + "..." if len(content_preview) > 100 else content_preview
        response += f"    プレビュー: {preview}"

    return response

if __name__ == '__main__':
    # Test
    import sqlite3

    init_db()

    test_messages = [
        "ウェブ検索: OpenAI ChatGPT",
        "ローカル検索: ドキュメント",
        "検索履歴",
        "保存済み検索",
        "統計",
    ]

    for msg in test_messages:
        print(f"\n入力: {msg}")
        result = handle_message(msg)
        if result:
            print(result)
