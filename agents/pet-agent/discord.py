#!/usr/bin/env python3
"""
ペットエージェント #39 - Discord連携
"""

import re
from datetime import datetime
from db import *

def parse_message(message):
    """メッセージを解析"""
    # ペット追加
    pet_match = re.match(r'(?:ペット|pet)[：:]\s*(.+)', message, re.IGNORECASE)
    if pet_match:
        return parse_add_pet(pet_match.group(1))

    # 食事追加
    meal_match = re.match(r'(?:食事|meal|餌|feed)[：:]\s*(\d+)\s*(.+)', message, re.IGNORECASE)
    if meal_match:
        parsed = parse_add_meal(meal_match.group(2))
        parsed['pet_id'] = int(meal_match.group(1))
        return parsed

    # 散歩追加
    walk_match = re.match(r'(?:散歩|walk)[：:]\s*(\d+)\s*(.+)', message, re.IGNORECASE)
    if walk_match:
        parsed = parse_add_walk(walk_match.group(2))
        parsed['pet_id'] = int(walk_match.group(1))
        return parsed

    # 健康記録追加
    health_match = re.match(r'(?:健康|health|病院|hospital|診察|checkup)[：:]\s*(\d+)\s*(.+)', message, re.IGNORECASE)
    if health_match:
        parsed = parse_add_health(health_match.group(2))
        parsed['pet_id'] = int(health_match.group(1))
        return parsed

    # 一覧
    list_match = re.match(r'(?:(?:ペット|pet)(?:一覧|list)|list|pets)', message, re.IGNORECASE)
    if list_match:
        return {'action': 'list_pets'}

    # 食事一覧
    meals_match = re.match(r'(?:食事|meal|餌|feed)[：:]\s*(\d+)', message, re.IGNORECASE)
    if meals_match:
        return {'action': 'list_meals', 'pet_id': int(meals_match.group(1))}

    # 散歩一覧
    walks_match = re.match(r'(?:散歩|walk)[：:]\s*(\d+)', message, re.IGNORECASE)
    if walks_match:
        return {'action': 'list_walks', 'pet_id': int(walks_match.group(1))}

    # 健康記録一覧
    health_list_match = re.match(r'(?:健康|health|病院|hospital|診察|checkup)[：:]\s*(\d+)', message, re.IGNORECASE)
    if health_list_match:
        return {'action': 'list_health', 'pet_id': int(health_list_match.group(1))}

    return None

def parse_add_pet(content):
    """ペット追加を解析"""
    result = {'action': 'add_pet', 'name': None, 'species': None, 'breed': None,
              'birth_date': None, 'weight': None, 'gender': None, 'microchip': None, 'notes': None}

    # 名前 (最初の部分)
    name_match = re.match(r'^([^、,（\(【]+)', content)
    if name_match:
        result['name'] = name_match.group(1).strip()

    # 種類
    species_match = re.search(r'(?:種類|species|動物)[：:]\s*([^、,]+)', content)
    if species_match:
        result['species'] = species_match.group(1).strip()

    # 品種
    breed_match = re.search(r'(?:品種|breed)[：:]\s*([^、,]+)', content)
    if breed_match:
        result['breed'] = breed_match.group(1).strip()

    # 誕生日
    birth_match = re.search(r'(?:誕生日|birth|生年月日)[：:]\s*([^、,]+)', content)
    if birth_match:
        result['birth_date'] = parse_date(birth_match.group(1).strip())

    # 体重
    weight_match = re.search(r'(?:体重|weight)[：:]?\s*(\d+(?:\.\d+)?)\s*(kg|g)?', content)
    if weight_match:
        result['weight'] = float(weight_match.group(1))

    # 性別
    gender_match = re.search(r'(?:性別|gender)[：:]\s*(オス|メス|雄|雌|male|female)', content)
    if gender_match:
        gender_map = {
            'オス': 'オス', '雄': 'オス', 'male': 'オス',
            'メス': 'メス', '雌': 'メス', 'female': 'メス'
        }
        result['gender'] = gender_map.get(gender_match.group(1).lower())

    # チップ番号
    chip_match = re.search(r'(?:チップ|microchip|id)[：:]?\s*([^、,]+)', content)
    if chip_match:
        result['microchip'] = chip_match.group(1).strip()

    # メモ
    notes_match = re.search(r'(?:メモ|備考|memo|note)[：:]\s*(.+)', content)
    if notes_match:
        result['notes'] = notes_match.group(1).strip()

    # 名前がまだない場合、最初の項目より前を名前とする
    if not result['name']:
        for key in ['種類', 'species', '動物', '品種', 'breed', '誕生日', 'birth', '生年月日',
                    '体重', 'weight', '性別', 'gender', 'チップ', 'microchip', 'id',
                    'メモ', '備考', 'memo', 'note']:
            match = re.search(rf'{key}[：:]', content)
            if match:
                result['name'] = content[:match.start()].strip()
                break
        else:
            result['name'] = content.strip()

    return result

def parse_add_meal(content):
    """食事追加を解析"""
    result = {'action': 'add_meal', 'date': None, 'food': None, 'amount': None, 'time': None, 'notes': None}

    # 日付
    date_match = re.search(r'(?:日付|date)[：:]\s*([^、,]+)', content)
    if date_match:
        result['date'] = parse_date(date_match.group(1).strip())
    else:
        # デフォルトは今日
        result['date'] = datetime.now().strftime("%Y-%m-%d")

    # 時間
    time_match = re.search(r'(?:時間|time)[：:]?\s*(\d{1,2}:\d{2})', content)
    if time_match:
        result['time'] = time_match.group(1)

    # 餌
    food_match = re.search(r'(?:餌|food|フード)[：:]\s*([^、,]+)', content)
    if food_match:
        result['food'] = food_match.group(1).strip()

    # 量
    amount_match = re.search(r'(?:量|amount)[：:]?\s*(\d+)\s*(g|ml|カップ)?', content)
    if amount_match:
        result['amount'] = f"{amount_match.group(1)}{amount_match.group(2) or 'g'}"

    # メモ
    notes_match = re.search(r'(?:メモ|備考|memo|note)[：:]\s*(.+)', content)
    if notes_match:
        result['notes'] = notes_match.group(1).strip()

    # 餌がない場合、最初の項目より前を餌とする
    if not result['food']:
        for key in ['日付', 'date', '時間', 'time', '餌', 'food', 'フード', '量', 'amount',
                    'メモ', '備考', 'memo', 'note']:
            match = re.search(rf'{key}[：:]', content)
            if match:
                result['food'] = content[:match.start()].strip()
                break
        else:
            result['food'] = content.strip()

    return result

def parse_add_walk(content):
    """散歩追加を解析"""
    result = {'action': 'add_walk', 'date': None, 'duration': None, 'distance': None, 'time': None, 'notes': None}

    # 日付
    date_match = re.search(r'(?:日付|date)[：:]\s*([^、,]+)', content)
    if date_match:
        result['date'] = parse_date(date_match.group(1).strip())
    else:
        # デフォルトは今日
        result['date'] = datetime.now().strftime("%Y-%m-%d")

    # 時間
    time_match = re.search(r'(?:時間|time)[：:]?\s*(\d{1,2}:\d{2})', content)
    if time_match:
        result['time'] = time_match.group(1)

    # 時間（長さ）
    duration_match = re.search(r'(?:長さ|duration|時間h?|hour|min|分)[：:]?\s*(\d+)\s*(時間|h|hour|分|min)?', content)
    if duration_match:
        result['duration'] = int(duration_match.group(1))
        if duration_match.group(2) and '時間' in duration_match.group(2):
            result['duration'] *= 60  # 時間を分に変換

    # 距離
    distance_match = re.search(r'(?:距離|distance)[：:]?\s*(\d+(?:\.\d+)?)\s*(km|m)?', content)
    if distance_match:
        result['distance'] = float(distance_match.group(1))
        if distance_match.group(2) == 'km':
            result['distance'] *= 1000  # kmをmに変換

    # メモ
    notes_match = re.search(r'(?:メモ|備考|memo|note)[：:]\s*(.+)', content)
    if notes_match:
        result['notes'] = notes_match.group(1).strip()

    return result

def parse_add_health(content):
    """健康記録追加を解析"""
    result = {'action': 'add_health', 'date': None, 'type': None, 'description': None, 'vet': None, 'notes': None}

    # 日付
    date_match = re.search(r'(?:日付|date)[：:]\s*([^、,]+)', content)
    if date_match:
        result['date'] = parse_date(date_match.group(1).strip())
    else:
        # デフォルトは今日
        result['date'] = datetime.now().strftime("%Y-%m-%d")

    # タイプ
    type_match = re.search(r'(?:種類|type|タイプ)[：:]\s*([^、,]+)', content)
    if type_match:
        result['type'] = type_match.group(1).strip()

    # 説明
    description_match = re.search(r'(?:説明|description|内容|desc)[：:]\s*(.+)', content)
    if description_match:
        result['description'] = description_match.group(1).strip()

    # 獣医
    vet_match = re.search(r'(?:獣医|vet|動物病院|hospital)[：:]\s*([^、,]+)', content)
    if vet_match:
        result['vet'] = vet_match.group(1).strip()

    # メモ
    notes_match = re.search(r'(?:メモ|備考|memo|note)[：:]\s*(.+)', content)
    if notes_match:
        result['notes'] = notes_match.group(1).strip()

    # タイプがない場合、最初の項目より前をタイプとする
    if not result['type']:
        for key in ['日付', 'date', '種類', 'type', 'タイプ', '説明', 'description', '内容', 'desc',
                    '獣医', 'vet', '動物病院', 'hospital', 'メモ', '備考', 'memo', 'note']:
            match = re.search(rf'{key}[：:]', content)
            if match:
                result['type'] = content[:match.start()].strip()
                break
        else:
            result['type'] = content.strip()

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

    if action == 'add_pet':
        if not parsed['name']:
            return "❌ 名前を入力してください"

        pet_id = add_pet(
            parsed['name'],
            parsed['species'],
            parsed['breed'],
            parsed['birth_date'],
            parsed['weight'],
            parsed['gender'],
            parsed['microchip'],
            parsed['notes']
        )

        response = f"🐾 ペット #{pet_id} 追加完了\n"
        response += f"名前: {parsed['name']}\n"
        if parsed['species']:
            response += f"種類: {parsed['species']}\n"
        if parsed['breed']:
            response += f"品種: {parsed['breed']}\n"
        if parsed['birth_date']:
            response += f"誕生日: {parsed['birth_date']}\n"
        if parsed['weight']:
            response += f"体重: {parsed['weight']}kg\n"
        if parsed['gender']:
            response += f"性別: {parsed['gender']}\n"
        if parsed['microchip']:
            response += f"チップ番号: {parsed['microchip']}\n"
        if parsed['notes']:
            response += f"メモ: {parsed['notes']}"

        return response

    elif action == 'add_meal':
        meal_id = add_meal(
            parsed['pet_id'],
            parsed['date'],
            parsed['food'],
            parsed['amount'],
            parsed['time'],
            parsed['notes']
        )

        pet = get_pet(parsed['pet_id'])
        pet_name = pet[1] if pet else f"ID {parsed['pet_id']}"

        response = f"🍽️ 食事 #{meal_id} 追加完了\n"
        response += f"ペット: {pet_name}\n"
        response += f"日付: {parsed['date']}\n"
        if parsed['time']:
            response += f"時間: {parsed['time']}\n"
        if parsed['food']:
            response += f"餌: {parsed['food']}\n"
        if parsed['amount']:
            response += f"量: {parsed['amount']}\n"
        if parsed['notes']:
            response += f"メモ: {parsed['notes']}"

        return response

    elif action == 'add_walk':
        walk_id = add_walk(
            parsed['pet_id'],
            parsed['date'],
            parsed['duration'],
            parsed['distance'],
            parsed['time'],
            parsed['notes']
        )

        pet = get_pet(parsed['pet_id'])
        pet_name = pet[1] if pet else f"ID {parsed['pet_id']}"

        response = f"🚶 散歩 #{walk_id} 追加完了\n"
        response += f"ペット: {pet_name}\n"
        response += f"日付: {parsed['date']}\n"
        if parsed['time']:
            response += f"時間: {parsed['time']}\n"
        if parsed['duration']:
            response += f"長さ: {parsed['duration']}分\n"
        if parsed['distance']:
            response += f"距離: {parsed['distance']}m\n"
        if parsed['notes']:
            response += f"メモ: {parsed['notes']}"

        return response

    elif action == 'add_health':
        if not parsed['type']:
            return "❌ 種類を入力してください"

        health_id = add_health(
            parsed['pet_id'],
            parsed['date'],
            parsed['type'],
            parsed['description'],
            parsed['vet'],
            parsed['notes']
        )

        pet = get_pet(parsed['pet_id'])
        pet_name = pet[1] if pet else f"ID {parsed['pet_id']}"

        response = f"🏥 健康記録 #{health_id} 追加完了\n"
        response += f"ペット: {pet_name}\n"
        response += f"日付: {parsed['date']}\n"
        response += f"種類: {parsed['type']}\n"
        if parsed['description']:
            response += f"説明: {parsed['description']}\n"
        if parsed['vet']:
            response += f"獣医: {parsed['vet']}\n"
        if parsed['notes']:
            response += f"メモ: {parsed['notes']}"

        return response

    elif action == 'list_pets':
        pets = list_pets()

        if not pets:
            return "🐾 ペットがいません"

        response = f"🐾 ペット一覧 ({len(pets)}件):\n"
        for pet in pets:
            response += format_pet(pet)

        return response

    elif action == 'list_meals':
        meals = list_meals(parsed['pet_id'])

        pet = get_pet(parsed['pet_id'])
        pet_name = pet[1] if pet else f"ID {parsed['pet_id']}"

        if not meals:
            return f"🍽️ {pet_name}の食事記録がありません"

        response = f"🍽️ {pet_name}の食事記録 ({len(meals)}件):\n"
        for meal in meals:
            response += format_meal(meal)

        return response

    elif action == 'list_walks':
        walks = list_walks(parsed['pet_id'])

        pet = get_pet(parsed['pet_id'])
        pet_name = pet[1] if pet else f"ID {parsed['pet_id']}"

        if not walks:
            return f"🚶 {pet_name}の散歩記録がありません"

        response = f"🚶 {pet_name}の散歩記録 ({len(walks)}件):\n"
        for walk in walks:
            response += format_walk(walk)

        return response

    elif action == 'list_health':
        health_records = list_health(parsed['pet_id'])

        pet = get_pet(parsed['pet_id'])
        pet_name = pet[1] if pet else f"ID {parsed['pet_id']}"

        if not health_records:
            return f"🏥 {pet_name}の健康記録がありません"

        response = f"🏥 {pet_name}の健康記録 ({len(health_records)}件):\n"
        for record in health_records:
            response += format_health(record)

        return response

    return None

def format_pet(pet):
    """ペットをフォーマット"""
    id, name, species, breed, birth_date, weight, gender, microchip, notes, created_at = pet

    response = f"\n[{id}] {name}"
    if species:
        response += f" ({species})"
    response += "\n"

    parts = []
    if breed:
        parts.append(f"🐶 {breed}")
    if gender:
        parts.append(f"🚻 {gender}")
    if weight:
        parts.append(f"⚖️ {weight}kg")

    if parts:
        response += f"    {' '.join(parts)}\n"

    return response

def format_meal(meal):
    """食事をフォーマット"""
    id, pet_id, date, time, food, amount, notes, created_at = meal

    response = f"\n📅 [{id}] {date}"
    if time:
        response += f" {time}"
    response += f"\n    🍽️ {food or '記録なし'}"

    if amount:
        response += f" ({amount})"

    response += "\n"

    return response

def format_walk(walk):
    """散歩をフォーマット"""
    id, pet_id, date, time, duration, distance, notes, created_at = walk

    response = f"\n📅 [{id}] {date}"
    if time:
        response += f" {time}"
    response += "\n"

    parts = []
    if duration:
        hours = duration // 60
        mins = duration % 60
        if hours > 0:
            parts.append(f"⏱️ {hours}時間{mins}分")
        else:
            parts.append(f"⏱️ {mins}分")
    if distance:
        parts.append(f"📏 {distance}m")

    if parts:
        response += f"    {' '.join(parts)}\n"

    return response

def format_health(record):
    """健康記録をフォーマット"""
    id, pet_id, date, type, description, vet, notes, created_at = record

    response = f"\n📅 [{id}] {date} - {type}\n"

    if description:
        response += f"    📝 {description[:100]}{'...' if len(description) > 100 else ''}\n"
    if vet:
        response += f"    🏥 {vet}\n"

    return response

if __name__ == '__main__':
    # テスト
    init_db()

    test_messages = [
        "ペット: ポチ, 種類: 犬, 品種: 柴犬",
        "食事: 1 ドッグフード, 量: 200g",
        "散歩: 1, 長さ: 30分, 距離: 1000m",
        "ペット一覧",
    ]

    for msg in test_messages:
        print(f"\n入力: {msg}")
        result = handle_message(msg)
        if result:
            print(result)
