#!/usr/bin/env python3
"""
フィットネスエージェント #35 - Discord連携
"""

import re
from datetime import datetime
from db import *

def parse_message(message):
    """メッセージを解析"""
    # トレーニング追加
    workout_match = re.match(r'(?:トレーニング|training|workout|筋トレ)[：:]\s*(.+)', message, re.IGNORECASE)
    if workout_match:
        return parse_add(workout_match.group(1))

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
    list_match = re.match(r'(?:(?:トレーニング|training|workout|筋トレ)(?:一覧|list)|list|workouts)', message, re.IGNORECASE)
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

    # 種目別
    exercise_match = re.match(r'(?:種目|exercise)[：:]\s*(.+)', message, re.IGNORECASE)
    if exercise_match:
        return {'action': 'list_by_exercise', 'exercise': exercise_match.group(1)}

    # 統計
    if message.strip() in ['統計', 'stats', 'トレーニング統計']:
        return {'action': 'stats'}

    return None

def parse_add(content):
    """トレーニング追加を解析"""
    result = {'action': 'add', 'date': None, 'exercise': None, 'sets': None, 'reps': None,
              'weight': None, 'weight_unit': 'kg', 'duration': None, 'duration_unit': 'minutes', 'notes': None}

    # 日付
    date_match = re.search(r'(?:日付|date)[：:]\s*([^、,]+)', content)
    if date_match:
        result['date'] = parse_date(date_match.group(1).strip())
    else:
        # デフォルトは今日
        result['date'] = datetime.now().strftime("%Y-%m-%d")

    # 種目 (最初の部分)
    exercise_match = re.match(r'^([^、,（\(×]+)', content)
    if exercise_match:
        result['exercise'] = exercise_match.group(1).strip()

    # セット
    sets_match = re.search(r'(?:セット|sets?)[×:：]\s*(\d+)', content)
    if sets_match:
        result['sets'] = int(sets_match.group(1))

    # 回数
    reps_match = re.search(r'(?:回数|reps?|回)[×:：]\s*(\d+)', content)
    if reps_match:
        result['reps'] = int(reps_match.group(1))

    # 重量
    weight_match = re.search(r'(?:重量|weight|kg|lb)[：:]?\s*(\d+)\s*(kg|lb)?', content)
    if weight_match:
        result['weight'] = int(weight_match.group(1))
        if weight_match.group(2):
            result['weight_unit'] = weight_match.group(2)

    # 時間
    duration_match = re.search(r'(?:時間|duration|分|min|時間h?|hour)[：:]?\s*(\d+)\s*(分|min|時間|hour)?', content)
    if duration_match:
        result['duration'] = int(duration_match.group(1))
        if duration_match.group(2):
            if '時間' in duration_match.group(2) or 'hour' in duration_match.group(2).lower():
                result['duration_unit'] = 'hours'
                result['duration'] *= 60  # 時間を分に変換
            else:
                result['duration_unit'] = 'minutes'

    # メモ
    notes_match = re.search(r'(?:メモ|備考|memo|note)[：:]\s*(.+)', content)
    if notes_match:
        result['notes'] = notes_match.group(1).strip()

    # 種目がまだない場合、最初の項目より前を種目とする
    if not result['exercise']:
        for key in ['日付', 'date', 'セット', 'sets', '回数', 'reps', '回', '重量', 'weight', 'kg', 'lb',
                    '時間', 'duration', '分', 'min', 'メモ', '備考', 'memo', 'note']:
            match = re.search(rf'{key}[×:：]', content)
            if match:
                result['exercise'] = content[:match.start()].strip()
                break
        else:
            result['exercise'] = content.strip()

    return result

def parse_update(content):
    """更新内容を解析"""
    result = {}

    # 日付
    date_match = re.search(r'(?:日付|date)[：:]\s*([^、,]+)', content)
    if date_match:
        result['date'] = parse_date(date_match.group(1).strip())

    # 種目
    exercise_match = re.search(r'(?:種目|exercise)[：:]\s*([^、,]+)', content)
    if exercise_match:
        result['exercise'] = exercise_match.group(1).strip()

    # セット
    sets_match = re.search(r'(?:セット|sets?)[×:：]\s*(\d+)', content)
    if sets_match:
        result['sets'] = int(sets_match.group(1))

    # 回数
    reps_match = re.search(r'(?:回数|reps?|回)[×:：]\s*(\d+)', content)
    if reps_match:
        result['reps'] = int(reps_match.group(1))

    # 重量
    weight_match = re.search(r'(?:重量|weight|kg|lb)[：:]?\s*(\d+)\s*(kg|lb)?', content)
    if weight_match:
        result['weight'] = int(weight_match.group(1))
        if weight_match.group(2):
            result['weight_unit'] = weight_match.group(2)

    # 時間
    duration_match = re.search(r'(?:時間|duration|分|min)[：:]?\s*(\d+)', content)
    if duration_match:
        result['duration'] = int(duration_match.group(1))

    # メモ
    notes_match = re.search(r'(?:メモ|備考|memo|note)[：:]\s*(.+)', content)
    if notes_match:
        result['notes'] = notes_match.group(1).strip()

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

    # 数字 + 日前
    days_match = re.match(r'(\d+)日前', date_str)
    if days_match:
        from datetime import timedelta
        days = int(days_match.group(1))
        return (today - timedelta(days=days)).strftime("%Y-%m-%d")

    return None

def handle_message(message):
    """メッセージを処理"""
    parsed = parse_message(message)

    if not parsed:
        return None

    action = parsed['action']

    if action == 'add':
        if not parsed['exercise']:
            return "❌ 種目を入力してください"

        workout_id = add_workout(
            parsed['date'],
            parsed['exercise'],
            parsed['sets'],
            parsed['reps'],
            parsed['weight'],
            parsed['weight_unit'],
            parsed['duration'],
            parsed['duration_unit'],
            parsed['notes']
        )

        response = f"💪 トレーニング #{workout_id} 追加完了\n"
        response += f"種目: {parsed['exercise']}\n"
        response += f"日付: {parsed['date']}\n"
        if parsed['sets'] and parsed['reps']:
            response += f"{parsed['sets']}セット × {parsed['reps']}回\n"
        if parsed['weight']:
            response += f"重量: {parsed['weight']}{parsed['weight_unit']}\n"
        if parsed['duration']:
            response += f"時間: {parsed['duration']}{parsed['duration_unit']}\n"
        if parsed['notes']:
            response += f"メモ: {parsed['notes']}"

        return response

    elif action == 'update':
        updates = parse_update(parsed['content'])

        if not updates:
            return "❌ 更新内容がありません"

        update_workout(parsed['workout_id'], **updates)

        response = f"✅ トレーニング #{parsed['workout_id']} 更新完了"

        return response

    elif action == 'delete':
        delete_workout(parsed['workout_id'])
        return f"🗑️ トレーニング #{parsed['workout_id']} 削除完了"

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
            return "💪 トレーニングがありません"

        response = f"💪 トレーニング一覧 ({len(workouts)}件):\n"
        for workout in workouts:
            response += format_workout(workout)

        return response

    elif action == 'today':
        today = datetime.now().strftime("%Y-%m-%d")
        workouts = get_by_date(today)

        if not workouts:
            return f"💪 今日のトレーニングはまだありません"

        response = f"💪 今日のトレーニング ({len(workouts)}件):\n"
        for workout in workouts:
            response += format_workout(workout)

        return response

    elif action == 'yesterday':
        from datetime import timedelta
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        workouts = get_by_date(yesterday)

        if not workouts:
            return f"💪 昨日のトレーニングはありません"

        response = f"💪 昨日のトレーニング ({len(workouts)}件):\n"
        for workout in workouts:
            response += format_workout(workout)

        return response

    elif action == 'this_month':
        current_month = datetime.now().strftime("%Y-%m")
        from datetime import timedelta
        first_day = f"{current_month}-01"
        next_month = datetime(datetime.now().year, datetime.now().month + 1, 1).strftime("%Y-%m-%d") if datetime.now().month < 12 else f"{datetime.now().year + 1}-01-01"

        workouts = list_workouts(date_from=first_day, date_to=next_month)

        if not workouts:
            return f"💪 今月のトレーニングはありません"

        response = f"💪 今月のトレーニング ({len(workouts)}件):\n"
        for workout in workouts:
            response += format_workout(workout)

        return response

    elif action == 'list_by_exercise':
        workouts = list_workouts(exercise=parsed['exercise'])

        if not workouts:
            return f"💪 「{parsed['exercise']}」のトレーニングはありません"

        response = f"💪 {parsed['exercise']} ({len(workouts)}件):\n"
        for workout in workouts:
            response += format_workout(workout)

        return response

    elif action == 'stats':
        stats = get_stats()

        response = "📊 トレーニング統計:\n"
        response += f"全トレーニング数: {stats['total']}件\n"
        response += f"今日: {stats['today']}件\n"
        response += f"今月: {stats['this_month']}件\n"
        response += f"総セット数: {stats['total_sets']}セット\n"
        if stats['total_volume'] > 0:
            response += f"総トン数: {stats['total_volume']:,}kg\n"
        response += f"種目数: {stats['exercises']}種類"

        return response

    return None

def format_workout(workout):
    """トレーニングをフォーマット"""
    id, date, exercise, sets, reps, weight, weight_unit, duration, duration_unit, notes, created_at = workout

    response = f"\n📅 [{id}] {date} - {exercise}\n"

    parts = []
    if sets and reps:
        parts.append(f"{sets}×{reps}")
    if weight:
        parts.append(f"{weight}{weight_unit}")
    if duration:
        parts.append(f"{duration}{duration_unit}")

    if parts:
        response += f"    💪 {' '.join(parts)}\n"

    if notes:
        response += f"    📝 {notes}\n"

    return response

if __name__ == '__main__':
    # テスト
    init_db()

    test_messages = [
        "トレーニング: ベンチプレス, セット: 3, 回数: 10, 重量: 60",
        "トレーニング: ランニング, 時間: 30分",
        "今日",
        "種目: ベンチプレス",
        "統計",
    ]

    for msg in test_messages:
        print(f"\n入力: {msg}")
        result = handle_message(msg)
        if result:
            print(result)
