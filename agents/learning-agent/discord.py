#!/usr/bin/env python3
"""
学習エージェント #37 - Discord連携
"""

import re
from datetime import datetime
from db import *

def parse_message(message):
    """メッセージを解析"""
    # 学習追加
    learn_match = re.match(r'(?:学習|learn|勉強|study)[：:]\s*(.+)', message, re.IGNORECASE)
    if learn_match:
        return parse_add_session(learn_match.group(1))

    # 目標追加
    goal_match = re.match(r'(?:目標|goal)[：:]\s*(.+)', message, re.IGNORECASE)
    if goal_match:
        return parse_add_goal(goal_match.group(1))

    # セッション更新
    update_session_match = re.match(r'(?:セッション更新|update session)[：:]\s*(\d+)\s*(.+)', message, re.IGNORECASE)
    if update_session_match:
        return {'action': 'update_session', 'session_id': int(update_session_match.group(1)), 'content': update_session_match.group(2)}

    # 目標更新
    update_goal_match = re.match(r'(?:目標更新|update goal)[：:]\s*(\d+)\s*(.+)', message, re.IGNORECASE)
    if update_goal_match:
        return {'action': 'update_goal', 'goal_id': int(update_goal_match.group(1)), 'content': update_goal_match.group(2)}

    # セッション削除
    delete_session_match = re.match(r'(?:セッション削除|delete session)[：:]\s*(\d+)', message, re.IGNORECASE)
    if delete_session_match:
        return {'action': 'delete_session', 'session_id': int(delete_session_match.group(1))}

    # 目標削除
    delete_goal_match = re.match(r'(?:目標削除|delete goal)[：:]\s*(\d+)', message, re.IGNORECASE)
    if delete_goal_match:
        return {'action': 'delete_goal', 'goal_id': int(delete_goal_match.group(1))}

    # 検索
    search_match = re.match(r'(?:検索|search)[：:]\s*(.+)', message, re.IGNORECASE)
    if search_match:
        return {'action': 'search', 'keyword': search_match.group(1)}

    # セッション一覧
    list_session_match = re.match(r'(?:(?:学習|learn|勉強|study)(?:一覧|list)|list|sessions)', message, re.IGNORECASE)
    if list_session_match:
        return {'action': 'list_sessions'}

    # 目標一覧
    list_goal_match = re.match(r'(?:(?:目標|goal)(?:一覧|list)|list|goals)', message, re.IGNORECASE)
    if list_goal_match:
        return {'action': 'list_goals'}

    # 今日
    if message.strip() in ['今日', 'today']:
        return {'action': 'today'}

    # 今月
    if message.strip() in ['今月', 'this month', '今月一覧']:
        return {'action': 'this_month'}

    # 科目別
    subject_match = re.match(r'(?:科目|subject)[：:]\s*(.+)', message, re.IGNORECASE)
    if subject_match:
        return {'action': 'list_by_subject', 'subject': subject_match.group(1)}

    # 統計
    if message.strip() in ['統計', 'stats', '学習統計']:
        return {'action': 'stats'}

    return None

def parse_add_session(content):
    """学習セッション追加を解析"""
    result = {'action': 'add_session', 'date': None, 'subject': None, 'topic': None,
              'duration': None, 'notes': None, 'progress': None, 'tags': None}

    # 日付
    date_match = re.search(r'(?:日付|date)[：:]\s*([^、,]+)', content)
    if date_match:
        result['date'] = parse_date(date_match.group(1).strip())
    else:
        # デフォルトは今日
        result['date'] = datetime.now().strftime("%Y-%m-%d")

    # 科目
    subject_match = re.search(r'(?:科目|subject)[：:]\s*([^、,]+)', content)
    if subject_match:
        result['subject'] = subject_match.group(1).strip()

    # トピック
    topic_match = re.search(r'(?:トピック|topic|内容)[：:]\s*(.+)', content)
    if topic_match:
        result['topic'] = topic_match.group(1).strip()

    # 時間
    duration_match = re.search(r'(?:時間|duration|時間h?|hour|min|分)[：:]?\s*(\d+)(\s*(時間|h|hour|分|min))?', content)
    if duration_match:
        result['duration'] = int(duration_match.group(1))
        if duration_match.group(2):
            unit = duration_match.group(2).strip().lower()
            if '時間' in unit or 'h' in unit or 'hour' in unit:
                result['duration'] *= 60  # 時間を分に変換

    # 進捗
    progress_match = re.search(r'(?:進捗|progress)[：:]?\s*(\d+)', content)
    if progress_match:
        progress = int(progress_match.group(1))
        if 0 <= progress <= 100:
            result['progress'] = progress

    # タグ
    tags_match = re.search(r'(?:タグ|tags)[：:]\s*(.+)', content)
    if tags_match:
        result['tags'] = tags_match.group(1).strip()

    # メモ
    notes_match = re.search(r'(?:メモ|備考|memo|note)[：:]\s*(.+)', content)
    if notes_match:
        result['notes'] = notes_match.group(1).strip()

    # 科目がない場合、最初の項目より前を科目とする
    if not result['subject']:
        for key in ['日付', 'date', '科目', 'subject', 'トピック', 'topic', '内容',
                    '時間', 'duration', '時間', 'h', 'hour', 'min', '分',
                    '進捗', 'progress', 'タグ', 'tags', 'メモ', '備考', 'memo', 'note']:
            match = re.search(rf'{key}[：:]', content)
            if match:
                result['subject'] = content[:match.start()].strip()
                break
        else:
            result['subject'] = content.strip()

    return result

def parse_add_goal(content):
    """目標追加を解析"""
    result = {'action': 'add_goal', 'title': None, 'subject': None, 'target_hours': None,
              'deadline': None, 'notes': None}

    # タイトル (最初の部分)
    title_match = re.match(r'^([^、,（\(【]+)', content)
    if title_match:
        result['title'] = title_match.group(1).strip()

    # 科目
    subject_match = re.search(r'(?:科目|subject)[：:]\s*([^、,]+)', content)
    if subject_match:
        result['subject'] = subject_match.group(1).strip()

    # 目標時間
    hours_match = re.search(r'(?:目標時間|target hours?|時間h?|hours?)[：:]?\s*(\d+)', content)
    if hours_match:
        result['target_hours'] = int(hours_match.group(1))

    # 期限
    deadline_match = re.search(r'(?:期限|deadline|due)[：:]\s*([^、,]+)', content)
    if deadline_match:
        result['deadline'] = parse_date(deadline_match.group(1).strip())

    # メモ
    notes_match = re.search(r'(?:メモ|備考|memo|note)[：:]\s*(.+)', content)
    if notes_match:
        result['notes'] = notes_match.group(1).strip()

    # タイトルがまだない場合、最初の項目より前をタイトルとする
    if not result['title']:
        for key in ['科目', 'subject', '目標時間', 'target hours', '時間', 'hours',
                    '期限', 'deadline', 'due', 'メモ', '備考', 'memo', 'note']:
            match = re.search(rf'{key}[：:]', content)
            if match:
                result['title'] = content[:match.start()].strip()
                break
        else:
            result['title'] = content.strip()

    return result

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

    if action == 'add_session':
        if not parsed['subject']:
            return "❌ 科目を入力してください"

        session_id = add_session(
            parsed['date'],
            parsed['subject'],
            parsed['topic'],
            parsed['duration'],
            parsed['notes'],
            parsed['progress'],
            parsed['tags']
        )

        response = f"📚 学習 #{session_id} 追加完了\n"
        response += f"科目: {parsed['subject']}\n"
        response += f"日付: {parsed['date']}\n"
        if parsed['topic']:
            response += f"トピック: {parsed['topic']}\n"
        if parsed['duration']:
            hours = parsed['duration'] // 60
            mins = parsed['duration'] % 60
            if hours > 0:
                response += f"時間: {hours}時間{mins}分\n"
            else:
                response += f"時間: {mins}分\n"
        if parsed['progress']:
            response += f"進捗: {parsed['progress']}%\n"
        if parsed['tags']:
            response += f"タグ: {parsed['tags']}\n"
        if parsed['notes']:
            response += f"メモ: {parsed['notes']}"

        return response

    elif action == 'add_goal':
        if not parsed['title']:
            return "❌ タイトルを入力してください"

        goal_id = add_goal(
            parsed['title'],
            parsed['subject'],
            parsed['target_hours'],
            parsed['deadline'],
            parsed['notes']
        )

        response = f"🎯 目標 #{goal_id} 追加完了\n"
        response += f"タイトル: {parsed['title']}\n"
        if parsed['subject']:
            response += f"科目: {parsed['subject']}\n"
        if parsed['target_hours']:
            response += f"目標時間: {parsed['target_hours']}時間\n"
        if parsed['deadline']:
            response += f"期限: {parsed['deadline']}\n"
        if parsed['notes']:
            response += f"メモ: {parsed['notes']}"

        return response

    elif action == 'update_session':
        # セッション更新（簡易実装）
        return f"✅ セッション #{parsed['session_id']} 更新機能は準備中です"

    elif action == 'update_goal':
        # 目標更新（簡易実装）
        return f"✅ 目標 #{parsed['goal_id']} 更新機能は準備中です"

    elif action == 'delete_session':
        delete_session(parsed['session_id'])
        return f"🗑️ セッション #{parsed['session_id']} 削除完了"

    elif action == 'delete_goal':
        delete_goal(parsed['goal_id'])
        return f"🗑️ 目標 #{parsed['goal_id']} 削除完了"

    elif action == 'search':
        keyword = parsed['keyword']
        sessions = search_sessions(keyword)

        if not sessions:
            return f"🔍 「{keyword}」の検索結果: 見つかりませんでした"

        response = f"🔍 「{keyword}」の検索結果 ({len(sessions)}件):\n"
        for session in sessions:
            response += format_session(session)

        return response

    elif action == 'list_sessions':
        sessions = list_sessions()

        if not sessions:
            return "📚 学習記録がありません"

        response = f"📚 学習記録 ({len(sessions)}件):\n"
        for session in sessions:
            response += format_session(session)

        return response

    elif action == 'list_goals':
        goals = list_goals()

        if not goals:
            return "🎯 目標がありません"

        response = f"🎯 目標一覧 ({len(goals)}件):\n"
        for goal in goals:
            response += format_goal(goal)

        return response

    elif action == 'today':
        today = datetime.now().strftime("%Y-%m-%d")
        sessions = get_by_date(today)

        if not sessions:
            return f"📚 今日の学習記録はまだありません"

        response = f"📚 今日の学習 ({len(sessions)}件):\n"
        for session in sessions:
            response += format_session(session)

        return response

    elif action == 'this_month':
        current_month = datetime.now().strftime("%Y-%m")
        from datetime import timedelta
        first_day = f"{current_month}-01"
        next_month = datetime(datetime.now().year, datetime.now().month + 1, 1).strftime("%Y-%m-%d") if datetime.now().month < 12 else f"{datetime.now().year + 1}-01-01"

        sessions = list_sessions(date_from=first_day, date_to=next_month)

        if not sessions:
            return f"📚 今月の学習記録はありません"

        response = f"📚 今月の学習 ({len(sessions)}件):\n"
        for session in sessions:
            response += format_session(session)

        return response

    elif action == 'list_by_subject':
        sessions = list_sessions(subject=parsed['subject'])

        if not sessions:
            return f"📚 「{parsed['subject']}」の学習記録はありません"

        response = f"📚 {parsed['subject']} ({len(sessions)}件):\n"
        for session in sessions:
            response += format_session(session)

        return response

    elif action == 'stats':
        stats = get_stats()

        response = "📊 学習統計:\n"
        response += f"全セッション数: {stats['total_sessions']}件\n"
        response += f"全学習時間: {stats['total_hours']}分"
        if stats['total_hours'] > 60:
            response += f" ({stats['total_hours'] // 60}時間{stats['total_hours'] % 60}分)"
        response += f"\n今日: {stats['today_hours']}分\n"
        response += f"今月: {stats['month_hours']}分\n"
        response += f"科目数: {stats['subjects']}種類\n"
        response += f"目標数: {stats['goals']}個\n"
        response += f"進行中: {stats['ongoing_goals']}個"

        return response

    return None

def format_session(session):
    """学習セッションをフォーマット"""
    id, date, subject, topic, duration, notes, progress, tags, created_at = session

    response = f"\n📅 [{id}] {date} - {subject}\n"

    parts = []
    if topic:
        parts.append(f"📝 {topic[:50]}{'...' if len(topic) > 50 else ''}")
    if duration:
        hours = duration // 60
        mins = duration % 60
        if hours > 0:
            parts.append(f"⏱️ {hours}時間{mins}分")
        else:
            parts.append(f"⏱️ {mins}分")
    if progress:
        parts.append(f"📈 {progress}%")

    if parts:
        response += f"    {' '.join(parts)}\n"

    if tags:
        response += f"    🏷️ {tags}\n"

    return response

def format_goal(goal):
    """目標をフォーマット"""
    id, title, subject, target_hours, current_hours, deadline, status, notes, created_at = goal

    status_icons = {'ongoing': '🎯', 'completed': '✅', 'cancelled': '❌'}
    status_icon = status_icons.get(status, '❓')

    response = f"\n{status_icon} [{id}] {title}\n"

    parts = []
    if subject:
        parts.append(f"📚 {subject}")
    if target_hours:
        progress_pct = int((current_hours / target_hours) * 100) if target_hours > 0 else 0
        parts.append(f"{current_hours}/{target_hours}時間 ({progress_pct}%)")
    if deadline:
        parts.append(f"📅 {deadline}")

    if parts:
        response += f"    {' '.join(parts)}\n"

    return response

if __name__ == '__main__':
    # テスト
    init_db()

    test_messages = [
        "学習: 数学, 科目: 数学, 時間: 60分, トピック: 微分積分",
        "目標: TOEIC 800点, 科目: 英語, 目標時間: 100",
        "今日",
        "目標",
        "統計",
    ]

    for msg in test_messages:
        print(f"\n入力: {msg}")
        result = handle_message(msg)
        if result:
            print(result)
