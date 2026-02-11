#!/usr/bin/env python3
"""
健康管理エージェント #3 - Discord連携
"""

import re
from datetime import datetime
from db import *

def parse_message(message):
    """メッセージを解析"""
    # 睡眠記録
    sleep_match = re.match(r'睡眠[:：]\s*(.+)', message)
    if sleep_match:
        return parse_sleep(sleep_match.group(1))

    # 運動記録
    exercise_match = re.match(r'運動[:：]\s*(.+)', message)
    if exercise_match:
        return parse_exercise(exercise_match.group(1))

    # 食事記録
    meal_match = re.match(r'食事[:：]\s*(.+)', message)
    if meal_match:
        return parse_meal(meal_match.group(1))

    # 体重記録
    weight_match = re.match(r'体重[:：]\s*(.+)', message)
    if weight_match:
        return {'action': 'weight', 'weight': weight_match.group(1)}

    # 統計
    if message.strip() in ['統計', 'stats', '健康']:
        return {'action': 'stats'}

    return None

def parse_sleep(content):
    """睡眠記録を解析"""
    # 形式: 23:00-7:00, 質:4
    match = re.search(r'(\d{1,2}):(\d{2})[~-](\d{1,2}):(\d{2}),?\s*質?[:：]\s*(\d)', content)
    if match:
        bedtime_hour, bedtime_min, wakeup_hour, wakeup_min, quality = match.groups()

        # 日付判定
        now = datetime.now()
        bedtime_dt = datetime(now.year, now.month, now.day, int(bedtime_hour), int(bedtime_min))
        wakeup_dt = datetime(now.year, now.month, now.day, int(wakeup_hour), int(wakeup_min))

        # 起床時間が就寝時間より早い場合、翌日
        if wakeup_dt < bedtime_dt:
            wakeup_dt += timedelta(days=1)

        return {
            'action': 'sleep',
            'bedtime': bedtime_dt.strftime("%Y-%m-%d %H:%M"),
            'wakeup': wakeup_dt.strftime("%Y-%m-%d %H:%M"),
            'quality': int(quality)
        }

    return None

def parse_exercise(content):
    """運動記録を解析"""
    # 形式: ランニング 30分, 5km, 300kcal
    result = {'action': 'exercise', 'type': None, 'duration': None, 'distance': None, 'calories': None, 'notes': None}

    # 運動種類
    type_match = re.match(r'^([^\d\s]+)', content)
    if type_match:
        result['type'] = type_match.group(1)

    # 時間
    duration_match = re.search(r'(\d+(?:\.\d+)?)\s*(分|時間|hour|h)', content)
    if duration_match:
        value, unit = duration_match.groups()
        if unit in ['時間', 'hour', 'h']:
            result['duration'] = float(value) * 60
        else:
            result['duration'] = float(value)

    # 距離
    distance_match = re.search(r'(\d+(?:\.\d+)?)\s*(km|m|キロ)', content)
    if distance_match:
        value, unit = distance_match.groups()
        if unit == 'm':
            result['distance'] = float(value) / 1000
        else:
            result['distance'] = float(value)

    # カロリー
    calories_match = re.search(r'(\d+)\s*(kcal|カロリー)', content)
    if calories_match:
        result['calories'] = float(calories_match.group(1))

    return result

def parse_meal(content):
    """食事記録を解析"""
    # 形式: 朝食, ラーメン, 800kcal
    meal_types = ['朝食', '昼食', '夕食', '間食']

    meal_type = '間食'
    for mt in meal_types:
        if mt in content:
            meal_type = mt
            content = content.replace(mt, '').strip()
            break

    # カロリー
    calories = None
    calories_match = re.search(r'(\d+)\s*(kcal|カロリー)', content)
    if calories_match:
        calories = float(calories_match.group(1))
        content = content.replace(calories_match.group(0), '').strip()

    return {
        'action': 'meal',
        'meal_type': meal_type,
        'content': content,
        'calories': calories
    }

def handle_message(message):
    """メッセージを処理"""
    parsed = parse_message(message)

    if not parsed:
        return None

    action = parsed['action']

    if action == 'sleep':
        try:
            memo_id = add_sleep(parsed['bedtime'], parsed['wakeup'], parsed['quality'])
            duration = parsed['wakeup']
            response = f"💤 睡眠記録 #{memo_id} 追加完了\n"
            response += f"就寝: {parsed['bedtime']}\n"
            response += f"起床: {parsed['wakeup']}\n"
            response += f"質: {parsed['quality']}/5"
            return response
        except Exception as e:
            return f"❌ エラー: {str(e)}"

    elif action == 'exercise':
        if not parsed['type'] or not parsed['duration']:
            return "❌ 運動種類と時間を指定してください"

        memo_id = add_exercise(
            parsed['type'],
            parsed['duration'],
            parsed['distance'],
            parsed['calories'],
            parsed['notes']
        )

        response = f"🏃 運動記録 #{memo_id} 追加完了\n"
        response += f"種類: {parsed['type']}\n"
        response += f"時間: {parsed['duration']}分\n"
        if parsed['distance']:
            response += f"距離: {parsed['distance']}km\n"
        if parsed['calories']:
            response += f"消費カロリー: {parsed['calories']}kcal"
        return response

    elif action == 'meal':
        memo_id = add_meal(parsed['meal_type'], parsed['content'], parsed['calories'])

        response = f"🍽️ 食事記録 #{memo_id} 追加完了\n"
        response += f"種類: {parsed['meal_type']}\n"
        response += f"内容: {parsed['content']}"
        if parsed['calories']:
            response += f"\nカロリー: {parsed['calories']}kcal"
        return response

    elif action == 'weight':
        try:
            weight = float(parsed['weight'])
            memo_id = add_weight(weight)
            return f"⚖️ 体重記録 #{memo_id} 追加完了: {weight}kg"
        except ValueError:
            return "❌ 体重は数字で入力してください"

    elif action == 'stats':
        stats = get_recent_records(days=7)

        response = "📊 週間統計 (過去7日間):\n\n"
        response += f"💤 睡眠:\n"
        response += f"  記録数: {stats['sleep']['count']}回\n"
        response += f"  平均時間: {stats['sleep']['avg_duration']}時間\n"
        response += f"  平均質: {stats['sleep']['avg_quality']}/5\n\n"

        response += f"🏃 運動:\n"
        response += f"  記録数: {stats['exercise']['count']}回\n"
        response += f"  総時間: {stats['exercise']['total_duration']}分\n"
        response += f"  総カロリー: {stats['exercise']['total_calories']}kcal\n\n"

        response += f"🍽️ 食事:\n"
        response += f"  記録数: {stats['meal']['count']}回\n"
        response += f"  総カロリー: {stats['meal']['total_calories']}kcal"

        return response

    return None

if __name__ == '__main__':
    # テスト
    from datetime import timedelta
    init_db()

    test_messages = [
        "睡眠: 23:00-7:00, 質:4",
        "運動: ランニング 30分, 5km, 300kcal",
        "食事: 朝食, オムライス, 600kcal",
        "体重: 65.5",
        "統計",
    ]

    for msg in test_messages:
        print(f"\n入力: {msg}")
        result = handle_message(msg)
        if result:
            print(result)
