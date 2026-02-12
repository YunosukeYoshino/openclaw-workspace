#!/usr/bin/env python3
"""
名言エージェント #20 - Discord連携
"""

import re
from db import *

def parse_message(message):
    """メッセージを解析"""
    # 名言追加
    quote_match = re.match(r'(?:名言|quote)[:：]\s*(.+)', message, re.IGNORECASE)
    if quote_match:
        return parse_quote(quote_match.group(1))

    # 検索
    search_match = re.match(r'検索[:：]\s*(.+)', message)
    if search_match:
        return {'action': 'search', 'keyword': search_match.group(1)}

    # 一覧
    if message.strip() in ['名言一覧', '一覧', 'list', 'quotes']:
        return {'action': 'list'}

    # ランダム
    if message.strip() in ['ランダム', 'random', '名言']:
        return {'action': 'random'}

    # 評価
    rate_match = re.match(r'(?:評価|rate)[:：]\s*(\d+)\s+(\d+)', message, re.IGNORECASE)
    if rate_match:
        return {'action': 'rate', 'quote_id': int(rate_match.group(1)), 'rating': int(rate_match.group(2))}

    return None

def parse_quote(content):
    """名言を解析"""
    result = {'action': 'add_quote', 'content': None, 'author': None, 'category': None, 'tags': None}

    # 作者
    author_match = re.search(r'作者[:：]\s*([^、,]+)', content)
    if author_match:
        result['author'] = author_match.group(1).strip()
        content = content.replace(author_match.group(0), '').strip()

    # カテゴリ
    category_match = re.search(r'カテゴリ[:：]\s*([^、,]+)', content)
    if category_match:
        result['category'] = category_match.group(1).strip()
        content = content.replace(category_match.group(0), '').strip()

    # タグ
    tag_match = re.search(r'タグ[:：]\s*([^、,]+)', content)
    if tag_match:
        tags_str = tag_match.group(1).strip()
        result['tags'] = [t.strip() for t in tags_str.split(',') if t.strip()]
        content = content.replace(tag_match.group(0), '').strip()

    # 内容 (残り全部)
    result['content'] = content.strip()

    return result

def handle_message(message):
    """メッセージを処理"""
    parsed = parse_message(message)

    if not parsed:
        return None

    action = parsed['action']

    if action == 'add_quote':
        if not parsed['content']:
            return "❌ 名言の内容を入力してください"

        quote_id = add_quote(
            parsed['content'],
            parsed['author'],
            parsed['category'],
            parsed['tags']
        )

        response = f"💬 名言 #{quote_id} 追加完了\n"
        response += f"内容: {parsed['content']}\n"
        if parsed['author']:
            response += f"作者: {parsed['author']}"
        if parsed['category']:
            response += f"\nカテゴリ: {parsed['category']}"
        if parsed['tags']:
            response += f"\nタグ: {', '.join(parsed['tags'])}"

        return response

    elif action == 'list':
        quotes = list_quotes()

        if not quotes:
            return "💬 名言がありません"

        response = f"💬 名言一覧 ({len(quotes)}件):\n"
        for quote in quotes:
            response += format_quote(quote)

        return response

    elif action == 'search':
        keyword = parsed['keyword']
        quotes = search_quotes(keyword)

        if not quotes:
            return f"🔍 「{keyword}」の検索結果: 見つかりませんでした"

        response = f"🔍 「{keyword}」の検索結果 ({len(quotes)}件):\n"
        for quote in quotes:
            response += format_quote(quote)

        return response

    elif action == 'random':
        import random
        quotes = list_quotes(limit=100)

        if not quotes:
            return "💬 名言がありません"

        quote = random.choice(quotes)
        return format_quote_full(quote)

    elif action == 'rate':
        rate_quote(parsed['quote_id'], parsed['rating'])
        stars = "⭐" * parsed['rating']
        return f"⭐ 名言 #{parsed['quote_id']} 評価: {parsed['rating']}/5 {stars}"

    return None

def format_quote(quote):
    """名言をフォーマット（一覧用）"""
    id, content, author, category, rating = quote

    stars = "⭐" * rating

    response = f"\n💬 [{id}] {content[:30]}..."
    if author:
        response += f"\n    作者: {author}"
    if category:
        response += f"\n    カテゴリ: {category}"
    if rating > 0:
        response += f"\n    評価: {stars}"

    return response

def format_quote_full(quote):
    """名言をフォーマット（詳細用）"""
    id, content, author, category, rating = quote

    stars = "⭐" * rating

    response = f"💬 名言 #{id}\n"
    response += f"「{content}」"
    if author:
        response += f"\n    - {author}"
    if category:
        response += f"\n    カテゴリ: {category}"
    if rating > 0:
        response += f"\n    評価: {stars}"

    return response

if __name__ == '__main__':
    # テスト
    init_db()

    test_messages = [
        "名言: 失敗は成功のもと, 作者:トーマス・エジソン, カテゴリ:成功",
        "名言: 継続は力なり, 作者:エジソン, カテゴリ:努力",
        "名言: すべての道はローマに通ず",
        "名言一覧",
        "ランダム",
    ]

    for msg in test_messages:
        print(f"\n入力: {msg}")
        result = handle_message(msg)
        if result:
            print(result)
