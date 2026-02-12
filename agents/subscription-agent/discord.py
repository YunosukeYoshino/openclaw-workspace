#!/usr/bin/env python3
"""
サブスクリプション管理エージェント #56 - Discord連携
"""

import re
from datetime import datetime, timedelta
from db import *

def parse_message(message):
    sub_match = re.match(r'(?:サブスクリプション|subscription|sub)[：:]\s*(.+)', message, re.IGNORECASE)
    if sub_match:
        return parse_add(sub_match.group(1))

    update_match = re.match(r'(?:更新|update|pause|resume|cancel)[：:]\s*(\d+)', message, re.IGNORECASE)
    if update_match:
        parsed = parse_update(message)
        parsed['sub_id'] = int(update_match.group(1))
        if 'pause' in message.lower():
            parsed['status'] = 'paused'
        elif 'resume' in message.lower():
            parsed['status'] = 'active'
        elif 'cancel' in message.lower():
            parsed['status'] = 'cancelled'
        return parsed

    list_match = re.match(r'(?:(?:サブスクリプション|subscription|sub)(?:一覧|list)|list|subs)', message, re.IGNORECASE)
    if list_match:
        return {'action': 'list'}

    if message.strip() in ['合計', 'total', 'monthly']:
        return {'action': 'total'}

    return None

def parse_add(content):
    result = {'action': 'add', 'name': None, 'service': None, 'amount': None,
              'currency': 'JPY', 'billing_cycle': 'monthly', 'next_billing_date': None, 'notes': None}

    name_match = re.match(r'^([^、,（\(【]+)', content)
    if name_match:
        result['name'] = name_match.group(1).strip()

    service_match = re.search(r'(?:サービス|service)[：:]\s*([^、,]+)', content)
    if service_match:
        result['service'] = service_match.group(1).strip()

    amount_match = re.search(r'(?:金額|amount|￥|¥)[：:]?\s*(\d+)', content)
    if amount_match:
        result['amount'] = int(amount_match.group(1))

    cycle_match = re.search(r'(?:課金周期|billing|cycle)[：:]\s*(monthly|yearly|quarterly|weekly|毎月|毎年)', content)
    if cycle_match:
        cycle_str = cycle_match.group(1).lower()
        if cycle_str in ['毎月', 'monthly']:
            result['billing_cycle'] = 'monthly'
        elif cycle_str in ['毎年', 'yearly']:
            result['billing_cycle'] = 'yearly'
        else:
            result['billing_cycle'] = cycle_str

    date_match = re.search(r'(?:次回|next|課金日|billing)[：:]\s*([^、,]+)', content)
    if date_match:
        result['next_billing_date'] = parse_date(date_match.group(1).strip())

    notes_match = re.search(r'(?:メモ|備考|memo|note)[：:]\s*(.+)', content)
    if notes_match:
        result['notes'] = notes_match.group(1).strip()

    if not result['name']:
        for key in ['サービス', 'service', '金額', 'amount', '￥', '¥', '課金周期', 'billing', 'cycle', '次回', 'next', '課金日', 'billing', 'メモ', '備考', 'memo', 'note']:
            match = re.search(rf'{key}[：:]', content)
            if match:
                result['name'] = content[:match.start()].strip()
                break
        else:
            result['name'] = content.strip()

    return result

def parse_update(content):
    result = {'action': 'update', 'status': None, 'next_billing_date': None, 'amount': None}

    status_match = re.search(r'(?:ステータス|status|状態)[：:]\s*(active|paused|cancelled)', content)
    if status_match:
        result['status'] = status_match.group(1)

    date_match = re.search(r'(?:次回|next|課金日)[：:]\s*([^、,]+)', content)
    if date_match:
        result['next_billing_date'] = parse_date(date_match.group(1).strip())

    amount_match = re.search(r'(?:金額|amount)[：:]?\s*(\d+)', content)
    if amount_match:
        result['amount'] = int(amount_match.group(1))

    return result

def parse_date(date_str):
    today = datetime.now()

    if '今日' in date_str:
        return today.strftime("%Y-%m-%d")
    if '明日' in date_str:
        return (today + timedelta(days=1)).strftime("%Y-%m-%d")
    if '来週' in date_str:
        return (today + timedelta(weeks=1)).strftime("%Y-%m-%d")
    if '来月' in date_str:
        return (today.replace(day=1) + timedelta(days=32)).replace(day=1).strftime("%Y-%m-%d")

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
    parsed = parse_message(message)

    if not parsed:
        return None

    action = parsed['action']

    if action == 'add':
        if not parsed['name'] or not parsed['amount']:
            return "❌ 名前と金額を入力してください"

        sub_id = add_subscription(
            parsed['name'], parsed['service'], parsed['amount'], parsed['currency'],
            parsed['billing_cycle'], parsed['next_billing_date'], parsed['notes']
        )

        cycle_text = {'monthly': '毎月', 'yearly': '毎年', 'quarterly': '四半期ごと', 'weekly': '毎週'}.get(parsed['billing_cycle'], parsed['billing_cycle'])

        response = f"💳 サブスクリプション #{sub_id} 追加完了\n"
        response += f"名前: {parsed['name']}\n"
        if parsed['service']:
            response += f"サービス: {parsed['service']}\n"
        response += f"金額: ¥{parsed['amount']:,}/{cycle_text}\n"
        if parsed['next_billing_date']:
            response += f"次回: {parsed['next_billing_date']}"

        return response

    elif action == 'update':
        update_subscription(parsed['sub_id'], status=parsed.get('status'), next_billing_date=parsed.get('next_billing_date'), amount=parsed.get('amount'))
        status_text = {'active': '有効', 'paused': '一時停止', 'cancelled': '解約'}.get(parsed.get('status'), '更新')
        return f"✅ サブスクリプション #{parsed['sub_id']} {status_text}"

    elif action == 'list':
        subs = list_subscriptions()

        if not subs:
            return "💳 サブスクリプションがありません"

        response = f"💳 サブスクリプション ({len(subs)}件):\n"
        for sub in subs:
            response += format_sub(sub)

        return response

    elif action == 'total':
        total = get_monthly_total()
        return f"💰 月次合計: ¥{total:,}"

    return None

def format_sub(sub):
    id, name, service, amount, currency, billing_cycle, next_billing_date, status, notes, created_at = sub

    status_icons = {'active': '✅', 'paused': '⏸️', 'cancelled': '❌'}
    status_icon = status_icons.get(status, '❓')

    cycle_text = {'monthly': '毎月', 'yearly': '毎年', 'quarterly': '四半期', 'weekly': '毎週'}.get(billing_cycle, billing_cycle)

    response = f"{status_icon} [{id}] {name} - ¥{amount:,}/{cycle_text}\n"

    if next_billing_date:
        response += f"    📅 {next_billing_date}\n"

    return response

if __name__ == '__main__':
    init_db()

    test_messages = [
        "サブスクリプション: Netflix, サービス: Netflix, 金額: 1490",
        "サブスクリプション: Spotify, 金額: 980",
        "サブスクリプション一覧",
        "合計",
    ]

    for msg in test_messages:
        print(f"\n入力: {msg}")
        result = handle_message(msg)
        if result:
            print(result)
