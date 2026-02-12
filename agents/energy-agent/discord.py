#!/usr/bin/env python3
"""
エネルギーレベル記録エージェント #62 - Discord連携
"""

import re
from datetime import datetime
from db import *

def parse_message(message):
    """メッセージを解析"""
    # 追加
    energy_match = re.match(r'(?:エネルギー|energy)[：:]\s*(.+)', message, re.IGNORECASE)
    if energy_match:
        return parse_energy(energy_match.group(1))

    # 一覧
    if message.strip() in ['エネルギー一覧', 'エネルギー', 'energy', 'list']:
        return {'action': 'list'}

    # 統計
    if message.strip() in ['統計', 'stats', 'エネルギー統計']:
        return {'action': 'stats'}

    return None

def parse_energy(content):
    """エネルギー情報を解析"""
    result = {'action': 'add_energy', 'level': None, 'time_period': None, 'activity': None, 'notes': None}

    # レベル (1-10)
    level_match = re.search(r'(\d+)', content)
    if level_match:
        result['level'] = int(level_match.group(1))
        result['level'] = max(1, min(10, result['level']))

    # 時間帯
    period_map = {
        '朝': 'morning', '午前': 'morning', 'morning': 'morning', 'am': 'morning',
        '昼': 'afternoon', '午後': 'afternoon', 'afternoon': 'afternoon', 'pm': 'afternoon',
        '夕': 'evening', '夕方': 'evening', 'evening': 'evening',
        '夜': 'night', '深夜': 'night', 'night': 'night'
    }

    for key, value in period_map.items():
        if key in content:
            result['time_period'] = value
            break

    # 活動
    activity_match = re.search(r'(?:活動|activity)[：:]\s*([^、,メモ]+)', content, re.IGNORECASE)
    if activity_match:
        result['activity'] = activity_match.group(1).strip()

    # メモ
    notes_match = re.search(r'(?:メモ|memo|note)[：:]\s*(.+)', content, re.IGNORECASE)
    if notes_match:
        result['notes'] = notes_match.group(1).strip()

    # レベルがまだない場合、最初の部分をレベルとする
    if result['level'] is None:
        # 数字がない場合はデフォルト5
        result['level'] = 5

    # 時間帯がまだない場合、現在時刻から推測
    if not result['time_period']:
        hour = datetime.now().hour
        if 5 <= hour < 12:
            result['time_period'] = 'morning'
        elif 12 <= hour < 17:
            result['time_period'] = 'afternoon'
        elif 17 <= hour < 21:
            result['time_period'] = 'evening'
        else:
            result['time_period'] = 'night'

    return result

def handle_message(message):
    """メッセージを処理"""
    parsed = parse_message(message)

    if not parsed:
        return None

    action = parsed['action']

    if action == 'add_energy':
        if parsed['level'] is None:
            return "❌ エネルギーレベルを入力してください（1-10）"

        energy_id = add_energy(
            parsed['level'],
            parsed['time_period'],
            parsed['activity'],
            parsed['notes']
        )

        level_bar = '█' * parsed['level'] + '░' * (10 - parsed['level'])
        period_text = {
            'morning': '🌅 朝',
            'afternoon': '☀️ 昼',
            'evening': '🌆 夕方',
            'night': '🌙 夜'
        }.get(parsed['time_period'], '')

        response = f"⚡ エネルギー #{energy_id} 追加完了\n"
        response += f"レベル: {parsed['level']}/10 {level_bar}\n"
        if period_text:
            response += f"時間帯: {period_text}\n"
        if parsed['activity']:
            response += f"活動: {parsed['activity']}\n"
        if parsed['notes']:
            response += f"メモ: {parsed['notes']}"

        return response

    elif action == 'list':
        energies = list_energy()

        if not energies:
            return "⚡ エネルギー記録がありません"

        response = f"⚡ エネルギー記録 ({len(energies)}件):\n"
        for energy in energies:
            response += format_energy(energy)

        return response

    elif action == 'stats':
        stats = get_stats(days=7)

        response = "📊 週間エネルギー統計:\n"
        response += f"記録数: {stats['total']}件\n"
        response += f"平均レベル: {stats['avg_level']}/10\n"
        response += f"最高: {stats['max']}/10\n"
        response += f"最低: {stats['min']}/10\n\n"

        if stats['by_period']:
            response += "時間帯別平均:\n"
            period_text = {
                'morning': '🌅 朝',
                'afternoon': '☀️ 昼',
                'evening': '🌆 夕方',
                'night': '🌙 夜'
            }
            for period, avg in stats['by_period'].items():
                text = period_text.get(period, period)
                response += f"  - {text}: {avg}/10\n"

        return response

    return None

def format_energy(energy):
    """エネルギー記録をフォーマット"""
    id, level, time_period, activity, notes, created_at = energy

    level_bar = '█' * level + '░' * (10 - level)
    period_text = {
        'morning': '🌅 朝',
        'afternoon': '☀️ 昼',
        'evening': '🌆 夕方',
        'night': '🌙 夜'
    }.get(time_period, '')

    response = f"\n⚡ [{id}] {level}/10 {level_bar}"
    if period_text:
        response += f" | {period_text}"
    if activity:
        response += f"\n    活動: {activity}"
    if notes:
        response += f"\n    メモ: {notes}"
    response += f"\n    日時: {created_at}"

    return response

if __name__ == '__main__':
    init_db()

    test_messages = [
        "エネルギー: 8, 朝, 活動: ジョギング",
        "エネルギー: 4, 昼, メモ: 会議で疲れた",
        "エネルギー: 9, 夜, 活動: プログラミング",
        "エネルギー一覧",
        "統計",
    ]

    for msg in test_messages:
        print(f"\n入力: {msg}")
        result = handle_message(msg)
        if result:
            print(result)
