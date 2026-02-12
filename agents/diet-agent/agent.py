#!/usr/bin/env python3
"""
ダイエットエージェント #48 - Discord連携
"""

import re
from datetime import datetime, timedelta
from db import *

def parse_message(message):
    """メッセージを解析"""
    # 追加
    add_match = re.match(r'(?:食事|meal|食べて|ate)[：:]\s*(.+)', message, re.IGNORECASE)
    if add_match:
        return {'action': 'add', 'content': add_match.group(1)}

    # 更新
    update_match = re.match(r'(?:更新|update)[：:]\s*(\d+)\s*(.+)', message, re.IGNORECASE)
    if update_match:
        return {'action': 'update', 'meal_id': int(update_match.group(1)), 'content': update_match.group(2)}

    # 削除
    delete_match = re.match(r'(?:削除|delete|remove)[：:]\s*(\d+)', message, re.IGNORECASE)
    if delete_match:
        return {'action': 'delete', 'meal_id': int(delete_match.group(1))}

    # 検索
    search_match = re.match(r'(?:検索|search)[：:]\s*(.+)', message, re.IGNORECASE)
    if search_match:
        return {'action': 'search', 'keyword': search_match.group(1)}

    # 目標設定
    goal_match = re.match(r'(?:目標|goal)[：:]\s*(.+)', message, re.IGNORECASE)
    if goal_match:
        return {'action': 'set_goal', 'content': goal_match.group(1)}

    # 一覧
    if message.strip() in ['食事', 'meal', 'meals', '食事記録']:
        return {'action': 'list'}

    # 今日
    if message.strip() in ['今日', 'today']:
        return {'action': 'today'}

    # 統計
    if message.strip() in ['統計', 'stats', 'statistics']:
        return {'action': 'stats'}

    # サマリー
    if message.strip() in ['サマリー', 'summary']:
        return {'action': 'summary'}

    return None

def parse_meal_content(content):
    """食事内容を解析"""
    result = {'meal_type': None, 'food': None, 'calories': None,
              'protein': None, 'carbs': None, 'fat': None,
              'fiber': None, 'date': None, 'time': None,
              'notes': None, 'amount': None, 'unit': 'g'}

    # 食事タイプ
    type_match = re.search(r'(?:タイプ|type|種類|meal)[：:]\s*(.+)', content, re.IGNORECASE)
    if type_match:
        type_str = type_match.group(1).strip().lower()
        # 英語タイプに変換
        type_map = {
            '朝食': 'breakfast', 'breakfast': 'breakfast',
            '昼食': 'lunch', 'lunch': 'lunch',
            '夕食': 'dinner', 'dinner': 'dinner',
            '間食': 'snack', 'snack': 'snack',
            '夕方': 'evening'
        }
        result['meal_type'] = type_map.get(type_str, type_str)

    # カロリー
    cal_match = re.search(r'(?:カロリー|calorie|cal|kcal)[×:]?\s*(\d+)', content, re.IGNORECASE)
    if cal_match:
        result['calories'] = int(cal_match.group(1))

    # タンパク質
    protein_match = re.search(r'(?:タンパク|protein|プロテイン)[×:]?\s*(\d+(?:\.\d+)?)', content, re.IGNORECASE)
    if protein_match:
        result['protein'] = float(protein_match.group(1))

    # 炭水化物
    carbs_match = re.search(r'(?:炭水化物|carbs|carbohydrate)[×:]?\s*(\d+(?:\.\d+)?)', content, re.IGNORECASE)
    if carbs_match:
        result['carbs'] = float(carbs_match.group(1))

    # 脂質
    fat_match = re.search(r'(?:脂質|fat)[×:]?\s*(\d+(?:\.\d+)?)', content, re.IGNORECASE)
    if fat_match:
        result['fat'] = float(fat_match.group(1))

    # 食物繊維
    fiber_match = re.search(r'(?:食物繊維|fiber|fibre)[×:]?\s*(\d+(?:\.\d+)?)', content, re.IGNORECASE)
    if fiber_match:
        result['fiber'] = float(fiber_match.group(1))

    # 量
    amount_match = re.search(r'(?:量|amount)[×:]?\s*(\d+(?:\.\d+)?)', content, re.IGNORECASE)
    if amount_match:
        result['amount'] = float(amount_match.group(1))

    # 単位
    unit_match = re.search(r'(?:単位|unit)[×:]?\s*(g|kg|ml|l|cup)', content, re.IGNORECASE)
    if unit_match:
        result['unit'] = unit_match.group(1).lower()

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

    # 最初の項目より前を食品とする
    for key in ['タイプ', 'type', '種類', 'meal', 'カロリー', 'calorie', 'cal', 'タンパク', 'protein']:
        match = re.search(rf'{key}[×:：]', content)
        if match:
            result['food'] = content[:match.start()].strip()
            break
    else:
        result['food'] = content.strip()

    return result

def parse_goal_content(content):
    """目標内容を解析"""
    result = {'date': None, 'calories': None, 'protein': None, 'carbs': None, 'fat': None}

    # 日付
    date_match = re.search(r'(?:日付|date)[：:]\s*([^、,]+)', content, re.IGNORECASE)
    if date_match:
        result['date'] = parse_date(date_match.group(1).strip())
    else:
        result['date'] = datetime.now().strftime("%Y-%m-%d")

    # カロリー
    cal_match = re.search(r'(?:カロリー|calorie|cal|kcal)[×:]?\s*(\d+)', content, re.IGNORECASE)
    if cal_match:
        result['calories'] = int(cal_match.group(1))

    # タンパク質
    protein_match = re.search(r'(?:タンパク|protein|プロテイン)[×:]?\s*(\d+(?:\.\d+)?)', content, re.IGNORECASE)
    if protein_match:
        result['protein'] = float(protein_match.group(1))

    # 炭水化物
    carbs_match = re.search(r'(?:炭水化物|carbs|carbohydrate)[×:]?\s*(\d+(?:\.\d+)?)', content, re.IGNORECASE)
    if carbs_match:
        result['carbs'] = float(carbs_match.group(1))

    # 脂質
    fat_match = re.search(r'(?:脂質|fat)[×:]?\s*(\d+(?:\.\d+)?)', content, re.IGNORECASE)
    if fat_match:
        result['fat'] = float(fat_match.group(1))

    return result

def parse_update_content(content):
    """更新内容を解析"""
    result = parse_meal_content(content)
    return {k: v for k, v in result.items() if v is not None}

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
        content = parse_meal_content(parsed['content'])

        if not content['food']:
            return "❌ 食品を入力してください"

        meal_id = add_meal(
            meal_type=content['meal_type'],
            food=content['food'],
            calories=content['calories'],
            protein=content['protein'],
            carbs=content['carbs'],
            fat=content['fat'],
            fiber=content['fiber'],
            date=content['date'],
            time=content['time'],
            notes=content['notes'],
            amount=content['amount'],
            unit=content['unit']
        )

        response = f"🍽️ 食事 #{meal_id} 追加完了\n"
        response += f"食品: {content['food']}\n"
        if content['meal_type']:
            type_text = {
                'breakfast': '朝食',
                'lunch': '昼食',
                'dinner': '夕食',
                'snack': '間食'
            }.get(content['meal_type'], content['meal_type'])
            response += f"タイプ: {type_text}\n"
        if content['calories']:
            response += f"カロリー: {content['calories']}kcal\n"
        if content['protein']:
            response += f"タンパク質: {content['protein']}g\n"
        if content['carbs']:
            response += f"炭水化物: {content['carbs']}g\n"
        if content['fat']:
            response += f"脂質: {content['fat']}g"
        if content['date']:
            response += f"\n日付: {content['date']}"

        return response

    elif action == 'update':
        updates = parse_update_content(parsed['content'])

        if not updates:
            return "❌ 更新内容がありません"

        update_meal(parsed['meal_id'], **updates)

        response = f"✅ 食事 #{parsed['meal_id']} 更新完了"

        return response

    elif action == 'delete':
        delete_meal(parsed['meal_id'])
        return f"🗑️ 食事 #{parsed['meal_id']} 削除完了"

    elif action == 'search':
        keyword = parsed['keyword']
        meals = search_meals(keyword)

        if not meals:
            return f"🔍 「{keyword}」の検索結果: 見つかりませんでした"

        response = f"🔍 「{keyword}」の検索結果 ({len(meals)}件):\n"
        for meal in meals:
            response += format_meal(meal)

        return response

    elif action == 'set_goal':
        content = parse_goal_content(parsed['content'])

        set_goal(
            date=content['date'],
            calories=content['calories'],
            protein=content['protein'],
            carbs=content['carbs'],
            fat=content['fat']
        )

        response = f"🎯 目標設定完了\n"
        response += f"日付: {content['date']}\n"
        if content['calories']:
            response += f"カロリー: {content['calories']}kcal\n"
        if content['protein']:
            response += f"タンパク質: {content['protein']}g\n"
        if content['carbs']:
            response += f"炭水化物: {content['carbs']}g\n"
        if content['fat']:
            response += f"脂質: {content['fat']}g"

        return response

    elif action == 'list':
        meals = list_meals()

        if not meals:
            return "🍽️ 食事記録がありません"

        response = f"🍽️ 食事一覧 ({len(meals)}件):\n"
        for meal in meals:
            response += format_meal(meal)

        return response

    elif action == 'today':
        date = datetime.now().strftime("%Y-%m-%d")
        meals = get_by_date(date)

        if not meals:
            return f"🍽️ 今日の食事記録はありません"

        response = f"🍽️ 今日の食事 ({len(meals)}件):\n"
        for meal in meals:
            response += format_meal(meal, show_date=False)

        # サマリーを追加
        summary = get_daily_summary(date)
        response += f"\n📊 今日のサマリー:\n"
        response += f"  カロリー: {summary[1]}kcal"
        if summary[2]:
            response += f"\n  タンパク質: {summary[2]}g"
        if summary[3]:
            response += f"\n  炭水化物: {summary[3]}g"
        if summary[4]:
            response += f"\n  脂質: {summary[4]}g"

        return response

    elif action == 'stats':
        stats = get_stats()

        response = "📊 統計情報:\n"
        response += f"総食事数: {stats['total_meals']}回\n"
        response += f"記録日数: {stats['logged_days']}日\n"
        if stats['avg_calories']:
            response += f"平均カロリー: {stats['avg_calories']:.0f}kcal/回\n"
        response += f"今日: {stats['today_meals']}回 ({stats['today_calories']}kcal)"

        if stats['frequent_foods']:
            response += "\n\n🍽️ よく食べる食品:"
            for food, count in stats['frequent_foods'][:5]:
                response += f"\n  • {food} ({count}回)"

        return response

    elif action == 'summary':
        date = datetime.now().strftime("%Y-%m-%d")
        summary = get_daily_summary(date)
        goal = get_goal(date)

        response = f"📊 今日のサマリー ({date}):\n"
        response += f"  カロリー: {summary[1]}kcal"
        if goal and goal[2]:
            response += f" / {goal[2]}kcal ({(summary[1]/goal[2]*100):.0f}%)"

        if summary[2]:
            response += f"\n  タンパク質: {summary[2]}g"
            if goal and goal[3]:
                response += f" / {goal[3]}g"
        if summary[3]:
            response += f"\n  炭水化物: {summary[3]}g"
            if goal and goal[4]:
                response += f" / {goal[4]}g"
        if summary[4]:
            response += f"\n  脂質: {summary[4]}g"
            if goal and goal[5]:
                response += f" / {goal[5]}g"

        if summary[0] == 0:
            response += "\n\n⚠️ 今日の食事が記録されていません"

        return response

    return None

def format_meal(meal, show_date=True):
    """食事をフォーマット"""
    id, meal_type, food, calories, protein, carbs, fat, fiber, date, time, notes, amount, unit, created_at = meal

    type_emoji = {
        'breakfast': '🌅',
        'lunch': '☀️',
        'dinner': '🌙',
        'snack': '🍪',
        'evening': '🌆'
    }

    response = ""
    if show_date:
        emoji = type_emoji.get(meal_type, '🍽️')
        response = f"\n{emoji} [{id}] {date} {time} - {food}\n"
    else:
        emoji = type_emoji.get(meal_type, '🍽️')
        response = f"\n{emoji} [{id}] {time} - {food}\n"

    if amount:
        response += f"    量: {amount}{unit}"

    if calories or protein or carbs or fat:
        response += "\n    栄養素: "
        parts = []
        if calories:
            parts.append(f"{calories}kcal")
        if protein:
            parts.append(f"P:{protein}g")
        if carbs:
            parts.append(f"C:{carbs}g")
        if fat:
            parts.append(f"F:{fat}g")
        if parts:
            response += ' | '.join(parts)

    if meal_type:
        type_text = {
            'breakfast': '朝食',
            'lunch': '昼食',
            'dinner': '夕食',
            'snack': '間食'
        }.get(meal_type, meal_type)
        response += f"\n    タイプ: {type_text}"

    if notes:
        response += f"\n    📝 {notes}"

    return response

if __name__ == '__main__':
    init_db()

    test_messages = [
        "食事: ご飯と味噌汁, タイプ: 朝食, カロリー: 400, タンパク: 15",
        "食事: チキンサラダ, タイプ: 昼食, カロリー: 350, タンパク: 30",
        "目標: カロリー 2000, タンパク 150",
        "サマリー",
    ]

    for msg in test_messages:
        print(f"\n入力: {msg}")
        result = handle_message(msg)
        if result:
            print(result)
