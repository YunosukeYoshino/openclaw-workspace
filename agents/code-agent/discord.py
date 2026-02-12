#!/usr/bin/env python3
"""
コードスニペットエージェント #7 - Discord連携
"""

import re
from db import *

def parse_message(message):
    """メッセージを解析"""
    # スニペット追加
    snippet_match = re.match(r'(?:スニペット|snippet|code)[:：]\s*(.+)', message, re.IGNORECASE)
    if snippet_match:
        return parse_snippet(snippet_match.group(1))

    # スニペット取得
    get_match = re.match(r'(?:取得|get)[:：]\s*(\d+)', message, re.IGNORECASE)
    if get_match:
        return {'action': 'get', 'snippet_id': int(get_match.group(1))}

    # 検索
    search_match = re.match(r'検索[:：]\s*(.+)', message)
    if search_match:
        return {'action': 'search', 'keyword': search_match.group(1)}

    # 一覧
    if message.strip() in ['スニペット一覧', '一覧', 'list', 'snippets']:
        return {'action': 'list'}

    # 統計
    if message.strip() in ['統計', 'stats', 'スニペット統計']:
        return {'action': 'stats'}

    return None

def parse_snippet(content):
    """スニペットを解析"""
    result = {'action': 'add', 'title': None, 'language': None, 'code': None, 'memo': None}

    # タイトル
    title_match = re.search(r'タイトル[:：]\s*([^、,（\(【]+)', content)
    if title_match:
        result['title'] = title_match.group(1).strip()
        content = content.replace(title_match.group(0), '').strip()

    # 言語
    language_match = re.search(r'言語[:：]\s*([^、,]+)', content)
    if language_match:
        result['language'] = language_match.group(1).strip()

    # メモ
    memo_match = re.search(r'メモ[:：]\s*(.+)', content)
    if memo_match:
        result['memo'] = memo_match.group(1).strip()
        content = content.replace(memo_match.group(0), '').strip()

    # コード (残り全部)
    result['code'] = content.strip()

    # タイトルがまだない場合、コードの最初の行をタイトルとする
    if not result['title']:
        lines = result['code'].split('\n')
        if lines and lines[0]:
            result['title'] = lines[0][:50]

    return result

def handle_message(message):
    """メッセージを処理"""
    parsed = parse_message(message)

    if not parsed:
        return None

    action = parsed['action']

    if action == 'add':
        if not parsed['code']:
            return "❌ コードを入力してください"

        snippet_id = add_snippet(
            parsed['title'] or 'Untitled',
            parsed['code'],
            parsed['language'],
            parsed['memo']
        )

        response = f"💻 スニペット #{snippet_id} 追加完了\n"
        response += f"タイトル: {parsed['title'] or 'Untitled'}\n"
        if parsed['language']:
            response += f"言語: {parsed['language']}"
        if parsed['memo']:
            response += f"\nメモ: {parsed['memo']}"

        return response

    elif action == 'get':
        snippet = get_snippet(parsed['snippet_id'])
        if not snippet:
            return f"❌ スニペット #{parsed['snippet_id']} が見つかりません"

        return format_snippet_full(snippet)

    elif action == 'search':
        keyword = parsed['keyword']
        snippets = search_snippets(keyword)

        if not snippets:
            return f"🔍 「{keyword}」の検索結果: 見つかりませんでした"

        response = f"🔍 「{keyword}」の検索結果 ({len(snippets)}件):\n"
        for snippet in snippets:
            response += format_snippet(snippet)

        return response

    elif action == 'list':
        snippets = list_snippets()

        if not snippets:
            return "💻 スニペットがありません"

        response = f"💻 スニペット一覧 ({len(snippets)}件):\n"
        for snippet in snippets:
            response += format_snippet(snippet)

        return response

    elif action == 'stats':
        stats = get_stats()

        response = "📊 スニペット統計:\n"
        response += f"全スニペット数: {stats['total_snippets']}件\n\n"

        if stats['by_language']:
            response += "言語別:\n"
            for lang, count in stats['by_language'].items():
                response += f"  - {lang}: {count}件\n"

        return response

    return None

def format_snippet(snippet):
    """スニペットをフォーマット（一覧用）"""
    id, title, language, created_at = snippet
    response = f"\n[{id}] {title}"
    if language:
        response += f" ({language})"
    response += f"\n    作成日: {created_at}"
    return response

def format_snippet_full(snippet):
    """スニペットをフォーマット（詳細用）"""
    id, title, language, code, memo, created_at = snippet

    response = f"💻 スニペット #{id}\n"
    response += f"タイトル: {title}\n"
    if language:
        response += f"言語: {language}\n"
    response += f"作成日: {created_at}\n\n"
    if memo:
        response += f"メモ: {memo}\n\n"

    # コード
    response += "```"
    if language:
        response += language
    response += f"\n{code}\n```"

    return response

if __name__ == '__main__':
    # テスト
    init_db()

    test_messages = [
        "スニペット: タイトル:Hello World, 言語:Python, コード:print('Hello, World!')",
        "スニペット: タイトル:FizzBuzz, 言語:JavaScript, メモ:有名な問題, コード:for(let i=1;i<=100;i++){console.log(i%15==0?'FizzBuzz':i%3==0?'Fizz':i%5==0?'Buzz':i)}",
        "スニペット: タイトル:配列逆転, 言語:Python, コード:def reverse(arr): return arr[::-1]",
        "検索: Python",
        "取得: 1",
        "一覧",
        "統計",
    ]

    for msg in test_messages:
        print(f"\n入力: {msg}")
        result = handle_message(msg)
        if result:
            print(result)
