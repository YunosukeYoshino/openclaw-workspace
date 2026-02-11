#!/usr/bin/env python3
"""
借金管理エージェント #55 - Discord連携
"""

import re
from datetime import datetime
from db import *

def parse_message(message):
    """メッセージを解析"""
    # 借金追加
    debt_match = re.match(r'(?:借金|debt|ローン|loan)[：:]\s*(.+)', message, re.IGNORECASE)
    if debt_match:
        return parse_add_debt(debt_match.group(1))

    # 支払い
    payment_match = re.match(r'(?:支払い|payment|返済)[：:]\s*(\d+)\s*(\d+(?:\.\d+)?)', message, re.IGNORECASE)
    if payment_match:
        parsed = parse_add_payment(message)
        parsed['debt_id'] = int(payment_match.group(1))
        parsed['amount'] = float(payment_match.group(2))
        return parsed

    # 返済プラン
    plan_match = re.match(r'(?:プラン|plan)[：:]\s*(\d+)', message, re.IGNORECASE)
    if plan_match:
        parsed = parse_add_repayment_plan(message)
        parsed['debt_id'] = int(plan_match.group(1))
        return parsed

    # 一覧
    list_match = re.match(r'(?:(?:借金|debt|ローン|loan)(?:一覧|list)|list|debts)', message, re.IGNORECASE)
    if list_match:
        return {'action': 'list'}

    # 支払い履歴
    history_match = re.match(r'(?:履歴|history|支払い)[：:]\s*(\d+)', message, re.IGNORECASE)
    if history_match:
        return {'action': 'history', 'debt_id': int(history_match.group(1))}

    # 残高
    balance_match = re.match(r'(?:残高|balance)[：:]\s*(\d+)', message, re.IGNORECASE)
    if balance_match:
        return {'action': 'balance', 'debt_id': int(balance_match.group(1))}

    # サマリー
    summary_match = re.match(r'(?:サマリー|summary)[：:]\s*(\d+)', message, re.IGNORECASE)
    if summary_match:
        return {'action': 'summary', 'debt_id': int(summary_match.group(1))}

    return None

def parse_add_debt(content):
    """借金追加を解析"""
    result = {'action': 'add', 'name': None, 'lender': None, 'principal_amount': None,
              'interest_rate': None, 'interest_type': 'fixed', 'due_date': None, 'notes': None}

    # 名前 (最初の部分)
    name_match = re.match(r'^([^、,（\(【]+)', content)
    if name_match:
        result['name'] = name_match.group(1).strip()

    # 借入先
    lender_match = re.search(r'(?:借入先|lender|先)[：:]\s*([^、,]+)', content)
    if lender_match:
        result['lender'] = lender_match.group(1).strip()

    # 元本
    principal_match = re.search(r'(?:元本|principal|金額|amount)[：:]?\s*(\d+(?:\.\d+)?)', content)
    if principal_match:
        result['principal_amount'] = float(principal_match.group(1))

    # 金利
    rate_match = re.search(r'(?:金利|interest|rate)[：:]?\s*(\d+(?:\.\d+)?)', content)
    if rate_match:
        result['interest_rate'] = float(rate_match.group(1))

    # 金利タイプ
    type_match = re.search(r'(?:タイプ|type|種類)[：:]\s*(fixed|variable|固定|変動)', content)
    if type_match:
        type_str = type_match.group(1).lower()
        if type_str in ['固定', 'fixed']:
            result['interest_type'] = 'fixed'
        elif type_str in ['変動', 'variable']:
            result['interest_type'] = 'variable'

    # 返済期限
    date_match = re.search(r'(?:返済期限|due|期限|deadline)[：:]\s*([^、,]+)', content)
    if date_match:
        result['due_date'] = parse_date(date_match.group(1).strip())

    # メモ
    notes_match = re.search(r'(?:メモ|備考|memo|note)[：:]\s*(.+)', content)
    if notes_match:
        result['notes'] = notes_match.group(1).strip()

    # 名前がまだない場合、最初の項目より前を名前とする
    if not result['name']:
        for key in ['借入先', 'lender', '先', '元本', 'principal', '金額', 'amount',
                    '金利', 'interest', 'rate', 'タイプ', 'type', '種類',
                    '返済期限', 'due', '期限', 'deadline', 'メモ', '備考', 'memo', 'note']:
            match = re.search(rf'{key}[：:]', content)
            if match:
                result['name'] = content[:match.start()].strip()
                break
        else:
            result['name'] = content.strip()

    return result

def parse_add_payment(content):
    """支払い追加を解析"""
    result = {'action': 'add_payment', 'payment_date': None, 'type': 'principal', 'notes': None}

    # 日付
    date_match = re.search(r'(?:日付|date)[：:]\s*([^、,]+)', content)
    if date_match:
        result['payment_date'] = parse_date(date_match.group(1).strip())

    # タイプ
    type_match = re.search(r'(?:タイプ|type)[：:]\s*(principal|interest|元本|利息|利子)', content)
    if type_match:
        type_str = type_match.group(1).lower()
        if type_str in ['principal', '元本']:
            result['type'] = 'principal'
        elif type_str in ['interest', '利息', '利子']:
            result['type'] = 'interest'

    # メモ
    notes_match = re.search(r'(?:メモ|備考|memo|note)[：:]\s*(.+)', content)
    if notes_match:
        result['notes'] = notes_match.group(1).strip()

    return result

def parse_add_repayment_plan(content):
    """返済プラン追加を解析"""
    result = {'action': 'add_plan', 'monthly_payment': None, 'start_date': None, 'end_date': None}

    # 月次支払額
    payment_match = re.search(r'(?:月次|monthly|支払額)[：:]?\s*(\d+(?:\.\d+)?)', content)
    if payment_match:
        result['monthly_payment'] = float(payment_match.group(1))

    # 開始日
    start_match = re.search(r'(?:開始|start|from)[：:]\s*([^、,]+)', content)
    if start_match:
        result['start_date'] = parse_date(start_match.group(1).strip())

    # 終了日
    end_match = re.search(r'(?:終了|end|to|until)[：:]\s*([^、,]+)', content)
    if end_match:
        result['end_date'] = parse_date(end_match.group(1).strip())

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
        if not parsed['name']:
            return "❌ 名前を入力してください"

        debt_id = add_debt(
            parsed['name'],
            parsed['lender'],
            parsed['principal_amount'],
            parsed['interest_rate'],
            parsed['interest_type'],
            parsed['due_date'],
            parsed['notes']
        )

        response = f"💳 借金 #{debt_id} 追加完了\n"
        response += f"名前: {parsed['name']}\n"
        if parsed['lender']:
            response += f"借入先: {parsed['lender']}\n"
        if parsed['principal_amount']:
            response += f"元本: ¥{parsed['principal_amount']:,.0f}\n"
        if parsed['interest_rate']:
            response += f"金利: {parsed['interest_rate']}%\n"
        if parsed['interest_type']:
            type_text = {'fixed': '固定', 'variable': '変動'}.get(parsed['interest_type'], parsed['interest_type'])
            response += f"タイプ: {type_text}\n"
        if parsed['due_date']:
            response += f"返済期限: {parsed['due_date']}\n"
        if parsed['notes']:
            response += f"メモ: {parsed['notes']}"

        return response

    elif action == 'add_payment':
        if not parsed['amount']:
            return "❌ 金額を入力してください"

        payment_id = add_payment(
            parsed['debt_id'],
            parsed['amount'],
            parsed['payment_date'],
            parsed['type'],
            parsed['notes']
        )

        debt_id = parsed['debt_id']
        debt_name = f"借金#{debt_id}"
        debts = list_debts()
        for d in debts:
            if d[0] == debt_id:
                debt_name = d[1]
                break

        type_text = {'principal': '元本', 'interest': '利息'}.get(parsed['type'], parsed['type'])

        return f"💰 支払い #{payment_id}: ¥{parsed['amount']:,} ({debt_name}, {type_text})"

    elif action == 'add_plan':
        if not parsed['monthly_payment']:
            return "❌ 月次支払額を入力してください"

        plan_id = add_repayment_plan(
            parsed['debt_id'],
            parsed['monthly_payment'],
            parsed['start_date'],
            parsed['end_date']
        )

        return f"📅 返済プラン #{plan_id}: ¥{parsed['monthly_payment']:,}/月"

    elif action == 'list':
        debts = list_debts()

        if not debts:
            return "💳 借金がありません"

        response = f"💳 借金一覧 ({len(debts)}件):\n"
        for debt in debts:
            response += format_debt(debt)

        return response

    elif action == 'history':
        payments = list_payments(parsed['debt_id'])

        debt_id = parsed['debt_id']
        debt_name = f"借金#{debt_id}"
        debts = list_debts()
        for d in debts:
            if d[0] == debt_id:
                debt_name = d[1]
                break

        if not payments:
            return f"📅 {debt_name}の支払い履歴がありません"

        response = f"📅 {debt_name}の支払い履歴 ({len(payments)}件):\n"
        for payment in payments:
            response += format_payment(payment)

        return response

    elif action == 'balance':
        balance = get_balance(parsed['debt_id'])

        debt_id = parsed['debt_id']
        debt_name = f"借金#{debt_id}"
        debts = list_debts()
        for d in debts:
            if d[0] == debt_id:
                debt_name = d[1]
                break

        if balance is None:
            return f"💳 借金 #{parsed['debt_id']} が見つかりません"

        return f"💳 {debt_name}の残高: ¥{balance:,.0f}"

    elif action == 'summary':
        summary = get_payment_summary(parsed['debt_id'])

        debt_id = parsed['debt_id']
        debt_name = f"借金#{debt_id}"
        debts = list_debts()
        for d in debts:
            if d[0] == debt_id:
                debt_name = d[1]
                break

        return f"📊 {debt_name}の支払いサマリー:\n" \
               f"  元本: ¥{summary['principal']:,.0f}\n" \
               f"  利息: ¥{summary['interest']:,.0f}\n" \
               f"  合計: ¥{summary['total']:,.0f}\n" \
               f"  回数: {summary['count']}回"

    return None

def format_debt(debt):
    """借金をフォーマット"""
    id, name, lender, principal_amount, interest_rate, interest_type, due_date, notes, created_at = debt

    balance = get_balance(id)

    response = f"\n[{id}] {name}"

    if lender:
        response += f" ({lender})"

    response += "\n"
    response += f"  残高: ¥{balance:,.0f} / ¥{principal_amount:,.0f}\n"

    parts = []
    if interest_rate:
        parts.append(f"📊 {interest_rate}%")
    if interest_type:
        type_text = {'fixed': '固定', 'variable': '変動'}.get(interest_type, interest_type)
        parts.append(type_text)
    if due_date:
        parts.append(f"📅 {due_date}")

    if parts:
        response += f"  {' '.join(parts)}\n"

    return response

def format_payment(payment):
    """支払いをフォーマット"""
    id, debt_id, amount, payment_date, type, notes, created_at = payment

    type_icon = "💰" if type == 'principal' else "📊"
    type_text = {'principal': '元本', 'interest': '利息'}.get(type, type)

    response = f"{type_icon} [{id}] {payment_date} - ¥{amount:,.0f} ({type_text})"

    if notes:
        response += f": {notes[:30]}{'...' if len(notes) > 30 else ''}"

    response += "\n"

    return response

if __name__ == '__main__':
    # テスト
    init_db()

    test_messages = [
        "借金: クレジットカード, 借入先: 銀行A, 元本: 500000, 金利: 15, 返済期限: 2027-12-31",
        "支払い: 1 10000",
        "プラン: 1, 月次: 20000, 開始: 2026-03-01, 終了: 2027-12-31",
        "借金一覧",
        "残高: 1",
    ]

    for msg in test_messages:
        print(f"\n入力: {msg}")
        result = handle_message(msg)
        if result:
            print(result)
