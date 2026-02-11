#!/usr/bin/env python3
"""
貯金管理エージェント #54 - Discord連携
"""

import re
from datetime import datetime
from db import *

def parse_message(message):
    """メッセージを解析"""
    # 目標追加
    goal_match = re.match(r'(?:目標|goal)[：:]\s*(.+)', message, re.IGNORECASE)
    if goal_match:
        return parse_add_goal(goal_match.group(1))

    # 入出金
    transaction_match = re.match(r'(?:入金|deposit|出金|withdrawal)[：:]\s*(\d+)', message, re.IGNORECASE)
    if transaction_match:
        parsed = parse_add_transaction(message)
        parsed['goal_id'] = int(transaction_match.group(1))
        # タイプを判定
        if '入金' in message.lower() or 'deposit' in message.lower():
            parsed['type'] = 'deposit'
        else:
            parsed['type'] = 'withdrawal'
        return parsed

    # 定期積立
    scheduled_match = re.match(r'(?:定期|scheduled|積立)[：:]\s*(\d+)', message, re.IGNORECASE)
    if scheduled_match:
        parsed = parse_add_scheduled(message)
        parsed['goal_id'] = int(scheduled_match.group(1))
        return parsed

    # 一覧
    list_match = re.match(r'(?:(?:目標|goal)(?:一覧|list)|list|goals)', message, re.IGNORECASE)
    if list_match:
        return {'action': 'list'}

    # 入出金履歴
    history_match = re.match(r'(?:履歴|history|入出金)[：:]\s*(\d+)', message, re.IGNORECASE)
    if history_match:
        return {'action': 'history', 'goal_id': int(history_match.group(1))}

    # 進捗
    progress_match = re.match(r'(?:進捗|progress)[：:]\s*(\d+)', message, re.IGNORECASE)
    if progress_match:
        return {'action': 'progress', 'goal_id': int(progress_match.group(1))}

    return None

def parse_add_goal(content):
    """目標追加を解析"""
    result = {'action': 'add', 'name': None, 'target_amount': None, 'target_date': None,
              'interest_rate': None, 'description': None}

    # 名前 (最初の部分)
    name_match = re.match(r'^([^、,（\(【]+)', content)
    if name_match:
        result['name'] = name_match.group(1).strip()

    # 目標金額
    amount_match = re.search(r'(?:目標|target|金額|amount)[：:]?\s*(\d+)', content)
    if amount_match:
        result['target_amount'] = int(amount_match.group(1))

    # 目標日
    date_match = re.search(r'(?:目標日|target|期限|deadline)[：:]\s*([^、,]+)', content)
    if date_match:
        result['target_date'] = parse_date(date_match.group(1).strip())

    # 利率
    rate_match = re.search(r'(?:利率|interest|rate)[：:]?\s*(\d+(?:\.\d+)?)', content)
    if rate_match:
        result['interest_rate'] = float(rate_match.group(1))

    # 説明
    desc_match = re.search(r'(?:説明|description|desc)[：:]\s*(.+)', content)
    if desc_match:
        result['description'] = desc_match.group(1).strip()

    # 名前がまだない場合、最初の項目より前を名前とする
    if not result['name']:
        for key in ['目標', 'target', '金額', 'amount', '目標日', 'target', '期限', 'deadline',
                    '利率', 'interest', 'rate', '説明', 'description', 'desc']:
            match = re.search(rf'{key}[：:]', content)
            if match:
                result['name'] = content[:match.start()].strip()
                break
        else:
            result['name'] = content.strip()

    return result

def parse_add_transaction(content):
    """入出金追加を解析"""
    result = {'action': 'add_transaction', 'amount': None, 'date': None, 'notes': None}

    # 金額
    amount_match = re.search(r'(?:金額|amount|￥|¥)[：:]?\s*(\d+)', content)
    if amount_match:
        result['amount'] = int(amount_match.group(1))

    # 日付
    date_match = re.search(r'(?:日付|date)[：:]\s*([^、,]+)', content)
    if date_match:
        result['date'] = parse_date(date_match.group(1).strip())

    # メモ
    notes_match = re.search(r'(?:メモ|備考|memo|note)[：:]\s*(.+)', content)
    if notes_match:
        result['notes'] = notes_match.group(1).strip()

    return result

def parse_add_scheduled(content):
    """定期積立追加を解析"""
    result = {'action': 'add_scheduled', 'amount': None, 'frequency': 'monthly', 'next_date': None}

    # 金額
    amount_match = re.search(r'(?:金額|amount)[：:]?\s*(\d+)', content)
    if amount_match:
        result['amount'] = int(amount_match.group(1))

    # 頻度
    freq_match = re.search(r'(?:頻度|frequency|間隔)[：:]\s*(daily|weekly|biweekly|monthly|yearly|毎日|毎週|毎月|毎年)', content)
    if freq_match:
        freq_str = freq_match.group(1).lower()
        freq_map = {
            'daily': 'daily', '毎日': 'daily',
            'weekly': 'weekly', '毎週': 'weekly',
            'biweekly': 'biweekly',
            'monthly': 'monthly', '毎月': 'monthly',
            'yearly': 'yearly', '毎年': 'yearly'
        }
        result['frequency'] = freq_map.get(freq_str, 'monthly')

    # 次回日
    date_match = re.search(r'(?:次回|next|開始日)[：:]\s*([^、,]+)', content)
    if date_match:
        result['next_date'] = parse_date(date_match.group(1).strip())

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

    if action == 'add':
        if not parsed['name'] or not parsed['target_amount']:
            return "❌ 名前と目標金額を入力してください"

        goal_id = add_goal(
            parsed['name'],
            parsed['target_amount'],
            parsed['target_date'],
            parsed['interest_rate'],
            parsed['description']
        )

        response = f"🎯 目標 #{goal_id} 追加完了\n"
        response += f"名前: {parsed['name']}\n"
        response += f"目標金額: ¥{parsed['target_amount']:,}\n"
        if parsed['target_date']:
            response += f"目標日: {parsed['target_date']}\n"
        if parsed['interest_rate']:
            response += f"利率: {parsed['interest_rate']}%\n"
        if parsed['description']:
            response += f"説明: {parsed['description']}"

        return response

    elif action == 'add_transaction':
        if not parsed['amount']:
            return "❌ 金額を入力してください"

        transaction_id = add_transaction(
            parsed['goal_id'],
            parsed['type'],
            parsed['amount'],
            parsed['date'],
            parsed['notes']
        )

        goal_id = parsed['goal_id']
        goal_name = f"目標#{goal_id}"
        goals = list_goals()
        for g in goals:
            if g[0] == goal_id:
                goal_name = g[1]
                break

        type_text = '入金' if parsed['type'] == 'deposit' else '出金'

        return f"✅ {type_text}記録 #{transaction_id}: ¥{parsed['amount']:,} ({goal_name})"

    elif action == 'add_scheduled':
        if not parsed['amount']:
            return "❌ 金額を入力してください"

        deposit_id = add_scheduled_deposit(
            parsed['goal_id'],
            parsed['amount'],
            parsed['frequency'],
            parsed['next_date']
        )

        freq_text = {'daily': '毎日', 'weekly': '毎週', 'biweekly': '2週間ごと', 'monthly': '毎月', 'yearly': '毎年'}.get(parsed['frequency'], parsed['frequency'])

        return f"🔄 定期積立 #{deposit_id} 追加完了: ¥{parsed['amount']:,} ({freq_text})"

    elif action == 'list':
        goals = list_goals()

        if not goals:
            return "🎯 目標がありません"

        response = f"🎯 目標一覧 ({len(goals)}件):\n"
        for goal in goals:
            response += format_goal(goal)

        return response

    elif action == 'history':
        transactions = list_transactions(parsed['goal_id'])

        goal_id = parsed['goal_id']
        goal_name = f"目標#{goal_id}"
        goals = list_goals()
        for g in goals:
            if g[0] == goal_id:
                goal_name = g[1]
                break

        if not transactions:
            return f"📅 {goal_name}の入出金履歴がありません"

        response = f"📅 {goal_name}の入出金履歴 ({len(transactions)}件):\n"
        for transaction in transactions:
            response += format_transaction(transaction)

        return response

    elif action == 'progress':
        progress = get_progress(parsed['goal_id'])

        if not progress:
            return f"📊 目標 #{parsed['goal_id']} が見つかりません"

        goal_id = parsed['goal_id']
        goal_name = f"目標#{goal_id}"
        goals = list_goals()
        for g in goals:
            if g[0] == goal_id:
                goal_name = g[1]
                break

        progress_bar = '█' * int(progress['progress_pct'] / 10)
        if len(progress_bar) < 10:
            progress_bar += '░' * (10 - len(progress_bar))

        return f"📊 {goal_name}の進捗:\n" \
               f"  現在: ¥{progress['current_amount']:,}\n" \
               f"  目標: ¥{progress['target_amount']:,}\n" \
               f"  残り: ¥{progress['remaining']:,}\n" \
               f"  進捗: {progress['progress_pct']:.1f}%\n" \
               f"  [{progress_bar}]"

    return None

def format_goal(goal):
    """目標をフォーマット"""
    id, name, target_amount, current_amount, target_date, interest_rate, description, created_at = goal

    progress_pct = (current_amount / target_amount) * 100 if target_amount > 0 else 0
    progress_bar = '█' * int(progress_pct / 10)
    if len(progress_bar) < 10:
        progress_bar += '░' * (10 - len(progress_bar))

    response = f"\n[{id}] {name}\n"
    response += f"  ¥{current_amount:,} / ¥{target_amount:,} ({progress_pct:.1f}%)\n"
    response += f"  [{progress_bar}]\n"

    if target_date:
        response += f"  📅 {target_date}\n"
    if interest_rate:
        response += f"  💰 {interest_rate}%\n"
    if description:
        response += f"  📝 {description[:50]}{'...' if len(description) > 50 else ''}\n"

    return response

def format_transaction(transaction):
    """入出金をフォーマット"""
    id, goal_id, type, amount, date, notes, created_at = transaction

    type_icon = "💰" if type == 'deposit' else "💸"

    response = f"{type_icon} [{id}] {date} - ¥{amount:,}"

    if notes:
        response += f" ({notes[:30]}{'...' if len(notes) > 30 else ''})"

    response += "\n"

    return response

if __name__ == '__main__':
    # テスト
    init_db()

    test_messages = [
        "目標: 海外旅行, 目標: 300000, 目標日: 2026-12-31",
        "入金: 1, 金額: 10000",
        "定期: 1, 金額: 5000, 頻度: 毎月",
        "目標一覧",
        "進捗: 1",
    ]

    for msg in test_messages:
        print(f"\n入力: {msg}")
        result = handle_message(msg)
        if result:
            print(result)
