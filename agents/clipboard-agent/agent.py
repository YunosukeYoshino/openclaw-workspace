#!/usr/bin/env python3
"""
クリップボード管理エージェント - Discord連携
Clipboard Management Agent - Discord Integration
"""

import re
from datetime import datetime
from db import *

def parse_message(message):
    """メッセージを解析 / Parse message"""

    # 履歴追加 / Add to history
    history_match = re.match(r'(?:履歴|history|clip)[:：]\s*(.+)', message, re.IGNORECASE)
    if history_match:
        return {'action': 'add_history', 'content': history_match.group(1).strip()}

    # スニペット追加 / Add snippet
    snippet_match = re.match(r'(?:スニペット|snippet|snip)[:：]\s*(.+)', message, re.IGNORECASE)
    if snippet_match:
        return parse_add_snippet(snippet_match.group(1))

    # 履歴検索 / Search history
    hsearch_match = re.match(r'(?:履歴検索|history search|hsearch)[:：]\s*(.+)', message, re.IGNORECASE)
    if hsearch_match:
        return {'action': 'search_history', 'keyword': hsearch_match.group(1)}

    # スニペット検索 / Search snippets
    ssearch_match = re.match(r'(?:スニペット検索|snippet search|ssearch|検索)[:：]\s*(.+)', message, re.IGNORECASE)
    if ssearch_match:
        return {'action': 'search_snippet', 'keyword': ssearch_match.group(1)}

    # 履歴一覧 / History list
    hlist_match = re.match(r'(?:履歴|history)(?:一覧|list)?', message, re.IGNORECASE)
    if hlist_match:
        return {'action': 'list_history'}

    # スニペット一覧 / Snippet list
    slist_match = re.match(r'(?:スニペット|snippet|snip)(?:一覧|list)?', message, re.IGNORECASE)
    if slist_match:
        return {'action': 'list_snippets'}

    # お気に入り一覧 / Favorites list
    if message.strip() in ['お気に入り', 'favorites', 'favs', 'fav']:
        return {'action': 'list_favorites'}

    # スニペット取得 / Get snippet
    get_match = re.match(r'(?:取得|get|show)[:：]\s*(?:スニペット|snippet|snip)?\s*(\d+)', message, re.IGNORECASE)
    if get_match:
        return {'action': 'get_snippet', 'snippet_id': int(get_match.group(1))}

    # 履歴取得 / Get history
    hget_match = re.match(r'(?:履歴取得|history get|hget)[:：]\s*(\d+)', message, re.IGNORECASE)
    if hget_match:
        return {'action': 'get_history', 'history_id': int(hget_match.group(1))}

    # お気に入り追加/削除 / Toggle favorite
    fav_match = re.match(r'(?:お気に入り|favorite|fav)[:：]\s*(\d+)', message, re.IGNORECASE)
    if fav_match:
        return {'action': 'toggle_favorite', 'snippet_id': int(fav_match.group(1))}

    # 削除 / Delete
    del_snippet_match = re.match(r'(?:削除|delete|del)[:：]\s*(?:スニペット|snippet)?\s*(\d+)', message, re.IGNORECASE)
    if del_snippet_match:
        return {'action': 'delete_snippet', 'snippet_id': int(del_snippet_match.group(1))}

    del_history_match = re.match(r'(?:履歴削除|history delete|hdel)[:：]\s*(\d+)', message, re.IGNORECASE)
    if del_history_match:
        return {'action': 'delete_history', 'history_id': int(del_history_match.group(1))}

    # カテゴリ一覧 / Categories
    if message.strip() in ['カテゴリ一覧', 'categories', 'cats']:
        return {'action': 'categories'}

    # タグ一覧 / Tags
    if message.strip() in ['タグ一覧', 'tags']:
        return {'action': 'tags'}

    # 統計 / Stats
    if message.strip() in ['統計', 'stats', 'クリップボード統計']:
        return {'action': 'stats'}

    # 古い履歴削除 / Clear old history
    clear_match = re.match(r'(?:古い履歴削除|clear old|clear)[:：]\s*(\d+)?', message, re.IGNORECASE)
    if clear_match:
        days = int(clear_match.group(1)) if clear_match.group(1) else 30
        return {'action': 'clear_old', 'days': days}

    return None

def parse_add_snippet(content):
    """スニペット追加を解析 / Parse snippet add"""
    result = {'action': 'add_snippet', 'title': None, 'content': None, 'description': None,
              'category': None, 'tags': None, 'is_favorite': False}

    # タイトル (最初の部分)
    title_match = re.match(r'^([^、,（\(【♪]+)', content)
    if title_match:
        result['title'] = title_match.group(1).strip()
        content = content[title_match.end():].strip()

    # コンテンツ
    content_match = re.search(r'(?:内容|content)[:：]\s*(.+)', content, re.IGNORECASE)
    if content_match:
        result['content'] = content_match.group(1).strip()
        # タイトルがまだ見つかっていない場合、内容より前をタイトルとする
        if not result['title']:
            result['title'] = content[:content_match.start()].strip()

    # 説明
    desc_match = re.search(r'(?:説明|description|desc)[:：]\s*(.+)', content, re.IGNORECASE)
    if desc_match:
        result['description'] = desc_match.group(1).strip()

    # カテゴリ
    cat_match = re.search(r'(?:カテゴリ|category|cat)[:：]\s*([^,、]+)', content, re.IGNORECASE)
    if cat_match:
        result['category'] = cat_match.group(1).strip()

    # タグ
    tag_match = re.search(r'(?:タグ|tag)[:：]\s*(.+)', content, re.IGNORECASE)
    if tag_match:
        tags_str = tag_match.group(1).strip()
        result['tags'] = [t.strip() for t in re.split(r'[,、\s]+', tags_str) if t.strip()]

    # お気に入り
    if 'お気に入り' in content or 'favorite' in content.lower() or 'fav' in content.lower():
        result['is_favorite'] = True

    return result

def handle_message(message):
    """メッセージを処理 / Handle message"""
    parsed = parse_message(message)

    if not parsed:
        return None

    action = parsed['action']

    if action == 'add_history':
        history_id = add_to_history(parsed['content'])
        return f"📋 履歴 #{history_id} に保存しました / Saved to history #{history_id}"

    elif action == 'add_snippet':
        if not parsed['title']:
            return "❌ タイトルを入力してください / Please enter a title"

        snippet_id = add_snippet(
            parsed['title'],
            parsed['content'],
            parsed['description'],
            parsed['category'],
            parsed['tags'],
            parsed['is_favorite']
        )

        response = f"✅ スニペット #{snippet_id} 追加完了 / Snippet added\n"
        response += f"タイトル / Title: {parsed['title']}\n"
        if parsed['category']:
            response += f"カテゴリ / Category: {parsed['category']}\n"
        if parsed['tags']:
            response += f"タグ / Tags: {', '.join(parsed['tags'])}\n"
        if parsed['is_favorite']:
            response += "⭐ お気に入りに追加 / Added to favorites"

        return response

    elif action == 'search_history':
        keyword = parsed['keyword']
        results = search_history(keyword)

        if not results:
            return f"🔍 「{keyword}」の履歴検索結果: 見つかりませんでした / No history found for \"{keyword}\""

        response = f"🔍 「{keyword}」の履歴検索結果 ({len(results)}件 / results):\n"
        for item in results:
            response += format_history_item(item)

        return response

    elif action == 'search_snippet':
        keyword = parsed['keyword']
        results = search_snippets(keyword)

        if not results:
            return f"🔍 「{keyword}」のスニペット検索結果: 見つかりませんでした / No snippets found for \"{keyword}\""

        response = f"🔍 「{keyword}」のスニペット検索結果 ({len(results)}件 / results):\n"
        for snippet in results:
            response += format_snippet(snippet)

        return response

    elif action == 'list_history':
        history = get_history()

        if not history:
            return "📋 クリップボード履歴がありません / No clipboard history"

        response = f"📋 クリップボード履歴 ({len(history)}件 / items):\n"
        for item in history:
            response += format_history_item(item)

        return response

    elif action == 'list_snippets':
        snippets = get_snippets()

        if not snippets:
            return "📝 スニペットがありません / No snippets"

        response = f"📝 スニペット一覧 ({len(snippets)}件 / items):\n"
        for snippet in snippets:
            response += format_snippet(snippet)

        return response

    elif action == 'list_favorites':
        snippets = get_snippets(favorites_only=True)

        if not snippets:
            return "⭐ お気に入りがありません / No favorites"

        response = f"⭐ お気に入り ({len(snippets)}件 / items):\n"
        for snippet in snippets:
            response += format_snippet(snippet)

        return response

    elif action == 'get_snippet':
        snippet = get_snippet(parsed['snippet_id'])

        if not snippet:
            return f"❌ スニペット #{parsed['snippet_id']} が見つかりません / Snippet #{parsed['snippet_id']} not found"

        response = f"📝 スニペット #{parsed['snippet_id']}:\n"
        response += f"タイトル / Title: {snippet[1]}\n"
        response += f"内容 / Content:\n```\n{snippet[2]}\n```"

        return response

    elif action == 'get_history':
        item = get_history_item(parsed['history_id'])

        if not item:
            return f"❌ 履歴 #{parsed['history_id']} が見つかりません / History #{parsed['history_id']} not found"

        response = f"📋 履歴 #{parsed['history_id']}:\n"
        response += f"```\n{item[1]}\n```"

        return response

    elif action == 'toggle_favorite':
        snippet = get_snippet(parsed['snippet_id'])

        if not snippet:
            return f"❌ スニペット #{parsed['snippet_id']} が見つかりません / Snippet #{parsed['snippet_id']} not found"

        new_fav = not snippet[6]
        update_snippet(parsed['snippet_id'], is_favorite=new_fav)
        status = "お気に入りに追加" if new_fav else "お気に入りから削除"
        status_en = "added to favorites" if new_fav else "removed from favorites"

        return f"⭐ スニペット #{parsed['snippet_id']} を{status}しました / Snippet #{parsed['snippet_id']} {status_en}"

    elif action == 'delete_snippet':
        delete_snippet(parsed['snippet_id'])
        return f"🗑️ スニペット #{parsed['snippet_id']} 削除完了 / Snippet deleted"

    elif action == 'delete_history':
        delete_history_item(parsed['history_id'])
        return f"🗑️ 履歴 #{parsed['history_id']} 削除完了 / History deleted"

    elif action == 'categories':
        categories = get_categories()

        if not categories:
            return "📁 カテゴリがありません / No categories"

        response = "📁 カテゴリ一覧 / Categories:\n"
        for cat in categories:
            response += f"  • {cat[1]}\n"

        return response

    elif action == 'tags':
        tags = get_tags()

        if not tags:
            return "🏷️ タグがありません / No tags"

        response = "🏷️ タグ一覧 / Tags:\n"
        for tag in tags:
            response += f"  • {tag[1]}\n"

        return response

    elif action == 'stats':
        stats = get_stats()

        response = "📊 クリップボード統計 / Clipboard Stats:\n"
        response += f"履歴数 / History: {stats['history_count']}件\n"
        response += f"スニペット数 / Snippets: {stats['snippet_count']}件\n"
        response += f"お気に入り数 / Favorites: {stats['favorite_count']}件"

        return response

    elif action == 'clear_old':
        deleted = clear_old_history(parsed['days'])
        return f"🧹 {parsed['days']}日以上前の履歴 {deleted}件を削除しました / Deleted {deleted} history items older than {parsed['days']} days"

    return None

def format_history_item(item):
    """履歴アイテムをフォーマット / Format history item"""
    id, preview, content_type, size, use_count, last_used = item

    response = f"\n📋 [{id}] "
    response += f"{preview}...\n"
    response += f"    👁️ {use_count}回 / {last_used[:10]}\n"

    return response

def format_snippet(snippet):
    """スニペットをフォーマット / Format snippet"""
    id, title, preview, description, category, is_favorite, use_count, updated_at = snippet

    response = f"\n📝 [{id}] "
    if is_favorite:
        response += "⭐ "
    response += f"{title}\n"
    if preview:
        response += f"    {preview}...\n"
    if category:
        response += f"    📁 {category}\n"
    response += f"    👁️ {use_count}回 / {updated_at[:10]}\n"

    return response

if __name__ == '__main__':
    # テスト / Test
    init_db()

    test_messages = [
        "履歴: サンプルテキストです",
        "スニペット: よく使う返信, 内容:ありがとうございます。確認いたします。",
        "スニペット検索: 返信",
        "スニペット一覧",
        "統計",
    ]

    for msg in test_messages:
        print(f"\n入力 / Input: {msg}")
        result = handle_message(msg)
        if result:
            print(result)
