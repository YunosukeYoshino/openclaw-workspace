#!/usr/bin/env python3
"""
日記エージェント #33 - Discord連携
"""

import re
from datetime import datetime
from db import *

def parse_message(message):
    """メッセージを解析"""
    # 日記追加
    journal_match = re.match(r'(?:日記|journal)[：:]\s*(.+)', message, re.IGNORECASE)
    if journal_match:
        return parse_add(journal_match.group(1))

    # 更新
    update_match = re.match(r'(?:更新|update)[：:]\s*(\d+)\s*(.+)', message, re.IGNORECASE)
    if update_match:
        return {'action': 'update', 'journal_id': int(update_match.group(1)), 'content': update_match.group(2)}

    # 削除
    delete_match = re.match(r'(?:削除|delete|remove)[：:]\s*(\d+)', message, re.IGNORECASE)
    if delete_match:
        return {'action': 'delete', 'journal_id': int(delete_match.group(1))}

    # 検索
    search_match = re.match(r'(?:検索|search)[：:]\s*(.+)', message, re.IGNORECASE)
    if search_match:
        return {'action': 'search', 'keyword': search_match.group(1)}

    # 一覧
    list_match = re.match(r'(?:(?:日記|journal)(?:一覧|list)|list|journals)', message, re.IGNORECASE)
    if list_match:
        return {'action': 'list'}

    # 今日
    if message.strip() in ['今日', 'today']:
        return {'action': 'today'}

    # 昨日
    if message.strip() in ['昨日', 'yesterday']:
        return {'action': 'yesterday'}

    # 今月
    if message.strip() in ['今月', 'this month', '今月一覧']:
        return {'action': 'this_month'}

    # 気分別
    mood_match = re.match(r'(?:気分|mood)[：:]\s*(.+)', message, re.IGNORECASE)
    if mood_match:
        return {'action': 'list_by_mood', 'mood': parse_mood(mood_match.group(1))}

    # 日付指定
    date_match = re.match(r'(\d{1,2})/(\d{1,2})', message)
    if date_match:
        month = int(date_match.group(1))
        day = int(date_match.group(2))
        year = datetime.now().year
        date_str = f"{year}-{month:02d}-{day:02d}"
        return {'action': 'by_date', 'date': date_str}

    # 統計
    if message.strip() in ['統計', 'stats', '日記統計']:
        return {'action': 'stats'}

    return None

def parse_add(content):
    """日記追加を解析"""
    result = {'action': 'add', 'date': None, 'title': None, 'content': None, 'mood': None, 'weather': None, 'tags': None}

    # 日付
    date_match = re.search(r'(?:日付|date)[：:]\s*([^、,]+)', content)
    if date_match:
        result['date'] = parse_date(date_match.group(1).strip())
    else:
        # デフォルトは今日
        result['date'] = datetime.now().strftime("%Y-%m-%d")

    # タイトル
    title_match = re.search(r'(?:タイトル|title)[：:]\s*([^、,]+)', content)
    if title_match:
        result['title'] = title_match.group(1).strip()

    # 気分
    mood_match = re.search(r'(?:気分|mood)[：:]\s*([^、,]+)', content)
    if mood_match:
        result['mood'] = parse_mood(mood_match.group(1).strip())

    # 天気
    weather_match = re.search(r'(?:天気|weather)[：:]\s*([^、,]+)', content)
    if weather_match:
        result['weather'] = weather_match.group(1).strip()

    # タグ
    tags_match = re.search(r'(?:タグ|tags)[：:]\s*(.+)', content)
    if tags_match:
        result['tags'] = tags_match.group(1).strip()

    # タイトルと内容の区切りを見つける
    # 最初の項目より前をタイトル、残りを内容とする
    for key in ['日付', 'date', 'タイトル', 'title', '気分', 'mood', '天気', 'weather', 'タグ', 'tags']:
        match = re.search(rf'{key}[：:]', content)
        if match:
            before = content[:match.start()].strip()
            if before and not result['title']:
                result['title'] = before
            break

    # 内容（タグ以降の部分）
    if tags_match:
        content_start = tags_match.end()
        result['content'] = content[content_start:].strip()
    elif result['title']:
        # タイトル以外を内容に
        temp_content = content.replace(result['title'], '', 1)
        for key in ['日付', 'date', 'タイトル', 'title', '気分', 'mood', '天気', 'weather', 'タグ', 'tags']:
            temp_content = re.sub(rf'{key}[：:][^、,]*', '', temp_content, flags=re.IGNORECASE)
        result['content'] = temp_content.strip()

    if not result['content'] and result['title']:
        # タイトルのみで内容がない場合
        result['content'] = None

    return result

def parse_update(content):
    """更新内容を解析"""
    result = {}

    # 日付
    date_match = re.search(r'(?:日付|date)[：:]\s*([^、,]+)', content)
    if date_match:
        result['date'] = parse_date(date_match.group(1).strip())

    # タイトル
    title_match = re.search(r'(?:タイトル|title)[：:]\s*([^、,]+)', content)
    if title_match:
        result['title'] = title_match.group(1).strip()

    # 気分
    mood_match = re.search(r'(?:気分|mood)[：:]\s*([^、,]+)', content)
    if mood_match:
        result['mood'] = parse_mood(mood_match.group(1).strip())

    # 天気
    weather_match = re.search(r'(?:天気|weather)[：:]\s*([^、,]+)', content)
    if weather_match:
        result['weather'] = weather_match.group(1).strip()

    # タグ
    tags_match = re.search(r'(?:タグ|tags)[：:]\s*(.+)', content)
    if tags_match:
        result['tags'] = tags_match.group(1).strip()

    # 内容
    content_match = re.search(r'(?:内容|content|body)[：:]\s*(.+)', content)
    if content_match:
        result['content'] = content_match.group(1).strip()

    return result

def parse_mood(mood_str):
    """気分を解析"""
    mood_map = {
        'happy': 'happy', 'happy': 'happy', '嬉しい': 'happy', '楽しい': 'happy', '良い': 'happy', 'いい': 'happy',
        'sad': 'sad', 'sad': 'sad', '悲しい': 'sad', 'つらい': 'sad', '辛い': 'sad',
        'neutral': 'neutral', 'neutral': 'neutral', '普通': 'neutral', 'ふつう': 'neutral',
        'excited': 'excited', 'excited': 'excited', '興奮': 'excited', 'わくわく': 'excited', 'やる気': 'excited',
        'calm': 'calm', 'calm': 'calm', '落ち着いてる': 'calm', 'リラックス': 'calm', '穏やか': 'calm',
        'angry': 'angry', 'angry': 'angry', '怒り': 'angry', '腹立つ': 'angry', 'イライラ': 'angry',
        'anxious': 'anxious', 'anxious': 'anxious', '不安': 'anxious', '心配': 'anxious',
        'tired': 'tired', 'tired': 'tired', '疲れた': 'tired', '疲労': 'tired'
    }

    mood_lower = mood_str.lower()
    for key, value in mood_map.items():
        if key in mood_lower:
            return value

    return mood_str

def parse_date(date_str):
    """日付を解析"""
    today = datetime.now()

    # 今日
    if '今日' in date_str:
        return today.strftime("%Y-%m-%d")

    # 昨日
    if '昨日' in date_str:
        from datetime import timedelta
        return (today - timedelta(days=1)).strftime("%Y-%m-%d")

    # 明日
    if '明日' in date_str:
        from datetime import timedelta
        return (today + timedelta(days=1)).strftime("%Y-%m-%d")

    # 日付形式
    date_match = re.match(r'(\d{4})-(\d{1,2})-(\d{1,2})', date_str)
    if date_match:
        return f"{date_match.group(1)}-{date_match.group(2).zfill(2)}-{date_match.group(3).zfill(2)}"

    date_match = re.match(r'(\d{1,2})/(\d{1,2})', date_str)
    if date_match:
        month = int(date_match.group(1))
        day = int(date_match.group(2))
        return datetime(today.year, month, day).strftime("%Y-%m-%d")

    return None

def handle_message(message):
    """メッセージを処理"""
    parsed = parse_message(message)

    if not parsed:
        return None

    action = parsed['action']

    if action == 'add':
        journal_id = add_journal(
            parsed['date'],
            parsed['title'],
            parsed['content'],
            parsed['mood'],
            parsed['weather'],
            parsed['tags']
        )

        response = f"📝 日記 #{journal_id} 追加完了\n"
        response += f"日付: {parsed['date']}\n"
        if parsed['title']:
            response += f"タイトル: {parsed['title']}\n"
        if parsed['content']:
            response += f"内容: {parsed['content'][:100]}...\n"
        if parsed['mood']:
            response += f"気分: {parsed['mood']}\n"
        if parsed['weather']:
            response += f"天気: {parsed['weather']}\n"
        if parsed['tags']:
            response += f"タグ: {parsed['tags']}"

        return response

    elif action == 'update':
        updates = parse_update(parsed['content'])

        if not updates:
            return "❌ 更新内容がありません"

        update_journal(parsed['journal_id'], **updates)

        journal = get_journal(parsed['journal_id'])
        if journal:
            response = f"✅ 日記 #{parsed['journal_id']} 更新完了\n"
            response += format_journal(journal)
            return response
        else:
            return f"❌ 日記 #{parsed['journal_id']} が見つかりません"

    elif action == 'delete':
        delete_journal(parsed['journal_id'])
        return f"🗑️ 日記 #{parsed['journal_id']} 削除完了"

    elif action == 'search':
        keyword = parsed['keyword']
        journals = search_journals(keyword)

        if not journals:
            return f"🔍 「{keyword}」の検索結果: 見つかりませんでした"

        response = f"🔍 「{keyword}」の検索結果 ({len(journals)}件):\n"
        for journal in journals:
            response += format_journal(journal)

        return response

    elif action == 'list':
        journals = list_journals()

        if not journals:
            return "📝 日記がありません"

        response = f"📝 日記一覧 ({len(journals)}件):\n"
        for journal in journals:
            response += format_journal(journal)

        return response

    elif action == 'today':
        today = datetime.now().strftime("%Y-%m-%d")
        journals = get_by_date(today)

        if not journals:
            return f"📝 今日の日記はまだありません"

        response = f"📝 今日の日記 ({len(journals)}件):\n"
        for journal in journals:
            response += format_journal(journal)

        return response

    elif action == 'yesterday':
        from datetime import timedelta
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        journals = get_by_date(yesterday)

        if not journals:
            return f"📝 昨日の日記はありません"

        response = f"📝 昨日の日記 ({len(journals)}件):\n"
        for journal in journals:
            response += format_journal(journal)

        return response

    elif action == 'this_month':
        current_month = datetime.now().strftime("%Y-%m")
        from datetime import timedelta
        first_day = f"{current_month}-01"
        next_month = datetime(datetime.now().year, datetime.now().month + 1, 1).strftime("%Y-%m-%d") if datetime.now().month < 12 else f"{datetime.now().year + 1}-01-01"

        journals = list_journals(date_from=first_day, date_to=next_month)

        if not journals:
            return f"📝 今月の日記はありません"

        response = f"📝 今月の日記 ({len(journals)}件):\n"
        for journal in journals:
            response += format_journal(journal)

        return response

    elif action == 'by_date':
        journals = get_by_date(parsed['date'])

        if not journals:
            return f"📝 {parsed['date']}の日記はありません"

        response = f"📝 {parsed['date']}の日記 ({len(journals)}件):\n"
        for journal in journals:
            response += format_journal(journal)

        return response

    elif action == 'list_by_mood':
        journals = list_journals(mood=parsed['mood'])

        if not journals:
            return f"📝 「{parsed['mood']}」の日記はありません"

        response = f"📝 {parsed['mood']}な日 ({len(journals)}件):\n"
        for journal in journals:
            response += format_journal(journal)

        return response

    elif action == 'stats':
        stats = get_stats()

        response = "📊 日記統計:\n"
        response += f"全日記数: {stats['total']}件\n"
        response += f"今日: {stats['today']}件\n"
        response += f"今月: {stats['this_month']}件"

        if stats['mood_distribution']:
            response += "\n\n気分分布:\n"
            for mood, count in stats['mood_distribution']:
                response += f"  {mood}: {count}件\n"

        return response

    return None

def format_journal(journal):
    """日記をフォーマット"""
    id, date, title, content, mood, weather, tags, created_at = journal

    response = f"\n📅 [{id}] {date}"
    if title:
        response += f" - {title}"
    response += "\n"

    if content:
        response += f"    {content[:200]}{'...' if len(content) > 200 else ''}\n"

    mood_icons = {
        'happy': '😊', 'sad': '😢', 'neutral': '😐',
        'excited': '🎉', 'calm': '😌', 'angry': '😠',
        'anxious': '😰', 'tired': '😴'
    }

    parts = []
    if mood and mood in mood_icons:
        parts.append(mood_icons[mood])
    if weather:
        parts.append(weather)
    if tags:
        parts.append(f"🏷️ {tags}")

    if parts:
        response += f"    {' '.join(parts)}\n"

    return response

if __name__ == '__main__':
    # テスト
    init_db()

    test_messages = [
        "日記: 今日はいい天気だった, 気分: happy, 天気: 晴れ",
        "日記: 仕事が大変だった, 気分: tired, タグ: 仕事",
        "今日",
        "今月",
        "気分: happy",
        "統計",
    ]

    for msg in test_messages:
        print(f"\n入力: {msg}")
        result = handle_message(msg)
        if result:
            print(result)
