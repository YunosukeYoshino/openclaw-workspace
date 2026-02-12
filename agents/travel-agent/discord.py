#!/usr/bin/env python3
"""
旅行エージェント #30 - Discord連携
"""

import re
from datetime import datetime
from db import *

def parse_message(message):
    """メッセージを解析"""
    # 旅行追加
    travel_match = re.match(r'(?:旅行|travel)[:：]\s*(.+)', message, re.IGNORECASE)
    if travel_match:
        return parse_add(travel_match.group(1))

    # 更新
    update_match = re.match(r'(?:更新|update)[:：]\s*(\d+)\s*(.+)', message, re.IGNORECASE)
    if update_match:
        return {'action': 'update', 'travel_id': int(update_match.group(1)), 'content': update_match.group(2)}

    # 完了
    complete_match = re.match(r'(?:完了|completed|done)[:：]\s*(\d+)', message, re.IGNORECASE)
    if complete_match:
        return {'action': 'complete', 'travel_id': int(complete_match.group(1))}

    # キャンセル
    cancel_match = re.match(r'(?:キャンセル|cancel)[:：]\s*(\d+)', message, re.IGNORECASE)
    if cancel_match:
        return {'action': 'cancel', 'travel_id': int(cancel_match.group(1))}

    # 削除
    delete_match = re.match(r'(?:削除|delete|remove)[:：]\s*(\d+)', message, re.IGNORECASE)
    if delete_match:
        return {'action': 'delete', 'travel_id': int(delete_match.group(1))}

    # 検索
    search_match = re.match(r'(?:検索|search)[:：]\s*(.+)', message, re.IGNORECASE)
    if search_match:
        return {'action': 'search', 'keyword': search_match.group(1)}

    # 一覧
    list_match = re.match(r'(?:(?:旅行|travel)(?:一覧|list)|list|travels)', message, re.IGNORECASE)
    if list_match:
        return {'action': 'list'}

    # 計画中
    if message.strip() in ['計画中', 'planning', '計画一覧']:
        return {'action': 'list_planning'}

    # 予定済み
    if message.strip() in ['予定済み', 'scheduled', '予定一覧']:
        return {'action': 'list_scheduled'}

    # 統計
    if message.strip() in ['統計', 'stats', '旅行統計']:
        return {'action': 'stats'}

    return None

def parse_add(content):
    """旅行追加を解析"""
    result = {'action': 'add', 'destination': None, 'departure_date': None, 'return_date': None,
              'budget': None, 'accommodation': None, 'transportation': None, 'notes': None}

    # 目的地 (最初の部分)
    dest_match = re.match(r'^([^、,（\(]+)', content)
    if dest_match:
        result['destination'] = dest_match.group(1).strip()

    # 出発日
    dep_match = re.search(r'(?:出発|出発日|from)[:：]\s*([^、,]+)', content)
    if dep_match:
        result['departure_date'] = parse_date(dep_match.group(1).strip())

    # 帰着日
    ret_match = re.search(r'(?:帰着|帰着日|返却日|to|until)[:：]\s*([^、,]+)', content)
    if ret_match:
        result['return_date'] = parse_date(ret_match.group(1).strip())

    # 予算
    budget_match = re.search(r'(?:予算|budget)[:：]\s*(\d+)', content)
    if budget_match:
        result['budget'] = int(budget_match.group(1))

    # 宿泊先
    acc_match = re.search(r'(?:宿泊|ホテル|宿泊先|accommodation|hotel)[:：]\s*([^、,]+)', content)
    if acc_match:
        result['accommodation'] = acc_match.group(1).strip()

    # 交通手段
    trans_match = re.search(r'(?:交通|交通手段|移動|transportation)[:：]\s*([^、,]+)', content)
    if trans_match:
        result['transportation'] = trans_match.group(1).strip()

    # メモ
    notes_match = re.search(r'(?:メモ|備考|memo|note|notes)[:：]\s*(.+)', content)
    if notes_match:
        result['notes'] = notes_match.group(1).strip()

    # 目的地がまだない場合、最初の項目より前を目的地とする
    if not result['destination']:
        for key in ['出発', '出発日', 'from', '帰着', '帰着日', '返却日', 'to', 'until', '予算', 'budget',
                    '宿泊', 'ホテル', '宿泊先', 'accommodation', 'hotel', '交通', '交通手段', '移動', 'transportation',
                    'メモ', '備考', 'memo', 'note', 'notes']:
            match = re.search(rf'{key}[:：]', content)
            if match:
                result['destination'] = content[:match.start()].strip()
                break
        else:
            result['destination'] = content.strip()

    return result

def parse_date(date_str):
    """日付を解析"""
    today = datetime.now()

    # 今日
    if '今日' in date_str:
        return today.strftime("%Y-%m-%d")

    # 明日
    if '明日' in date_str:
        from datetime import timedelta
        return (today + timedelta(days=1)).strftime("%Y-%m-%d")

    # 来週
    if '来週' in date_str:
        from datetime import timedelta
        return (today + timedelta(days=7)).strftime("%Y-%m-%d")

    # 来月
    if '来月' in date_str:
        from datetime import timedelta
        return (today + timedelta(days=30)).strftime("%Y-%m-%d")

    # 日付形式
    date_match = re.match(r'(\d{4})-(\d{1,2})-(\d{1,2})', date_str)
    if date_match:
        return f"{date_match.group(1)}-{date_match.group(2).zfill(2)}-{date_match.group(3).zfill(2)}"

    date_match = re.match(r'(\d{1,2})/(\d{1,2})', date_str)
    if date_match:
        month = int(date_match.group(1))
        day = int(date_match.group(2))
        return datetime(today.year, month, day).strftime("%Y-%m-%d")

    # 数字 + 日後
    days_match = re.match(r'(\d+)日後', date_str)
    if days_match:
        from datetime import timedelta
        days = int(days_match.group(1))
        return (today + timedelta(days=days)).strftime("%Y-%m-%d")

    return None

def parse_update(content):
    """更新内容を解析"""
    result = {}

    # 目的地
    dest_match = re.search(r'(?:目的地|destination)[:：]\s*([^、,]+)', content)
    if dest_match:
        result['destination'] = dest_match.group(1).strip()

    # 出発日
    dep_match = re.search(r'(?:出発|出発日|from)[:：]\s*([^、,]+)', content)
    if dep_match:
        result['departure_date'] = parse_date(dep_match.group(1).strip())

    # 帰着日
    ret_match = re.search(r'(?:帰着|帰着日|返却日|to|until)[:：]\s*([^、,]+)', content)
    if ret_match:
        result['return_date'] = parse_date(ret_match.group(1).strip())

    # 予算
    budget_match = re.search(r'(?:予算|budget)[:：]\s*(\d+)', content)
    if budget_match:
        result['budget'] = int(budget_match.group(1))

    # 宿泊先
    acc_match = re.search(r'(?:宿泊|ホテル|宿泊先|accommodation|hotel)[:：]\s*([^、,]+)', content)
    if acc_match:
        result['accommodation'] = acc_match.group(1).strip()

    # 交通手段
    trans_match = re.search(r'(?:交通|交通手段|移動|transportation)[:：]\s*([^、,]+)', content)
    if trans_match:
        result['transportation'] = trans_match.group(1).strip()

    # メモ
    notes_match = re.search(r'(?:メモ|備考|memo|note|notes)[:：]\s*(.+)', content)
    if notes_match:
        result['notes'] = notes_match.group(1).strip()

    # ステータス
    status_match = re.search(r'(?:ステータス|status|状態)[:：]\s*(計画中|予定済み|完了|キャンセル|planning|scheduled|completed|cancelled)', content)
    if status_match:
        status_map = {
            '計画中': 'planning', 'planning': 'planning',
            '予定済み': 'scheduled', 'scheduled': 'scheduled',
            '完了': 'completed', 'completed': 'completed',
            'キャンセル': 'cancelled', 'cancelled': 'cancelled'
        }
        result['status'] = status_map.get(status_match.group(1).lower())

    return result

def handle_message(message):
    """メッセージを処理"""
    parsed = parse_message(message)

    if not parsed:
        return None

    action = parsed['action']

    if action == 'add':
        if not parsed['destination']:
            return "❌ 目的地を入力してください"

        travel_id = add_travel(
            parsed['destination'],
            parsed['departure_date'],
            parsed['return_date'],
            parsed['budget'],
            parsed['accommodation'],
            parsed['transportation'],
            parsed['notes']
        )

        response = f"✅ 旅行 #{travel_id} 追加完了\n"
        response += f"目的地: {parsed['destination']}\n"
        if parsed['departure_date']:
            response += f"出発日: {parsed['departure_date']}\n"
        if parsed['return_date']:
            response += f"帰着日: {parsed['return_date']}\n"
        if parsed['budget']:
            response += f"予算: ¥{parsed['budget']:,}\n"
        if parsed['accommodation']:
            response += f"宿泊先: {parsed['accommodation']}\n"
        if parsed['transportation']:
            response += f"交通手段: {parsed['transportation']}\n"
        if parsed['notes']:
            response += f"メモ: {parsed['notes']}"

        return response

    elif action == 'update':
        updates = parse_update(parsed['content'])

        if not updates:
            return "❌ 更新内容がありません"

        update_travel(parsed['travel_id'], **updates)

        travel = get_travel(parsed['travel_id'])
        if travel:
            response = f"✅ 旅行 #{parsed['travel_id']} 更新完了\n"
            response += format_travel(travel)
            return response
        else:
            return f"❌ 旅行 #{parsed['travel_id']} が見つかりません"

    elif action == 'complete':
        update_travel(parsed['travel_id'], status='completed')
        return f"✅ 旅行 #{parsed['travel_id']} 完了！"

    elif action == 'cancel':
        update_travel(parsed['travel_id'], status='cancelled')
        return f"❌ 旅行 #{parsed['travel_id']} キャンセルしました"

    elif action == 'delete':
        delete_travel(parsed['travel_id'])
        return f"🗑️ 旅行 #{parsed['travel_id']} 削除完了"

    elif action == 'search':
        keyword = parsed['keyword']
        travels = search_travels(keyword)

        if not travels:
            return f"🔍 「{keyword}」の検索結果: 見つかりませんでした"

        response = f"🔍 「{keyword}」の検索結果 ({len(travels)}件):\n"
        for travel in travels:
            response += format_travel(travel)

        return response

    elif action == 'list':
        travels = list_travels()

        if not travels:
            return "🌍 旅行がありません"

        response = f"🌍 旅行一覧 ({len(travels)}件):\n"
        for travel in travels:
            response += format_travel(travel)

        return response

    elif action == 'list_planning':
        travels = list_travels(status='planning')

        if not travels:
            return "🌍 計画中の旅行はありません"

        response = f"🌍 計画中の旅行 ({len(travels)}件):\n"
        for travel in travels:
            response += format_travel(travel)

        return response

    elif action == 'list_scheduled':
        travels = list_travels(status='scheduled')

        if not travels:
            return "🌍 予定済みの旅行はありません"

        response = f"🌍 予定済みの旅行 ({len(travels)}件):\n"
        for travel in travels:
            response += format_travel(travel)

        return response

    elif action == 'stats':
        stats = get_stats()

        response = "📊 旅行統計:\n"
        response += f"全旅行数: {stats['total']}件\n"
        response += f"計画中: {stats['planning']}件\n"
        response += f"予定済み: {stats['scheduled']}件\n"
        response += f"完了: {stats['completed']}件"

        return response

    return None

def format_travel(travel):
    """旅行をフォーマット"""
    id, destination, departure_date, return_date, budget, accommodation, transportation, notes, status, created_at = travel

    # ステータス表示
    status_icons = {'planning': '📝', 'scheduled': '📅', 'completed': '✅', 'cancelled': '❌'}
    status_icon = status_icons.get(status, '❓')

    response = f"\n{status_icon} [{id}] {destination}\n"
    if departure_date:
        response += f"    📅 {departure_date} - {return_date or '?'}\n"
    if budget:
        response += f"    💰 ¥{budget:,}\n"
    if accommodation:
        response += f"    🏨 {accommodation}\n"
    if transportation:
        response += f"    🚗 {transportation}\n"
    if notes:
        response += f"    📝 {notes}\n"

    return response

if __name__ == '__main__':
    # テスト
    init_db()

    test_messages = [
        "旅行: 沖縄, 出発: 3/1, 帰着: 3/3, 予算: 100000, 宿泊: ホテルABC",
        "旅行: 北海道, 出発: 4/10, 交通: 新幹線",
        "更新: 1, ステータス: 予定済み",
        "完了: 1",
        "計画中",
        "検索: 沖縄",
        "統計",
    ]

    for msg in test_messages:
        print(f"\n入力: {msg}")
        result = handle_message(msg)
        if result:
            print(result)
