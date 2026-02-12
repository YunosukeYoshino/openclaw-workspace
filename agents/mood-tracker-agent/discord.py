#!/usr/bin/env python3
"""
気分トラッカーエージェント #64 - Discord連携
"""

import re
from datetime import datetime
from db import *

def parse_message(message):
    """メッセージを解析"""
    # 気分追加
    mood_match = re.match(r'(?:気分|mood|feeling)[：:]\s*(.+)', message, re.IGNORECASE)
    if mood_match:
        return parse_mood(mood_match.group(1))

    # トリガー検索
    trigger_search_match = re.match(r'(?:トリガー|trigger)[：:]\s*(.+)', message, re.IGNORECASE)
    if trigger_search_match:
        return {'action': 'search_trigger', 'keyword': trigger_search_match.group(1)}

    # 一覧
    if message.strip() in ['気分一覧', '一覧', 'list', 'moods', 'mood list']:
        return {'action': 'list'}

    # 統計
    if message.strip() in ['統計', 'stats', '気分統計']:
        return {'action': 'stats'}

    return None

def parse_mood(content):
    """気分情報を解析"""
    result = {'action': 'add_mood', 'mood': None, 'intensity': 5, 'trigger': None, 'location': None, 'activity': None, 'notes': None}

    # 気分の種類
    mood_map = {
        'とても嬉': 'very_happy', '最高': 'very_happy', 'great': 'very_happy', 'awesome': 'very_happy',
        '嬉': 'happy', '幸せ': 'happy', 'happy': 'happy', 'good': 'happy',
        '普通': 'neutral', 'まあまあ': 'neutral', 'neutral': 'neutral', 'ok': 'neutral',
        '悲': 'sad', '残念': 'sad', 'sad': 'sad', 'bad': 'sad',
        'とても悲': 'very_sad', '最悪': 'very_sad', 'terrible': 'very_sad', 'awful': 'very_sad',
        '不安': 'anxious', '心配': 'anxious', 'anxious': 'anxious', 'worried': 'anxious',
        '穏や': 'calm', '落ち着': 'calm', 'calm': 'calm', 'relaxed': 'calm',
        '元気': 'energetic', '活力': 'energetic', 'energetic': 'energetic', 'energized': 'energetic',
        '疲': 'tired', '眠い': 'tired', 'tired': 'tired', 'sleepy': 'tired',
    }

    for key, value in mood_map.items():
        if key in content:
            result['mood'] = value
            break

    # 強度
    intensity_match = re.search(r'(?:強度|intensity)[：:]\s*(\d+)', content, re.IGNORECASE)
    if intensity_match:
        result['intensity'] = int(intensity_match.group(1))
        result['intensity'] = max(1, min(10, result['intensity']))

    # トリガー
    trigger_match = re.search(r'(?:トリガー|trigger|cause|原因)[：:]\s*([^、,場所]+)', content, re.IGNORECASE)
    if trigger_match:
        result['trigger'] = trigger_match.group(1).strip()

    # 場所
    location_match = re.search(r'(?:場所|location)[：:]\s*([^、,アクティビティ]+)', content, re.IGNORECASE)
    if location_match:
        result['location'] = location_match.group(1).strip()

    # アクティビティ
    activity_match = re.search(r'(?:アクティビティ|activity)[：:]\s*([^、,メモ]+)', content, re.IGNORECASE)
    if activity_match:
        result['activity'] = activity_match.group(1).strip()

    # メモ
    notes_match = re.search(r'(?:メモ|memo|note)[：:]\s*(.+)', content, re.IGNORECASE)
    if notes_match:
        result['notes'] = notes_match.group(1).strip()

    # 気分がまだない場合
    if not result['mood']:
        result['mood'] = 'neutral'

    return result

def handle_message(message):
    """メッセージを処理"""
    parsed = parse_message(message)

    if not parsed:
        return None

    action = parsed['action']

    if action == 'add_mood':
        if not parsed['mood']:
            return "❌ 気分を入力してください（例: 嬉しい, 悲しい, 普通）"

        mood_id = add_mood_entry(
            parsed['mood'],
            parsed['intensity'],
            parsed['trigger'],
            parsed['location'],
            parsed['activity'],
            parsed['notes']
        )

        mood_icons = {
            'very_happy': '🤩',
            'happy': '😊',
            'neutral': '😐',
            'sad': '😢',
            'very_sad': '😭',
            'anxious': '😰',
            'calm': '😌',
            'energetic': '💪',
            'tired': '😴',
            'other': '🤔'
        }
        mood_icon = mood_icons.get(parsed['mood'], '😐')
        intensity_bar = '█' * parsed['intensity'] + '░' * (10 - parsed['intensity'])

        response = f"{mood_icon} 気分 #{mood_id} 追加完了\n"
        response += f"気分: {parsed['mood']}\n"
        response += f"強度: {parsed['intensity']}/10 {intensity_bar}"
        if parsed['trigger']:
            response += f"\nトリガー: {parsed['trigger']}"
        if parsed['location']:
            response += f"\n場所: {parsed['location']}"
        if parsed['activity']:
            response += f"\nアクティビティ: {parsed['activity']}"
        if parsed['notes']:
            response += f"\nメモ: {parsed['notes']}"

        return response

    elif action == 'search_trigger':
        entries = search_by_trigger(parsed['keyword'], limit=10)

        if not entries:
            return f"🔍 「{parsed['keyword']}」の記録: 見つかりませんでした"

        response = f"🔍 「{parsed['keyword']}」の記録 ({len(entries)}件):\n"
        for entry in entries:
            response += format_mood_entry(entry)

        return response

    elif action == 'list':
        entries = list_mood_entries()

        if not entries:
            return "😐 気分記録がありません"

        response = f"😐 気分記録 ({len(entries)}件):\n"
        for entry in entries:
            response += format_mood_entry(entry)

        return response

    elif action == 'stats':
        stats = get_mood_stats(days=7)

        mood_icons = {
            'very_happy': '🤩',
            'happy': '😊',
            'neutral': '😐',
            'sad': '😢',
            'very_sad': '😭',
            'anxious': '😰',
            'calm': '😌',
            'energetic': '💪',
            'tired': '😴',
            'other': '🤔'
        }

        response = "📊 週間気分統計:\n"
        response += f"合計: {stats['total']}件\n\n"

        if stats['by_mood']:
            response += "気分別:\n"
            for m in stats['by_mood']:
                icon = mood_icons.get(m['mood'], '😐')
                response += f"  - {icon} {m['mood']}: {m['count']}件 (平均強度: {m['avg_intensity']}/10)\n"

        if stats['top_triggers']:
            response += "\n一般的なトリガー:\n"
            for trigger, count in stats['top_triggers']:
                response += f"  - {trigger}: {count}回\n"

        return response

    return None

def format_mood_entry(entry):
    """気分エントリーをフォーマット"""
    id, mood, intensity, trigger, location, activity, notes, created_at = entry

    mood_icons = {
        'very_happy': '🤩',
        'happy': '😊',
        'neutral': '😐',
        'sad': '😢',
        'very_sad': '😭',
        'anxious': '😰',
        'calm': '😌',
        'energetic': '💪',
        'tired': '😴',
        'other': '🤔'
    }
    mood_icon = mood_icons.get(mood, '😐')
    intensity_bar = '█' * intensity + '░' * (10 - intensity)

    response = f"\n{mood_icon} [{id}] {mood}"
    response += f"\n    強度: {intensity}/10 {intensity_bar}"
    if trigger:
        response += f"\n    トリガー: {trigger}"
    if location:
        response += f"\n    場所: {location}"
    if activity:
        response += f"\n    アクティビティ: {activity}"
    if notes:
        response += f"\n    メモ: {notes}"
    response += f"\n    日時: {created_at}"

    return response

if __name__ == '__main__':
    init_db()

    test_messages = [
        "気分: 嬉しい, 強度:8, トリガー: 友達と会った",
        "気分: 不安, 強度:5, トリガー: 重要なプレゼン",
        "気分: 元気, 強度:9, 場所: ジム, アクティビティ: 筋トレ",
        "気分一覧",
        "統計",
    ]

    for msg in test_messages:
        print(f"\n入力: {msg}")
        result = handle_message(msg)
        if result:
            print(result)
