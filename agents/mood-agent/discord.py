#!/usr/bin/env python3
"""
感情記録エージェント #14 - Discord連携
"""

import re
from db import *

def parse_message(message):
    """メッセージを解析"""
    # 感情追加
    mood_match = re.match(r'(?:感情|mood)[:：]\s*(.+)', message, re.IGNORECASE)
    if mood_match:
        return parse_mood(mood_match.group(1))

    # 検索
    search_match = re.match(r'検索[:：]\s*(.+)', message)
    if search_match:
        return {'action': 'search', 'keyword': search_match.group(1)}

    # 一覧
    if message.strip() in ['感情一覧', '一覧', 'list', 'moods']:
        return {'action': 'list'}

    # 統計
    if message.strip() in ['統計', 'stats', '感情統計']:
        return {'action': 'stats'}

    return None

def parse_mood(content):
    """感情を解析"""
    result = {'action': 'add_mood', 'type': None, 'intensity': 3, 'cause': None, 'memo': None}

    # 種類
    type_map = {
        '嬉': 'happy', '幸': 'happy', 'ハッピー': 'happy',
        '悲': 'sad', 'サ': 'sad', '悲しい': 'sad',
        '怒': 'angry', 'イラ': 'angry', '怒って': 'angry',
        '不安': 'anxious', '心配': 'anxious',
        'ワク': 'excited', '興奮': 'excited',
        '静': 'calm', '落ち': 'calm', '穏やか': 'calm',
        '疲': 'tired', '眠': 'tired',
    }

    for key, value in type_map.items():
        if key in content:
            result['type'] = value
            break

    # 強度
    intensity_match = re.search(r'強度[:：]\s*(\d+)', content)
    if intensity_match:
        result['intensity'] = int(intensity_match.group(1))
        result['intensity'] = max(1, min(5, result['intensity']))

    # 原因
    cause_match = re.search(r'原因[:：]\s*([^、,メモ]+)', content)
    if cause_match:
        result['cause'] = cause_match.group(1).strip()

    # メモ
    memo_match = re.search(r'メモ[:：]\s*(.+)', content)
    if memo_match:
        result['memo'] = memo_match.group(1).strip()

    # 種類がまだない場合、最初の部分を種類とする
    if not result['type']:
        cause_match = re.search(r'原因[:：]', content)
        if cause_match:
            result['type'] = 'other'
        else:
            result['type'] = 'other'

    return result

def handle_message(message):
    """メッセージを処理"""
    parsed = parse_message(message)

    if not parsed:
        return None

    action = parsed['action']

    if action == 'add_mood':
        if not parsed['type']:
            return "❌ 感情の種類を入力してください（例: 嬉しい, 悲しい, 怒っている）"

        mood_id = add_mood(
            parsed['type'],
            parsed['intensity'],
            parsed['cause'],
            parsed['memo']
        )

        type_icons = {
            'happy': '😊',
            'sad': '😢',
            'angry': '😠',
            'anxious': '😰',
            'excited': '🤩',
            'calm': '😌',
            'tired': '😴',
            'other': '😐'
        }
        type_icon = type_icons.get(parsed['type'], '😐')

        response = f"{type_icon} 感情 #{mood_id} 追加完了\n"
        response += f"種類: {parsed['type']}\n"
        response += f"強度: {parsed['intensity']}/5"
        if parsed['cause']:
            response += f"\n原因: {parsed['cause']}"
        if parsed['memo']:
            response += f"\nメモ: {parsed['memo']}"

        return response

    elif action == 'list':
        moods = list_moods()

        if not moods:
            return "😐 感情がありません"

        response = f"😐 感情一覧 ({len(moods)}件):\n"
        for mood in moods:
            response += format_mood(mood)

        return response

    elif action == 'stats':
        stats = get_mood_stats(days=7)

        type_icons = {
            'happy': '😊',
            'sad': '😢',
            'angry': '😠',
            'anxious': '😰',
            'excited': '🤩',
            'calm': '😌',
            'tired': '😴',
            'other': '😐'
        }

        response = "📊 週間感情統計:\n"
        response += f"合計: {stats['total']}件\n"
        response += f"平均強度: {stats['avg_intensity']}/5\n\n"

        if stats['by_type']:
            response += "種類別:\n"
            for mood_type, count in stats['by_type'].items():
                icon = type_icons.get(mood_type, '😐')
                response += f"  - {icon} {mood_type}: {count}件\n"

        return response

    return None

def format_mood(mood):
    """感情をフォーマット"""
    id, mood_type, intensity, cause, memo, created_at = mood

    type_icons = {
        'happy': '😊',
        'sad': '😢',
        'angry': '😠',
        'anxious': '😰',
        'excited': '🤩',
        'calm': '😌',
        'tired': '😴',
        'other': '😐'
    }
    type_icon = type_icons.get(mood_type, '😐')
    intensity_bar = '█' * intensity + '░' * (5 - intensity)

    response = f"\n{type_icon} [{id}] {mood_type}\n"
    response += f"    強度: {intensity}/5 {intensity_bar}"
    if cause:
        response += f"\n    原因: {cause}"
    if memo:
        response += f"\n    メモ: {memo}"
    response += f"\n    日時: {created_at}"

    return response

if __name__ == '__main__':
    # テスト
    init_db()

    test_messages = [
        "感情: 嬉しい, 強度:4, 原因: 新機能リリース",
        "感情: 疲れている, 強度:3, 原因: 徹夜",
        "感情: 不安, 強度:2, メモ: 進捗心配",
        "感情一覧",
        "統計",
    ]

    for msg in test_messages:
        print(f"\n入力: {msg}")
        result = handle_message(msg)
        if result:
            print(result)
