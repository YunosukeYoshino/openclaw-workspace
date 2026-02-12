#!/usr/bin/env python3
"""
植物エージェント #40 - Discord連携
"""

import re
from datetime import datetime
from db import *

def parse_message(message):
    """メッセージを解析"""
    # 植物追加
    plant_match = re.match(r'(?:植物|plant)[：:]\s*(.+)', message, re.IGNORECASE)
    if plant_match:
        return parse_add_plant(plant_match.group(1))

    # 水やり追加
    water_match = re.match(r'(?:水やり|water|watering)[：:]\s*(\d+)\s*(.+)', message, re.IGNORECASE)
    if water_match:
        parsed = parse_add_watering(water_match.group(2))
        parsed['plant_id'] = int(water_match.group(1))
        return parsed

    # 肥料追加
    fertilizer_match = re.match(r'(?:肥料|fertilizer|fert)[：:]\s*(\d+)\s*(.+)', message, re.IGNORECASE)
    if fertilizer_match:
        parsed = parse_add_fertilization(fertilizer_match.group(2))
        parsed['plant_id'] = int(fertilizer_match.group(1))
        return parsed

    # 健康記録追加
    health_match = re.match(r'(?:健康|health|状態|status)[：:]\s*(\d+)\s*(.+)', message, re.IGNORECASE)
    if health_match:
        parsed = parse_add_health(health_match.group(2))
        parsed['plant_id'] = int(health_match.group(1))
        return parsed

    # 一覧
    list_match = re.match(r'(?:(?:植物|plant)(?:一覧|list)|list|plants)', message, re.IGNORECASE)
    if list_match:
        return {'action': 'list_plants'}

    # 水やり一覧
    water_list_match = re.match(r'(?:水やり|water|watering)[：:]\s*(\d+)', message, re.IGNORECASE)
    if water_list_match:
        return {'action': 'list_waterings', 'plant_id': int(water_list_match.group(1))}

    # 肥料一覧
    fertilizer_list_match = re.match(r'(?:肥料|fertilizer|fert)[：:]\s*(\d+)', message, re.IGNORECASE)
    if fertilizer_list_match:
        return {'action': 'list_fertilizations', 'plant_id': int(fertilizer_list_match.group(1))}

    # 健康記録一覧
    health_list_match = re.match(r'(?:健康|health|状態|status)[：:]\s*(\d+)', message, re.IGNORECASE)
    if health_list_match:
        return {'action': 'list_health_records', 'plant_id': int(health_list_match.group(1))}

    return None

def parse_add_plant(content):
    """植物追加を解析"""
    result = {'action': 'add_plant', 'name': None, 'species': None, 'location': None,
              'acquired_date': None, 'notes': None}

    # 名前 (最初の部分)
    name_match = re.match(r'^([^、,（\(【]+)', content)
    if name_match:
        result['name'] = name_match.group(1).strip()

    # 種類
    species_match = re.search(r'(?:種類|species|品種)[：:]\s*([^、,]+)', content)
    if species_match:
        result['species'] = species_match.group(1).strip()

    # 場所
    location_match = re.search(r'(?:場所|location|置き場所)[：:]\s*([^、,]+)', content)
    if location_match:
        result['location'] = location_match.group(1).strip()

    # 入手日
    acquired_match = re.search(r'(?:入手日|acquired|購入日|got)[：:]\s*([^、,]+)', content)
    if acquired_match:
        result['acquired_date'] = parse_date(acquired_match.group(1).strip())

    # メモ
    notes_match = re.search(r'(?:メモ|備考|memo|note)[：:]\s*(.+)', content)
    if notes_match:
        result['notes'] = notes_match.group(1).strip()

    # 名前がまだない場合、最初の項目より前を名前とする
    if not result['name']:
        for key in ['種類', 'species', '品種', '場所', 'location', '置き場所',
                    '入手日', 'acquired', '購入日', 'got', 'メモ', '備考', 'memo', 'note']:
            match = re.search(rf'{key}[：:]', content)
            if match:
                result['name'] = content[:match.start()].strip()
                break
        else:
            result['name'] = content.strip()

    return result

def parse_add_watering(content):
    """水やり追加を解析"""
    result = {'action': 'add_watering', 'date': None, 'amount': None, 'time': None, 'notes': None}

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

    # 量
    amount_match = re.search(r'(?:量|amount)[：:]?\s*(\d+)\s*(ml|L|カップ|cup)?', content)
    if amount_match:
        result['amount'] = f"{amount_match.group(1)}{amount_match.group(2) or 'ml'}"

    # メモ
    notes_match = re.search(r'(?:メモ|備考|memo|note)[：:]\s*(.+)', content)
    if notes_match:
        result['notes'] = notes_match.group(1).strip()

    return result

def parse_add_fertilization(content):
    """肥料追加を解析"""
    result = {'action': 'add_fertilization', 'date': None, 'fertilizer': None, 'amount': None, 'notes': None}

    # 日付
    date_match = re.search(r'(?:日付|date)[：:]\s*([^、,]+)', content)
    if date_match:
        result['date'] = parse_date(date_match.group(1).strip())
    else:
        # デフォルトは今日
        result['date'] = datetime.now().strftime("%Y-%m-%d")

    # 肥料
    fertilizer_match = re.search(r'(?:肥料|fertilizer|fert|種類)[：:]\s*([^、,]+)', content)
    if fertilizer_match:
        result['fertilizer'] = fertilizer_match.group(1).strip()

    # 量
    amount_match = re.search(r'(?:量|amount)[：:]?\s*(\d+)\s*(g|mg|ml|カップ|cup)?', content)
    if amount_match:
        result['amount'] = f"{amount_match.group(1)}{amount_match.group(2) or 'g'}"

    # メモ
    notes_match = re.search(r'(?:メモ|備考|memo|note)[：:]\s*(.+)', content)
    if notes_match:
        result['notes'] = notes_match.group(1).strip()

    return result

def parse_add_health(content):
    """健康記録追加を解析"""
    result = {'action': 'add_health', 'date': None, 'status': None, 'description': None, 'notes': None}

    # 日付
    date_match = re.search(r'(?:日付|date)[：:]\s*([^、,]+)', content)
    if date_match:
        result['date'] = parse_date(date_match.group(1).strip())
    else:
        # デフォルトは今日
        result['date'] = datetime.now().strftime("%Y-%m-%d")

    # 状態
    status_match = re.search(r'(?:状態|status|健康状態)[：:]\s*([^、,]+)', content)
    if status_match:
        result['status'] = status_match.group(1).strip()

    # 説明
    description_match = re.search(r'(?:説明|description|内容|desc)[：:]\s*(.+)', content)
    if description_match:
        result['description'] = description_match.group(1).strip()

    # メモ
    notes_match = re.search(r'(?:メモ|備考|memo|note)[：:]\s*(.+)', content)
    if notes_match:
        result['notes'] = notes_match.group(1).strip()

    # 状態がない場合、最初の項目より前を状態とする
    if not result['status']:
        for key in ['日付', 'date', '状態', 'status', '健康状態', '説明', 'description', '内容', 'desc',
                    'メモ', '備考', 'memo', 'note']:
            match = re.search(rf'{key}[：:]', content)
            if match:
                result['status'] = content[:match.start()].strip()
                break
        else:
            result['status'] = content.strip()

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

    if action == 'add_plant':
        if not parsed['name']:
            return "❌ 名前を入力してください"

        plant_id = add_plant(
            parsed['name'],
            parsed['species'],
            parsed['location'],
            parsed['acquired_date'],
            parsed['notes']
        )

        response = f"🌱 植物 #{plant_id} 追加完了\n"
        response += f"名前: {parsed['name']}\n"
        if parsed['species']:
            response += f"種類: {parsed['species']}\n"
        if parsed['location']:
            response += f"場所: {parsed['location']}\n"
        if parsed['acquired_date']:
            response += f"入手日: {parsed['acquired_date']}\n"
        if parsed['notes']:
            response += f"メモ: {parsed['notes']}"

        return response

    elif action == 'add_watering':
        watering_id = add_watering(
            parsed['plant_id'],
            parsed['date'],
            parsed['amount'],
            parsed['time'],
            parsed['notes']
        )

        plant = get_plant(parsed['plant_id'])
        plant_name = plant[1] if plant else f"ID {parsed['plant_id']}"

        response = f"💧 水やり #{watering_id} 追加完了\n"
        response += f"植物: {plant_name}\n"
        response += f"日付: {parsed['date']}\n"
        if parsed['time']:
            response += f"時間: {parsed['time']}\n"
        if parsed['amount']:
            response += f"量: {parsed['amount']}\n"
        if parsed['notes']:
            response += f"メモ: {parsed['notes']}"

        return response

    elif action == 'add_fertilization':
        fertilization_id = add_fertilization(
            parsed['plant_id'],
            parsed['date'],
            parsed['fertilizer'],
            parsed['amount'],
            parsed['notes']
        )

        plant = get_plant(parsed['plant_id'])
        plant_name = plant[1] if plant else f"ID {parsed['plant_id']}"

        response = f"🧪 肥料 #{fertilization_id} 追加完了\n"
        response += f"植物: {plant_name}\n"
        response += f"日付: {parsed['date']}\n"
        if parsed['fertilizer']:
            response += f"肥料: {parsed['fertilizer']}\n"
        if parsed['amount']:
            response += f"量: {parsed['amount']}\n"
        if parsed['notes']:
            response += f"メモ: {parsed['notes']}"

        return response

    elif action == 'add_health':
        if not parsed['status']:
            return "❌ 状態を入力してください"

        health_id = add_health_record(
            parsed['plant_id'],
            parsed['date'],
            parsed['status'],
            parsed['description'],
            parsed['notes']
        )

        plant = get_plant(parsed['plant_id'])
        plant_name = plant[1] if plant else f"ID {parsed['plant_id']}"

        response = f"🌿 健康記録 #{health_id} 追加完了\n"
        response += f"植物: {plant_name}\n"
        response += f"日付: {parsed['date']}\n"
        response += f"状態: {parsed['status']}\n"
        if parsed['description']:
            response += f"説明: {parsed['description']}\n"
        if parsed['notes']:
            response += f"メモ: {parsed['notes']}"

        return response

    elif action == 'list_plants':
        plants = list_plants()

        if not plants:
            return "🌱 植物がいません"

        response = f"🌱 植物一覧 ({len(plants)}件):\n"
        for plant in plants:
            response += format_plant(plant)

        return response

    elif action == 'list_waterings':
        waterings = list_waterings(parsed['plant_id'])

        plant = get_plant(parsed['plant_id'])
        plant_name = plant[1] if plant else f"ID {parsed['plant_id']}"

        if not waterings:
            return f"💧 {plant_name}の水やり記録がありません"

        response = f"💧 {plant_name}の水やり記録 ({len(waterings)}件):\n"
        for watering in waterings:
            response += format_watering(watering)

        return response

    elif action == 'list_fertilizations':
        fertilizations = list_fertilizations(parsed['plant_id'])

        plant = get_plant(parsed['plant_id'])
        plant_name = plant[1] if plant else f"ID {parsed['plant_id']}"

        if not fertilizations:
            return f"🧪 {plant_name}の肥料記録がありません"

        response = f"🧪 {plant_name}の肥料記録 ({len(fertilizations)}件):\n"
        for fertilization in fertilizations:
            response += format_fertilization(fertilization)

        return response

    elif action == 'list_health_records':
        health_records = list_health_records(parsed['plant_id'])

        plant = get_plant(parsed['plant_id'])
        plant_name = plant[1] if plant else f"ID {parsed['plant_id']}"

        if not health_records:
            return f"🌿 {plant_name}の健康記録がありません"

        response = f"🌿 {plant_name}の健康記録 ({len(health_records)}件):\n"
        for record in health_records:
            response += format_health_record(record)

        return response

    return None

def format_plant(plant):
    """植物をフォーマット"""
    id, name, species, location, acquired_date, notes, created_at = plant

    response = f"\n[{id}] {name}"
    if species:
        response += f" ({species})"
    response += "\n"

    parts = []
    if location:
        parts.append(f"📍 {location}")
    if acquired_date:
        parts.append(f"📅 入手: {acquired_date}")

    if parts:
        response += f"    {' '.join(parts)}\n"

    return response

def format_watering(watering):
    """水やりをフォーマット"""
    id, plant_id, date, time, amount, notes, created_at = watering

    response = f"\n📅 [{id}] {date}"
    if time:
        response += f" {time}"
    response += "\n"

    if amount:
        response += f"    💧 {amount}\n"

    return response

def format_fertilization(fertilization):
    """肥料をフォーマット"""
    id, plant_id, date, fertilizer, amount, notes, created_at = fertilization

    response = f"\n📅 [{id}] {date}\n"

    parts = []
    if fertilizer:
        parts.append(f"🧪 {fertilizer}")
    if amount:
        parts.append(f"量: {amount}")

    if parts:
        response += f"    {' '.join(parts)}\n"

    return response

def format_health_record(record):
    """健康記録をフォーマット"""
    id, plant_id, date, status, description, notes, created_at = record

    response = f"\n📅 [{id}] {date} - {status}\n"

    if description:
        response += f"    📝 {description[:100]}{'...' if len(description) > 100 else ''}\n"

    return response

if __name__ == '__main__':
    # テスト
    init_db()

    test_messages = [
        "植物: サボテン, 種類: 多肉植物, 場所: 窓辺",
        "水やり: 1, 量: 100ml",
        "肥料: 1, 肥料: 液体肥料, 量: 10ml",
        "健康: 1, 状態: 順調",
        "植物一覧",
    ]

    for msg in test_messages:
        print(f"\n入力: {msg}")
        result = handle_message(msg)
        if result:
            print(result)
