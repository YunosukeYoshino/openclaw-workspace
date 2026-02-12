#!/usr/bin/env python3
"""
水分摂取エージェント #50 - Discord連携
"""

import re
from datetime import datetime, timedelta
from db import *

def parse_message(message):
    """メッセージを解析"""
    # 追加
    add_match = re.match(r'(?:水|water|水飲んだ|drank)[：:]\s*(.+)', message, re.IGNORECASE)
    if add_match:
        return {'action': 'add', 'content': add_match.group(1)}

    # 更新
    update_match = re.match(r'(?:更新|update)[：:]\s*(\d+)\s*(.+)', message, re.IGNORECASE)
    if update_match:
        return {'action': 'update', 'hydration_id': int(update_match.group(1)), 'content': update_match.group(2)}

    # 削除
    delete_match = re.match(r'(?:削除|delete|remove)[：:]\s*(\d+)', message, re.IGNORECASE)
    if delete_match:
        return {'action': 'delete', 'hydration_id': int(delete_match.group(1))}

    # 目標設定
    goal_match = re.match(r'(?:目標|goal)[：:]\s*(.+)', message, re.IGNORECASE)
    if goal_match:
        return {'action': 'set_goal', 'content': goal_match.group(1)}

    # 一覧
    if message.strip() in ['水', 'water', '水分', 'hydration', '水分記録']:
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

    # タイプ一覧
    if message.strip() in ['タイプ', 'types', 'drink types']:
        return {'action': 'types'}

    return None

def parse_hydration_content(content):
    """水分摂取内容を解析"""
    result = {'amount': None, 'unit': 'ml', 'time_taken': None,
              'date': None, 'notes': None, 'drink_type': None}

    # 量
    amount_match = re.search(r'(?:量|amount|ml|l|liter)[×:]?\s*(\d+(?:\.\d+)?)', content, re.IGNORECASE)
    if amount_match:
        result['amount'] = float(amount_match.group(1))

    # 単位
    unit_match = re.search(r'(?:単位|unit)[×:]?\s*(ml|l|liter|oz|cup)', content, re.IGNORECASE)
    if unit_match:
        result['unit'] = unit_match.group(1).lower()

    # 飲み物タイプ
    type_match = re.search(r'(?:タイプ|type|種類|drink)[：:]\s*(.+)', content, re.IGNORECASE)
    if type_match:
        result['drink_type'] = type_match.group(1).strip()

    # 時間
    time_match = re.search(r'(?:時間|time)[：:]\s*(\d{1,2}:\d{2})', content, re.IGNORECASE)
    if time_match:
        result['time_taken'] = time_match.group(1).strip()

    # 日付
    date_match = re.search(r'(?:日付|date)[：:]\s*([^、,]+)', content, re.IGNORECASE)
    if date_match:
        result['date'] = parse_date(date_match.group(1).strip())

    # メモ
    notes_match = re.search(r'(?:メモ|memo|note)[：:]\s*(.+)', content, re.IGNORECASE)
    if notes_match:
        result['notes'] = notes_match.group(1).strip()

    # 最初の項目より前を量とする
    for key in ['量', 'amount', 'タイプ', 'type', '種類', 'drink']:
        match = re.search(rf'{key}[×:：]', content)
        if match:
            amount_str = content[:match.start()].strip()
            # 数値を抽出
            num_match = re.search(r'(\d+(?:\.\d+)?)', amount_str)
            if num_match:
                result['amount'] = float(num_match.group(1))
            break

    return result

def parse_goal_content(content):
    """目標内容を解析"""
    result = {'date': None, 'goal_amount': None, 'unit': 'ml'}

    # 日付
    date_match = re.search(r'(?:日付|date)[：:]\s*([^、,]+)', content, re.IGNORECASE)
    if date_match:
        result['date'] = parse_date(date_match.group(1).strip())
    else:
        result['date'] = datetime.now().strftime("%Y-%m-%d")

    # 目標量
    amount_match = re.search(r'(?:目標|goal|量)[×:]?\s*(\d+(?:\.\d+)?)', content, re.IGNORECASE)
    if amount_match:
        result['goal_amount'] = float(amount_match.group(1))

    # 単位
    unit_match = re.search(r'(?:単位|unit)[×:]?\s*(ml|l|liter|oz|cup)', content, re.IGNORECASE)
    if unit_match:
        result['unit'] = unit_match.group(1).lower()

    return result

def parse_update_content(content):
    """更新内容を解析"""
    result = parse_hydration_content(content)
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
        content = parse_hydration_content(parsed['content'])

        if content['amount'] is None:
            return "❌ 水分量を入力してください"

        hydration_id = add_hydration(
            amount=content['amount'],
            unit=content['unit'],
            time_taken=content['time_taken'],
            date=content['date'],
            notes=content['notes'],
            drink_type=content['drink_type']
        )

        response = f"💧 水分摂取 #{hydration_id} 記録完了\n"
        response += f"量: {content['amount']}{content['unit']}\n"
        if content['drink_type']:
            response += f"タイプ: {content['drink_type']}\n"
        if content['time_taken']:
            response += f"時間: {content['time_taken']}\n"
        if content['date']:
            response += f"日付: {content['date']}"

        return response

    elif action == 'update':
        updates = parse_update_content(parsed['content'])

        if not updates:
            return "❌ 更新内容がありません"

        update_hydration(parsed['hydration_id'], **updates)

        response = f"✅ 水分摂取 #{parsed['hydration_id']} 更新完了"

        return response

    elif action == 'delete':
        delete_hydration(parsed['hydration_id'])
        return f"🗑️ 水分摂取 #{parsed['hydration_id']} 削除完了"

    elif action == 'set_goal':
        content = parse_goal_content(parsed['content'])

        if content['goal_amount'] is None:
            return "❌ 目標量を入力してください"

        set_goal(
            date=content['date'],
            goal_amount=content['goal_amount'],
            unit=content['unit']
        )

        response = f"🎯 目標設定完了\n"
        response += f"日付: {content['date']}\n"
        response += f"目標量: {content['goal_amount']}{content['unit']}"

        return response

    elif action == 'list':
        hydration = list_hydration()

        if not hydration:
            return "💧 水分摂取記録がありません"

        response = f"💧 水分摂取記録 ({len(hydration)}件):\n"
        for h in hydration:
            response += format_hydration(h)

        return response

    elif action == 'types':
        types = get_drink_types()

        if not types:
            return "📋 飲み物タイプがありません"

        response = "📋 飲み物タイプ一覧:\n"
        for drink_type, count in types:
            response += f"  • {drink_type} ({count}回)\n"

        return response

    elif action == 'today':
        date = datetime.now().strftime("%Y-%m-%d")
        hydration = get_by_date(date)

        if not hydration:
            return f"💧 今日の水分摂取記録はありません"

        response = f"💧 今日の水分摂取 ({len(hydration)}件):\n"
        for h in hydration:
            response += format_hydration(h, show_date=False)

        # サマリーを追加
        summary = get_daily_summary(date)
        goal = get_goal(date)
        response += f"\n📊 今日のサマリー:\n"
        response += f"  摂取量: {summary[1]}ml"
        if goal and goal[2]:
            response += f" / {goal[2]}{goal[3]} ({(summary[1]/goal[2]*100):.0f}%)"

        return response

    elif action == 'stats':
        stats = get_stats()

        response = "📊 統計情報:\n"
        response += f"総摂取回数: {stats['total_drinks']}回\n"
        response += f"総摂取量: {stats['total_amount']}ml\n"
        if stats['avg_amount']:
            response += f"平均摂取量: {stats['avg_amount']:.0f}ml/回\n"
        response += f"記録日数: {stats['logged_days']}日\n"
        response += f"今日: {stats['today_drinks']}回 ({stats['today_amount']}ml)"

        if stats['drink_types']:
            response += "\n\n🥤 飲み物タイプ:"
            for drink_type, count, total in stats['drink_types'][:5]:
                response += f"\n  • {drink_type}: {count}回 ({total}ml)"

        return response

    elif action == 'summary':
        date = datetime.now().strftime("%Y-%m-%d")
        summary = get_daily_summary(date)
        goal = get_goal(date)

        response = f"📊 今日のサマリー ({date}):\n"
        response += f"  摂取回数: {summary[0]}回\n"
        response += f"  摂取量: {summary[1]}ml"

        if goal and goal[2]:
            percent = (summary[1] / goal[2]) * 100
            response += f" / {goal[2]}{goal[3]} ({percent:.0f}%)"

            if percent >= 100:
                response += "\n🎉 目標達成！"
            elif percent >= 75:
                response += "\n💪 もう少し！"
            elif percent >= 50:
                response += "\n💧 半分達成"
            else:
                response += "\n⚠️ もっと水を飲みましょう！"

        if summary[0] == 0:
            response += "\n\n⚠️ 今日の水分摂取が記録されていません"

        return response

    return None

def format_hydration(hydration, show_date=True):
    """水分摂取をフォーマット"""
    id, amount, unit, time_taken, date, notes, drink_type, created_at = hydration

    # タイプに応じた絵文字
    type_emoji = {
        'water': '💧',
        'coffee': '☕',
        'tea': '🍵',
        'juice': '🧃',
        'soda': '🥤',
        'milk': '🥛',
        'beer': '🍺',
        'wine': '🍷'
    }

    emoji = type_emoji.get(drink_type, '💧')

    response = ""
    if show_date:
        response = f"\n{emoji} [{id}] {date} {time_taken} - {amount}{unit}\n"
    else:
        response = f"\n{emoji} [{id}] {time_taken} - {amount}{unit}\n"

    if drink_type:
        response += f"    タイプ: {drink_type}"

    if notes:
        response += f"\n    📝 {notes}"

    return response

if __name__ == '__main__':
    init_db()

    test_messages = [
        "水: 250ml, タイプ: water",
        "水: 500ml, タイプ: coffee",
        "目標: 2000ml",
        "サマリー",
    ]

    for msg in test_messages:
        print(f"\n入力: {msg}")
        result = handle_message(msg)
        if result:
            print(result)
