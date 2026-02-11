#!/usr/bin/env python3
"""
パスワード管理エージェント - Discord連携
Password Management Agent - Discord Integration
"""

import re
from datetime import datetime
from db import *

# マスターパスワード（実際の使用では安全な場所から読み込む）
MASTER_PASSWORD = "default_master_password_change_me"

def init():
    """初期化"""
    init_db(MASTER_PASSWORD)

def parse_message(message):
    """メッセージを解析 / Parse message"""

    # パスワード追加 / Add password
    add_match = re.match(r'(?:パスワード|password|pwd)[:：]\s*(.+)', message, re.IGNORECASE)
    if add_match:
        return parse_add(add_match.group(1))

    # パスワード生成 / Generate password
    gen_match = re.match(r'(?:生成|generate|gen)[:：]\s*(\d+)?', message, re.IGNORECASE)
    if gen_match:
        length = int(gen_match.group(1)) if gen_match.group(1) else 16
        return {'action': 'generate', 'length': length}

    # パスワード取得 / Get password
    get_match = re.match(r'(?:取得|get|show|view)[:：]\s*(\d+)', message, re.IGNORECASE)
    if get_match:
        return {'action': 'get', 'password_id': int(get_match.group(1))}

    # 検索 / Search
    search_match = re.match(r'(?:検索|search)[:：]\s*(.+)', message, re.IGNORECASE)
    if search_match:
        return {'action': 'search', 'keyword': search_match.group(1)}

    # 一覧 / List
    list_match = re.match(r'(?:パスワード|password|pwd)(?:一覧|list)?', message, re.IGNORECASE)
    if list_match:
        return {'action': 'list'}

    # 更新 / Update
    update_match = re.match(r'(?:更新|update)[:：]\s*(\d+)\s*,\s*(.+)', message, re.IGNORECASE)
    if update_match:
        return parse_update(int(update_match.group(1)), update_match.group(2))

    # 削除 / Delete
    delete_match = re.match(r'(?:削除|delete|del)[:：]\s*(\d+)', message, re.IGNORECASE)
    if delete_match:
        return {'action': 'delete', 'password_id': int(delete_match.group(1))}

    # 強度チェック / Password strength check
    strength_match = re.match(r'(?:強度|strength|check)[:：]\s*(.+)', message, re.IGNORECASE)
    if strength_match:
        return {'action': 'strength', 'password': strength_match.group(1)}

    # 統計 / Stats
    if message.strip() in ['統計', 'stats', 'パスワード統計']:
        return {'action': 'stats'}

    return None

def parse_add(content):
    """パスワード追加を解析 / Parse password add"""
    result = {'action': 'add', 'site_name': None, 'username': None, 'password': None,
              'site_url': None, 'category': None, 'notes': None, 'tags': None}

    # サイト名
    site_match = re.search(r'(?:サイト|site)[:：]\s*([^,、]+)', content, re.IGNORECASE)
    if site_match:
        result['site_name'] = site_match.group(1).strip()

    # ユーザー名
    user_match = re.search(r'(?:ユーザー|username|user|user[:：]\s*(.+)', content, re.IGNORECASE)
    if user_match:
        result['username'] = user_match.group(1).strip()

    # パスワード
    pass_match = re.search(r'(?:パスワード|password|pwd)[:：]\s*(.+)', content, re.IGNORECASE)
    if pass_match:
        result['password'] = pass_match.group(1).strip()

    # URL
    url_match = re.search(r'url[:：]\s*(https?://[^\s,、]+)', content, re.IGNORECASE)
    if url_match:
        result['site_url'] = url_match.group(1).strip()

    # カテゴリ
    cat_match = re.search(r'(?:カテゴリ|category|cat)[:：]\s*([^,、]+)', content, re.IGNORECASE)
    if cat_match:
        result['category'] = cat_match.group(1).strip()

    # メモ
    note_match = re.search(r'(?:メモ|notes?|note)[:：]\s*(.+)', content, re.IGNORECASE)
    if note_match:
        result['notes'] = note_match.group(1).strip()

    # タグ
    tag_match = re.search(r'(?:タグ|tag)[:：]\s*(.+)', content, re.IGNORECASE)
    if tag_match:
        tags_str = tag_match.group(1).strip()
        result['tags'] = [t.strip() for t in re.split(r'[,、\s]+', tags_str) if t.strip()]

    return result

def parse_update(password_id, content):
    """更新を解析 / Parse update"""
    result = {'action': 'update', 'password_id': password_id, 'site_name': None, 'username': None,
              'password': None, 'site_url': None, 'category': None, 'notes': None}

    site_match = re.search(r'(?:サイト|site)[:：]\s*([^,、]+)', content, re.IGNORECASE)
    if site_match:
        result['site_name'] = site_match.group(1).strip()

    user_match = re.search(r'(?:ユーザー|username|user)[:：]\s*(.+)', content, re.IGNORECASE)
    if user_match:
        result['username'] = user_match.group(1).strip()

    pass_match = re.search(r'(?:パスワード|password|pwd)[:：]\s*(.+)', content, re.IGNORECASE)
    if pass_match:
        result['password'] = pass_match.group(1).strip()

    url_match = re.search(r'url[:：]\s*(https?://[^\s,、]+)', content, re.IGNORECASE)
    if url_match:
        result['site_url'] = url_match.group(1).strip()

    cat_match = re.search(r'(?:カテゴリ|category|cat)[:：]\s*([^,、]+)', content, re.IGNORECASE)
    if cat_match:
        result['category'] = cat_match.group(1).strip()

    note_match = re.search(r'(?:メモ|notes?|note)[:：]\s*(.+)', content, re.IGNORECASE)
    if note_match:
        result['notes'] = note_match.group(1).strip()

    return result

def handle_message(message):
    """メッセージを処理 / Handle message"""
    parsed = parse_message(message)

    if not parsed:
        return None

    action = parsed['action']

    if action == 'add':
        if not parsed['site_name']:
            return "❌ サイト名を入力してください / Please enter a site name"
        if not parsed['username']:
            return "❌ ユーザー名を入力してください / Please enter a username"
        if not parsed['password']:
            return "❌ パスワードを入力してください / Please enter a password"

        password_id = add_password(
            parsed['site_name'],
            parsed['username'],
            parsed['password'],
            parsed['site_url'],
            parsed['category'],
            parsed['notes'],
            parsed['tags']
        )

        response = f"✅ パスワード #{password_id} 保存完了 / Password saved\n"
        response += f"サイト / Site: {parsed['site_name']}\n"
        response += f"ユーザー / Username: {parsed['username']}\n"
        if parsed['category']:
            response += f"カテゴリ / Category: {parsed['category']}\n"
        if parsed['tags']:
            response += f"タグ / Tags: {', '.join(parsed['tags'])}"

        return response

    elif action == 'generate':
        length = parsed['length']
        password = generate_password(length)

        response = f"🔐 生成されたパスワード ({length}文字 / characters):\n"
        response += f"```\n{password}\n```\n"

        strength = check_password_strength(password)
        response += f"強度 / Strength: {strength['level']} (Score: {strength['score']}/7)"

        return response

    elif action == 'get':
        result = get_password(parsed['password_id'])

        if not result:
            return f"❌ パスワード #{parsed['password_id']} が見つかりません / Password #{parsed['password_id']} not found"

        password_id, site_name, site_url, username, password, last_used = result

        response = f"🔐 パスワード #{password_id}:\n"
        response += f"サイト / Site: {site_name}\n"
        if site_url:
            response += f"URL: {site_url}\n"
        response += f"ユーザー / Username: {username}\n"
        response += f"パスワード / Password: ||{password}||\n"
        response += f"最終使用 / Last used: {last_used}"

        return response

    elif action == 'search':
        keyword = parsed['keyword']
        passwords = search_passwords(keyword)

        if not passwords:
            return f"🔍 「{keyword}」の検索結果: 見つかりませんでした / No results found for \"{keyword}\""

        response = f"🔍 「{keyword}」の検索結果 ({len(passwords)}件 / results):\n"
        for pwd in passwords:
            response += format_password(pwd)

        return response

    elif action == 'list':
        passwords = list_passwords()

        if not passwords:
            return "📋 パスワードがありません / No passwords found"

        response = f"📋 パスワード一覧 ({len(passwords)}件 / items):\n"
        for pwd in passwords:
            response += format_password(pwd)

        return response

    elif action == 'update':
        update_password(
            parsed['password_id'],
            parsed['site_name'],
            parsed['username'],
            parsed['password'],
            parsed['site_url'],
            parsed['category'],
            parsed['notes']
        )
        return f"✏️ パスワード #{parsed['password_id']} 更新完了 / Password updated"

    elif action == 'delete':
        delete_password(parsed['password_id'])
        return f"🗑️ パスワード #{parsed['password_id']} 削除完了 / Password deleted"

    elif action == 'strength':
        strength = check_password_strength(parsed['password'])

        response = f"🔍 パスワード強度チェック / Password strength check:\n"
        response += f"スコア / Score: {strength['score']}/7\n"
        response += f"レベル / Level: {strength['level']}\n"

        if strength['feedback']:
            response += f"フィードバック / Feedback:\n"
            for fb in strength['feedback']:
                response += f"  • {fb}\n"

        return response

    elif action == 'stats':
        stats = get_stats()

        response = "📊 パスワード統計 / Password Stats:\n"
        response += f"全パスワード数 / Total: {stats['total_passwords']}件\n"
        response += f"最近追加 / Recent: {stats['recent_additions']}件 (7日以内 / within 7 days)"

        if stats['by_category']:
            top_cat = list(stats['by_category'].items())[0]
            response += f"\nトップカテゴリ / Top category: {top_cat[0]} ({top_cat[1]}件)"

        if stats['by_tag']:
            top_tag = list(stats['by_tag'].items())[0]
            response += f"\nトップタグ / Top tag: {top_tag[0]} ({top_tag[1]}件)"

        return response

    return None

def format_password(pwd):
    """パスワードをフォーマット / Format password"""
    id, site_name, site_url, username, category, created_at, updated_at = pwd

    response = f"\n🔐 [{id}] {site_name}\n"
    if site_url:
        response += f"    🔗 {site_url}\n"
    response += f"    👤 {username}\n"
    if category:
        response += f"    📁 {category}\n"
    response += f"    📅 作成 / Created: {created_at[:10]}\n"

    return response

if __name__ == '__main__':
    # テスト / Test
    init()

    test_messages = [
        "パスワード: サイト:example.com, ユーザー:admin, パスワード:pass123",
        "生成: 20",
        "パスワード一覧",
        "統計",
    ]

    for msg in test_messages:
        print(f"\n入力 / Input: {msg}")
        result = handle_message(msg)
        if result:
            print(result)
