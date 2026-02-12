#!/usr/bin/env python3
"""
ワークアウトエージェント #47 - Discord連携
"""

import re
from datetime import datetime, timedelta
from db import *

def parse_message(message):
    """メッセージを解析"""
    # 追加
    add_match = re.match(r'(?:ワークアウト|workout|筋トレ|training|運動)[：:]\s*(.+)', message, re.IGNORECASE)
    if add_match:
        return {'action': 'add', 'content': add_match.group(1)}

    # 更新
    update_match = re.match(r'(?:更新|update)[：:]\s*(\d+)\s*(.+)', message, re.IGNORECASE)
    if update_match:
        return {'action': 'update', 'workout_id': int(update_match.group(1)), 'content': update_match.group(2)}

    # 削除
    delete_match = re.match(r'(?:削除|delete|remove)[：:]\s*(\d+)', message, re.IGNORECASE)
    if delete_match:
        return {'action': 'delete', 'workout_id': int(delete_match.group(1))}

    # 検索
    search_match = re.match(r'(?:検索|search)[：:]\s*(.+)', message, re.IGNORECASE)
    if search_match:
        return {'action': 'search', 'keyword': search_match.group(1)}

    # 一覧
    if message.strip() in ['ワークアウト', 'workout', '筋トレ', 'training', '運動', 'workouts']:
        return {'action': 'list'}

    # 種目一覧
    if message.strip() in ['種目', 'exercises', '種目一覧']:
        return {'action': 'exercises'}

    # カテゴリ
    if message.strip() in ['カテゴリ', 'categories']:
        return {'action': 'categories'}

    # 統計
    if message.strip() in ['統計', 'stats', 'statistics']:
        return {'action': 'stats'}

    # 今日
    if message.strip() in ['今日', 'today']:
        return {'action': 'today'}

    return None

def parse_workout_content(content):
    """ワークアウト内容を解析"""
    result = {'exercise': None, 'sets': None, 'reps': None, 'weight': None,
              'unit': 'kg', 'date': None, 'time': None, 'notes': None,
              'category': None, 'rpe': None}

    # 種目
    exercise_match = re.search(r'(?:種目|exercise)[：:]\s*(.+)', content, re.IGNORECASE)
    if exercise_match:
        result['exercise'] = exercise_match.group(1).strip()

    # セット数
    sets_match = re.search(r'(?:セット|sets?)[×:]?\s*(\d+)', content, re.IGNORECASE)
    if sets_match:
        result['sets'] = int(sets_match.group(1))

    # 回数
    reps_match = re.search(r'(?:回数|reps?|回)[×:]?\s*(\d+)', content, re.IGNORECASE)
    if reps_match:
        result['reps'] = int(reps_match.group(1))

    # 重量
    weight_match = re.search(r'(?:重量|weight)[×:]?\s*(\d+(?:\.\d+)?)', content, re.IGNORECASE)
    if weight_match:
        result['weight'] = float(weight_match.group(1))

    # 単位
    unit_match = re.search(r'(?:単位|unit)[×:]?\s*(kg|lb|lbs)', content, re.IGNORECASE)
    if unit_match:
        result['unit'] = unit_match.group(1).lower()

    # RPE
    rpe_match = re.search(r'(?:rpe|RPE)[×:]?\s*(\d{1,2})', content, re.IGNORECASE)
    if rpe_match:
        result['rpe'] = int(rpe_match.group(1))

    # カテゴリ
    category_match = re.search(r'(?:カテゴリ|category)[：:]\s*(.+)', content, re.IGNORECASE)
    if category_match:
        result['category'] = category_match.group(1).strip()

    # 日付
    date_match = re.search(r'(?:日付|date)[：:]\s*([^、,]+)', content, re.IGNORECASE)
    if date_match:
        result['date'] = parse_date(date_match.group(1).strip())

    # 時間
    time_match = re.search(r'(?:時間|time)[：:]\s*(\d{1,2}:\d{2})', content, re.IGNORECASE)
    if time_match:
        result['time'] = time_match.group(1).strip()

    # メモ
    notes_match = re.search(r'(?:メモ|memo|note)[：:]\s*(.+)', content, re.IGNORECASE)
    if notes_match:
        result['notes'] = notes_match.group(1).strip()

    # 最初の項目より前を種目とする
    for key in ['種目', 'exercise', 'セット', 'sets', '回数', 'reps', '重量', 'weight']:
        match = re.search(rf'{key}[×:：]', content)
        if match:
            result['exercise'] = content[:match.start()].strip()
            break
    else:
        result['exercise'] = content.strip()

    return result

def parse_update_content(content):
    """更新内容を解析"""
    result = {}

    # 種目
    exercise_match = re.search(r'(?:種目|exercise)[：:]\s*(.+)', content, re.IGNORECASE)
    if exercise_match:
        result['exercise'] = exercise_match.group(1).strip()

    # セット数
    sets_match = re.search(r'(?:セット|sets?)[×:]?\s*(\d+)', content, re.IGNORECASE)
    if sets_match:
        result['sets'] = int(sets_match.group(1))

    # 回数
    reps_match = re.search(r'(?:回数|reps?|回)[×:]?\s*(\d+)', content, re.IGNORECASE)
    if reps_match:
        result['reps'] = int(reps_match.group(1))

    # 重量
    weight_match = re.search(r'(?:重量|weight)[×:]?\s*(\d+(?:\.\d+)?)', content, re.IGNORECASE)
    if weight_match:
        result['weight'] = float(weight_match.group(1))

    # 単位
    unit_match = re.search(r'(?:単位|unit)[×:]?\s*(kg|lb|lbs)', content, re.IGNORECASE)
    if unit_match:
        result['unit'] = unit_match.group(1).lower()

    # RPE
    rpe_match = re.search(r'(?:rpe|RPE)[×:]?\s*(\d{1,2})', content, re.IGNORECASE)
    if rpe_match:
        result['rpe'] = int(rpe_match.group(1))

    # カテゴリ
    category_match = re.search(r'(?:カテゴリ|category)[：:]\s*(.+)', content, re.IGNORECASE)
    if category_match:
        result['category'] = category_match.group(1).strip()

    # 日付
    date_match = re.search(r'(?:日付|date)[：:]\s*([^、,]+)', content, re.IGNORECASE)
    if date_match:
        result['date'] = parse_date(date_match.group(1).strip())

    # 時間
    time_match = re.search(r'(?:時間|time)[：:]\s*(\d{1,2}:\d{2})', content, re.IGNORECASE)
    if time_match:
        result['time'] = time_match.group(1).strip()

    # メモ
    notes_match = re.search(r'(?:メモ|memo|note)[：:]\s*(.+)', content, re.IGNORECASE)
    if notes_match:
        result['notes'] = notes_match.group(1).strip()

    return result

def parse_date(date_str):
    """日付を解析"""
    today = datetime.now()

    if '今日' in date_str:
        return today.strftime("%Y-%m-%d")
    if '昨日' in date_str:
        return (today - timedelta(days=1)).strftime("%Y-%m-%d")
    if '明日' in date_str:
        return (today + timedelta(days=1)).strftime("%Y-%m-%d")

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
        content = parse_workout_content(parsed['content'])

        if not content['exercise']:
            return "❌ 種目を入力してください"

        workout_id = add_workout(
            exercise=content['exercise'],
            sets=content['sets'] or 3,
            reps=content['reps'],
            weight=content['weight'],
            unit=content['unit'],
            date=content['date'],
            time=content['time'],
            notes=content['notes'],
            category=content['category'],
            rpe=content['rpe']
        )

        response = f"💪 ワークアウト #{workout_id} 追加完了\n"
        response += f"種目: {content['exercise']}\n"
        response += f"セット: {content['sets'] or 3}セット"
        if content['reps']:
            response += f" × {content['reps']}回"
        if content['weight']:
            response += f" × {content['weight']}{content['unit']}"
        if content['rpe']:
            response += f"\nRPE: {content['rpe']}"
        if content['date']:
            response += f"\n日付: {content['date']}"
        if content['notes']:
            response += f"\nメモ: {content['notes']}"

        return response

    elif action == 'update':
        updates = parse_update_content(parsed['content'])

        if not updates:
            return "❌ 更新内容がありません"

        update_workout(parsed['workout_id'], **updates)

        response = f"✅ ワークアウト #{parsed['workout_id']} 更新完了"

        return response

    elif action == 'delete':
        delete_workout(parsed['workout_id'])
        return f"🗑️ ワークアウト #{parsed['workout_id']} 削除完了"

    elif action == 'search':
        keyword = parsed['keyword']
        workouts = search_workouts(keyword)

        if not workouts:
            return f"🔍 「{keyword}」の検索結果: 見つかりませんでした"

        response = f"🔍 「{keyword}」の検索結果 ({len(workouts)}件):\n"
        for workout in workouts:
            response += format_workout(workout)

        return response

    elif action == 'list':
        workouts = list_workouts()

        if not workouts:
            return "💪 ワークアウト記録がありません"

        response = f"💪 ワークアウト一覧 ({len(workouts)}件):\n"
        for workout in workouts:
            response += format_workout(workout)

        return response

    elif action == 'exercises':
        exercises = get_exercises()

        if not exercises:
            return "📋 種目がありません"

        response = "📋 種目一覧:\n"
        for exercise, category, count, avg_weight in exercises:
            response += f"  • {exercise}"
            if category:
                response += f" [{category}]"
            response += f" ({count}回"
            if avg_weight:
                response += f", 平均: {avg_weight:.1f}kg"
            response += ")\n"

        return response

    elif action == 'categories':
        categories = get_categories()

        if not categories:
            return "📁 カテゴリがありません"

        response = "📁 カテゴリ一覧:\n"
        for category, count in categories:
            response += f"  • {category} ({count}回)\n"

        return response

    elif action == 'stats':
        stats = get_stats()

        response = "📊 統計情報:\n"
        response += f"総ワークアウト数: {stats['total_workouts']}回\n"
        response += f"総セット数: {stats['total_sets']}セット\n"
        response += f"総回数: {stats['total_reps']}回\n"
        response += f"トレーニング日数: {stats['training_days']}日\n"
        if stats['max_weight']:
            response += f"最大重量: {stats['max_weight']}kg\n"
        response += f"今日: {stats['today']}回\n"
        response += f"今月: {stats['this_month']}回"

        return response

    elif action == 'today':
        date = datetime.now().strftime("%Y-%m-%d")
        workouts = get_by_date(date)

        if not workouts:
            return f"💪 今日のワークアウトはまだありません"

        response = f"💪 今日のワークアウト ({len(workouts)}件):\n"
        for workout in workouts:
            response += format_workout(workout, show_date=False, show_time=True)

        return response

    return None

def format_workout(workout, show_date=True, show_time=False):
    """ワークアウトをフォーマット"""
    id, exercise, sets, reps, weight, unit, date, time, notes, category, rpe, created_at = workout

    response = ""
    if show_date:
        response = f"\n💪 [{id}] {date} - {exercise}\n"
    else:
        response = f"\n💪 [{id}] {exercise}"
        if show_time and time:
            response += f" ({time})"
        response += "\n"

    parts = []
    parts.append(f"{sets}セット")
    if reps:
        parts.append(f"{reps}回")
    if weight:
        parts.append(f"{weight}{unit}")

    response += f"    {' × '.join(parts)}"

    if rpe:
        response += f"\n    RPE: {rpe}"
    if category:
        response += f"\n    カテゴリ: {category}"
    if notes:
        response += f"\n    📝 {notes}"

    return response

if __name__ == '__main__':
    init_db()

    test_messages = [
        "ワークアウト: ベンチプレス, セット: 3, 回数: 10, 重量: 60",
        "ワークアウト: スクワット, 4×12×80kg",
        "今日",
        "統計",
    ]

    for msg in test_messages:
        print(f"\n入力: {msg}")
        result = handle_message(msg)
        if result:
            print(result)
