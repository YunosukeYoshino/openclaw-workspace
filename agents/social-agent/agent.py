#!/usr/bin/env python3
"""
Social Media Agent - Natural Language Processing
Supports Japanese and English
"""

import re
from datetime import datetime
from db import *

# Platform keywords
PLATFORMS = ['twitter', 'x', 'facebook', 'instagram', 'linkedin', 'mastodon']

def detect_language(message):
    """言語を検出 / Detect language"""
    jp_keywords = ['投稿', '通知', 'アカウント', '予定', 'スケジュール']
    en_keywords = ['post', 'notification', 'account', 'schedule', 'social']

    message_lower = message.lower()
    jp_score = sum(1 for kw in jp_keywords if kw in message)
    en_score = sum(1 for kw in en_keywords if kw in message_lower)
    return 'jp' if jp_score >= en_score else 'en'

def parse_message(message, lang=None):
    """メッセージを解析 / Parse message"""
    lang = lang or detect_language(message)
    message_lower = message.lower()

    # Add post (投稿追加)
    if lang == 'jp':
        post_match = re.match(r'(?:投稿|post)[:：]\s*(.+)', message, re.IGNORECASE)
    else:
        post_match = re.match(r'(?:post|add post)[:：]\s*(.+)', message, re.IGNORECASE)

    if post_match:
        return parse_add_post(post_match.group(1), lang)

    # Schedule post (予定投稿)
    if lang == 'jp':
        schedule_match = re.match(r'(?:予定投稿|scheduled|schedule)[:：]\s*(.+)', message, re.IGNORECASE)
    else:
        schedule_match = re.match(r'(?:scheduled|schedule)[:：]\s*(.+)', message, re.IGNORECASE)

    if schedule_match:
        return parse_schedule_post(schedule_match.group(1), lang)

    # List posts (投稿一覧)
    for kw in ['投稿', 'posts', 'list posts', 'my posts']:
        if message.strip() in [kw, f'{kw} 一覧']:
            return {'action': 'list_posts'}

    # Add notification (通知追加)
    if lang == 'jp':
        notif_match = re.match(r'(?:通知追加|add notification)[:：]\s*(.+)', message, re.IGNORECASE)
    else:
        notif_match = re.match(r'(?:add notification|notification)[:：]\s*(.+)', message, re.IGNORECASE)

    if notif_match:
        return parse_add_notification(notif_match.group(1), lang)

    # List notifications (通知一覧)
    for kw in ['通知', 'notifications', 'list notifications']:
        if message.strip() in [kw, f'{kw} 一覧']:
            return {'action': 'list_notifications'}

    # Unread notifications (未読通知)
    for kw in ['未読通知', 'unread', 'unread notifications']:
        if message.strip() in [kw, f'{kw} 一覧']:
            return {'action': 'list_unread'}

    # Mark as read (既読にする)
    if lang == 'jp':
        read_match = re.match(r'(?:既読|mark read)[:：]\s*(\d+)', message)
    else:
        read_match = re.match(r'(?:mark read|read)[:：]\s*(\d+)', message, re.IGNORECASE)

    if read_match:
        return {'action': 'mark_read', 'notification_id': int(read_match.group(1))}

    # Add account (アカウント追加)
    if lang == 'jp':
        account_match = re.match(r'(?:アカウント追加|add account)[:：]\s*(.+)', message)
    else:
        account_match = re.match(r'(?:add account|account)[:：]\s*(.+)', message, re.IGNORECASE)

    if account_match:
        return parse_add_account(account_match.group(1), lang)

    # List accounts (アカウント一覧)
    for kw in ['アカウント', 'accounts', 'list accounts', 'connected accounts']:
        if message.strip() in [kw, f'{kw} 一覧']:
            return {'action': 'list_accounts'}

    # Post (mark as posted)
    if lang == 'jp':
        post_done_match = re.match(r'(?:投稿済|posted)[:：]\s*(\d+)', message)
    else:
        post_done_match = re.match(r'(?:posted|post done)[:：]\s*(\d+)', message, re.IGNORECASE)

    if post_done_match:
        return {'action': 'post_done', 'post_id': int(post_done_match.group(1))}

    return None

def parse_add_post(content, lang):
    """投稿追加を解析 / Parse add post"""
    result = {'action': 'add_post', 'platform': None, 'content': None}

    # Detect platform
    for platform in PLATFORMS:
        if platform in content.lower():
            result['platform'] = platform
            break

    if lang == 'jp':
        # Extract platform explicitly
        platform_match = re.search(r'(?:プラットフォーム|platform)[:：]\s*(\w+)', content, re.IGNORECASE)
        if platform_match:
            result['platform'] = platform_match.group(1).lower()
        else:
            # Default to twitter if no platform specified
            if not result['platform']:
                result['platform'] = 'twitter'

        # Content (remove platform keyword)
        for p in ['twitter', 'x', 'facebook', 'instagram', 'linkedin', 'mastodon']:
            content = content.lower().replace(p, '', 1)

        result['content'] = content.strip()
    else:
        platform_match = re.search(r'(?:platform)[:：]\s*(\w+)', content, re.IGNORECASE)
        if platform_match:
            result['platform'] = platform_match.group(1).lower()
        else:
            if not result['platform']:
                result['platform'] = 'twitter'

        for p in ['twitter', 'x', 'facebook', 'instagram', 'linkedin', 'mastodon']:
            content = content.lower().replace(p, '', 1)

        result['content'] = content.strip()

    return result

def parse_schedule_post(content, lang):
    """予定投稿を解析 / Parse schedule post"""
    result = {'action': 'schedule_post', 'platform': None, 'content': None, 'scheduled_time': None}

    # Platform
    for platform in PLATFORMS:
        if platform in content.lower():
            result['platform'] = platform
            break

    if not result['platform']:
        result['platform'] = 'twitter'

    # Scheduled time
    if lang == 'jp':
        time_match = re.search(r'(?:日時|時間|時刻)[:：]\s*(.+)', content)
    else:
        time_match = re.search(r'(?:time|scheduled|when)[:：]\s*(.+)', content, re.IGNORECASE)

    if time_match:
        result['scheduled_time'] = parse_datetime(time_match.group(1).strip(), lang)

    # Content
    if lang == 'jp':
        for kw in ['日時:', '時間:', '時刻:', 'twitter', 'x', 'facebook', 'instagram', 'linkedin', 'mastodon']:
            content = content.lower().replace(kw, '', 1)
    else:
        for kw in ['time:', 'scheduled:', 'when:', 'twitter', 'x', 'facebook', 'instagram', 'linkedin', 'mastodon']:
            content = content.lower().replace(kw, '', 1)

    result['content'] = content.strip()

    return result

def parse_add_notification(content, lang):
    """通知追加を解析 / Parse add notification"""
    result = {'action': 'add_notification', 'platform': None, 'content': None, 'type': 'mention'}

    # Platform
    for platform in PLATFORMS:
        if platform in content.lower():
            result['platform'] = platform
            break

    if not result['platform']:
        result['platform'] = 'twitter'

    # Content
    result['content'] = content.strip()

    return result

def parse_add_account(content, lang):
    """アカウント追加を解析 / Parse add account"""
    result = {'action': 'add_account', 'platform': None, 'account_name': None, 'account_id': None}

    # Platform
    for platform in PLATFORMS:
        if platform in content.lower():
            result['platform'] = platform
            break

    if lang == 'jp':
        # Extract platform explicitly
        platform_match = re.search(r'(?:プラットフォーム|platform)[:：]\s*(\w+)', content, re.IGNORECASE)
        if platform_match:
            result['platform'] = platform_match.group(1).lower()

        # Account name
        name_match = re.search(r'(?:アカウント名|名前|name)[:：]\s*(.+)', content, re.IGNORECASE)
        if name_match:
            result['account_name'] = name_match.group(1).strip()
    else:
        platform_match = re.search(r'(?:platform)[:：]\s*(\w+)', content, re.IGNORECASE)
        if platform_match:
            result['platform'] = platform_match.group(1).lower()

        name_match = re.search(r'(?:account name|name)[:：]\s*(.+)', content, re.IGNORECASE)
        if name_match:
            result['account_name'] = name_match.group(1).strip()

    return result

def parse_datetime(dt_str, lang):
    """日時を解析 / Parse datetime"""
    now = datetime.now()

    if lang == 'jp':
        # 今日/明日/明後日
        if '今日' in dt_str:
            time_match = re.search(r'(\d{1,2}):(\d{2})', dt_str)
            if time_match:
                return datetime(now.year, now.month, now.day, int(time_match.group(1)), int(time_match.group(2))).strftime("%Y-%m-%d %H:%M")
            return now.strftime("%Y-%m-%d 12:00")
        elif '明日' in dt_str:
            time_match = re.search(r'(\d{1,2}):(\d{2})', dt_str)
            if time_match:
                return (now.replace(hour=int(time_match.group(1)), minute=int(time_match.group(2))) + datetime.timedelta(days=1)).strftime("%Y-%m-%d %H:%M")
            return (now + datetime.timedelta(days=1)).strftime("%Y-%m-%d 12:00")
        else:
            # ISO format
            try:
                dt = datetime.strptime(dt_str.strip()[:16], "%Y-%m-%d %H:%M")
                return dt.strftime("%Y-%m-%d %H:%M")
            except:
                return None
    else:
        import datetime as dt_module
        if 'today' in dt_str.lower():
            time_match = re.search(r'(\d{1,2}):(\d{2})', dt_str)
            if time_match:
                return datetime(now.year, now.month, now.day, int(time_match.group(1)), int(time_match.group(2))).strftime("%Y-%m-%d %H:%M")
            return now.strftime("%Y-%m-%d 12:00")
        elif 'tomorrow' in dt_str.lower():
            time_match = re.search(r'(\d{1,2}):(\d{2})', dt_str)
            if time_match:
                return (now + dt_module.timedelta(days=1)).replace(hour=int(time_match.group(1)), minute=int(time_match.group(2))).strftime("%Y-%m-%d %H:%M")
            return (now + dt_module.timedelta(days=1)).strftime("%Y-%m-%d 12:00")
        else:
            try:
                dt = datetime.strptime(dt_str.strip()[:16], "%Y-%m-%d %H:%M")
                return dt.strftime("%Y-%m-%d %H:%M")
            except:
                return None

def handle_message(message):
    """メッセージを処理 / Handle message"""
    lang = detect_language(message)
    parsed = parse_message(message, lang)

    if not parsed:
        return None

    action = parsed['action']

    if action == 'add_post':
        if not parsed['content']:
            return lang_response(lang, '❌ 投稿内容を入力してください / Please enter post content')

        post_id = add_post(parsed['platform'], parsed['content'])

        response = lang_response(lang, f'📝 投稿 #{post_id} 追加完了 / Post #{post_id} added\n')
        response += lang_response(lang, f'プラットフォーム: {parsed["platform"]} / Platform: {parsed["platform"]}\n')
        response += lang_response(lang, f'内容: {parsed["content"][:50]}...' if len(parsed["content"]) > 50 else f'内容: {parsed["content"]}')
        return response

    elif action == 'schedule_post':
        if not parsed['content']:
            return lang_response(lang, '❌ 投稿内容を入力してください / Please enter post content')

        post_id = add_post(parsed['platform'], parsed['content'], parsed['scheduled_time'])

        response = lang_response(lang, f'📅 予定投稿 #{post_id} 追加完了 / Scheduled post #{post_id} added\n')
        response += lang_response(lang, f'プラットフォーム: {parsed["platform"]} / Platform: {parsed["platform"]}\n')
        if parsed['scheduled_time']:
            response += lang_response(lang, f'予定日時: {parsed["scheduled_time"]} / Scheduled: {parsed["scheduled_time"]}\n')
        response += lang_response(lang, f'内容: {parsed["content"][:50]}...' if len(parsed["content"]) > 50 else f'内容: {parsed["content"]}')
        return response

    elif action == 'list_posts':
        posts = list_posts()

        if not posts:
            return lang_response(lang, '📝 投稿がありません / No posts found')

        response = lang_response(lang, f'📝 投稿一覧 ({len(posts)}件) / Posts ({len(posts)} items):\n')
        for post in posts:
            response += format_post(post, lang)

        return response

    elif action == 'add_notification':
        if not parsed['content']:
            return lang_response(lang, '❌ 通知内容を入力してください / Please enter notification content')

        notif_id = add_notification(parsed['platform'], parsed['content'], parsed['type'])

        response = lang_response(lang, f'🔔 通知 #{notif_id} 追加完了 / Notification #{notif_id} added\n')
        response += lang_response(lang, f'プラットフォーム: {parsed["platform"]}')
        return response

    elif action == 'list_notifications':
        notifications = list_notifications()

        if not notifications:
            return lang_response(lang, '🔔 通知がありません / No notifications found')

        response = lang_response(lang, f'🔔 通知一覧 ({len(notifications)}件) / Notifications ({len(notifications)} items):\n')
        for notif in notifications:
            response += format_notification(notif, lang)

        return response

    elif action == 'list_unread':
        notifications = list_notifications(is_read=False)

        if not notifications:
            return lang_response(lang, '🔔 未読通知はありません / No unread notifications')

        response = lang_response(lang, f'🔔 未読通知 ({len(notifications)}件) / Unread notifications ({len(notifications)} items):\n')
        for notif in notifications:
            response += format_notification(notif, lang)

        return response

    elif action == 'mark_read':
        mark_notification_read(parsed['notification_id'])
        return lang_response(lang, f'✅ 通知 #{parsed["notification_id"]} を既読にしました / Marked notification #{parsed["notification_id"]} as read')

    elif action == 'post_done':
        update_post_status(parsed['post_id'], 'posted')
        return lang_response(lang, f'✅ 投稿 #{parsed["post_id"]} を投稿済みにしました / Marked post #{parsed["post_id"]} as posted')

    elif action == 'add_account':
        if not parsed['account_name']:
            return lang_response(lang, '❌ アカウント名を入力してください / Please enter account name')

        account_id = add_account(parsed['platform'], parsed['account_name'], parsed['account_id'])

        response = lang_response(lang, f'👤 アカウント #{account_id} 追加完了 / Account #{account_id} added\n')
        response += lang_response(lang, f'プラットフォーム: {parsed["platform"]}\n')
        response += lang_response(lang, f'アカウント名: {parsed["account_name"]} / Account name: {parsed["account_name"]}')
        return response

    elif action == 'list_accounts':
        accounts = list_accounts()

        if not accounts:
            return lang_response(lang, '👤 アカウントがありません / No accounts found')

        response = lang_response(lang, f'👤 アカウント一覧 ({len(accounts)}件) / Accounts ({len(accounts)} items):\n')
        for account in accounts:
            response += format_account(account, lang)

        return response

    return None

def format_post(post, lang):
    """投稿をフォーマット / Format post"""
    id, platform, content, status, scheduled_time, posted_time, created_at = post

    if lang == 'jp':
        response = f'\n[{id}] {platform}\n'
        response += f'    内容: {content[:50]}...\n' if len(content) > 50 else f'    内容: {content}\n'
        response += f'    状態: {status}\n'
        if scheduled_time:
            response += f'    予定日時: {scheduled_time}\n'
        if posted_time:
            response += f'    投稿日時: {posted_time}\n'
        response += f'    作成: {created_at}'
    else:
        response = f'\n[{id}] {platform}\n'
        response += f'    Content: {content[:50]}...\n' if len(content) > 50 else f'    Content: {content}\n'
        response += f'    Status: {status}\n'
        if scheduled_time:
            response += f'    Scheduled: {scheduled_time}\n'
        if posted_time:
            response += f'    Posted: {posted_time}\n'
        response += f'    Created: {created_at}'

    return response

def format_notification(notification, lang):
    """通知をフォーマット / Format notification"""
    id, platform, content, notif_type, is_read, timestamp = notification

    read_mark = '🔴' if not is_read else '⚪'

    if lang == 'jp':
        response = f'\n[{id}] {read_mark} {platform}\n'
        response += f'    内容: {content[:50]}...\n' if len(content) > 50 else f'    内容: {content}\n'
        response += f'    タイプ: {notif_type}\n'
        response += f'    時間: {timestamp}'
    else:
        response = f'\n[{id}] {read_mark} {platform}\n'
        response += f'    Content: {content[:50]}...\n' if len(content) > 50 else f'    Content: {content}\n'
        response += f'    Type: {notif_type}\n'
        response += f'    Time: {timestamp}'

    return response

def format_account(account, lang):
    """アカウントをフォーマット / Format account"""
    id, platform, account_name, account_id, is_active, created_at = account

    status = '有効' if is_active else '無効' if lang == 'jp' else 'active' if is_active else 'inactive'

    if lang == 'jp':
        response = f'\n[{id}] {platform}\n'
        response += f'    アカウント名: {account_name}\n'
        response += f'    状態: {status}\n'
        response += f'    追加日: {created_at}'
    else:
        response = f'\n[{id}] {platform}\n'
        response += f'    Account name: {account_name}\n'
        response += f'    Status: {status}\n'
        response += f'    Added: {created_at}'

    return response

def lang_response(lang, text):
    return text

if __name__ == '__main__':
    init_db()

    test_messages = [
        "post: Hello world!",
        "schedule: This is a scheduled post, time: tomorrow 10:00",
        "posts",
        "unread",
        "add notification @mention me",
        "accounts",
    ]

    for msg in test_messages:
        print(f"\n入力 / Input: {msg}")
        result = handle_message(msg)
        if result:
            print(result)
