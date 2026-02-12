#!/usr/bin/env python3
"""
学習記録エージェント #15 - Discord連携
"""

import re
from db import *

def parse_message(message):
    """メッセージを解析"""
    # 学習記録追加
    study_match = re.match(r'(?:学習|study)[:：]\s*(.+)', message, re.IGNORECASE)
    if study_match:
        return parse_study(study_match.group(1))

    # 検索
    search_match = re.match(r'検索[:：]\s*(.+)', message)
    if search_match:
        return {'action': 'search', 'keyword': search_match.group(1)}

    # 一覧
    if message.strip() in ['学習一覧', '一覧', 'list', 'study']:
        return {'action': 'list'}

    # 統計
    if message.strip() in ['統計', 'stats', '学習統計']:
        return {'action': 'stats'}

    return None

def parse_study(content):
    """学習を解析"""
    result = {'action': 'add_study', 'subject': None, 'duration': None, 'note': None}

    # 科目 (最初の部分)
    subject_match = re.match(r'^([^、,（\(【♪]+)', content)
    if subject_match:
        result['subject'] = subject_match.group(1).strip()
        content = content.replace(subject_match.group(0), '').strip()

    # 時間
    duration_match = re.search(r'(\d+)\s*(分|時間|hour|h|min)', content)
    if duration_match:
        value, unit = duration_match.groups()
        if unit in ['時間', 'hour', 'h']:
            result['duration'] = int(value) * 60
        else:
            result['duration'] = int(value)

    # メモ
    note_match = re.search(r'メモ[:：]\s*(.+)', content)
    if note_match:
        result['note'] = note_match.group(1).strip()

    return result

def handle_message(message):
    """メッセージを処理"""
    parsed = parse_message(message)

    if not parsed:
        return None

    action = parsed['action']

    if action == 'add_study':
        if not parsed['subject'] or not parsed['duration']:
            return "❌ 科目と時間を入力してください"

        session_id = add_study_session(
            parsed['subject'],
            parsed['duration'],
            parsed['note']
        )

        # 時間をフォーマット
        hours = parsed['duration'] // 60
        minutes = parsed['duration'] % 60
        time_str = f"{hours}時間{minutes}分" if hours > 0 else f"{minutes}分"

        response = f"📚 学習記録 #{session_id} 追加完了\n"
        response += f"科目: {parsed['subject']}\n"
        response += f"時間: {time_str}"
        if parsed['note']:
            response += f"\nメモ: {parsed['note']}"

        return response

    elif action == 'list':
        sessions = list_study_sessions()

        if not sessions:
            return "📚 学習記録がありません"

        response = f"📚 学習記録一覧 ({len(sessions)}件):\n"
        for session in sessions:
            response += format_session(session)

        return response

    elif action == 'stats':
        stats = get_study_stats(days=7)

        response = "📊 週間学習統計:\n"
        response += f"合計時間: {stats['total_hours']}時間{stats['total_minutes_only']}分\n"
        response += f"合計回数: {stats['count']}回\n\n"

        if stats['by_subject']:
            response += "科目別:\n"
            for subject in stats['by_subject']:
                h = subject['total'] // 60
                m = subject['total'] % 60
                time_str = f"{h}時間{m}分" if h > 0 else f"{m}分"
                response += f"  - {subject['subject']}: {time_str} ({subject['count']}回)\n"

        return response

    return None

def format_session(session):
    """学習記録をフォーマット"""
    id, subject, duration, note, created_at = session

    hours = duration // 60
    minutes = duration % 60
    time_str = f"{hours}時間{minutes}分" if hours > 0 else f"{minutes}分"

    response = f"\n[{id}] {subject}\n"
    response += f"    時間: {time_str}"
    if note:
        response += f"\n    メモ: {note}"
    response += f"\n    日時: {created_at}"

    return response

if __name__ == '__main__':
    # テスト
    init_db()

    test_messages = [
        "学習: Python, 1時間30分, メモ: 基礎復習",
        "学習: 数学, 45分",
        "学習: 英語, 2時間, メモ: リスニング",
        "学習一覧",
        "統計",
    ]

    for msg in test_messages:
        print(f"\n入力: {msg}")
        result = handle_message(msg)
        if result:
            print(result)
