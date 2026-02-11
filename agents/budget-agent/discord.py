#!/usr/bin/env python3
"""
予算管理エージェント #19 - Discord連携
"""

import re
from db import *

def parse_message(message):
    """メッセージを解析"""
    # 予算追加
    budget_match = re.match(r'(?:予算|budget)[:：]\s*(.+)', message, re.IGNORECASE)
    if budget_match:
        return parse_budget(budget_match.group(1))

    # 支出追加
    expense_match = re.match(r'(?:支出|expense)[:：]\s*(.+)', message, re.IGNORECASE)
    if expense_match:
        return parse_expense(expense_match.group(1))

    # 予算状況
    status_match = re.match(r'(?:状況|status)[:：]\s*(\d+)', message, re.IGNORECASE)
    if status_match:
        return {'action': 'status', 'budget_id': int(status_match.group(1))}

    # 一覧
    if message.strip() in ['予算一覧', '一覧', 'list', 'budgets']:
        return {'action': 'list'}

    # 統計
    if message.strip() in ['統計', 'stats', '予算統計']:
        return {'action': 'stats'}

    return None

def parse_budget(content):
    """予算を解析"""
    result = {'action': 'add_budget', 'category': None, 'amount': None, 'start_date': None, 'end_date': None}

    # カテゴリ
    category_match = re.match(r'^([^、,（\(【♪]+)', content)
    if category_match:
        result['category'] = category_match.group(1).strip()
        content = content.replace(category_match.group(0), '').strip()

    # 金額
    amount_match = re.search(r'金額[:：]\s*([0-9.,]+)', content)
    if amount_match:
        result['amount'] = float(amount_match.group(1).replace(',', ''))
        content = content.replace(amount_match.group(0), '').strip()

    # 期間
    period_match = re.search(r'期間[:：]\s*([^、,]+)', content)
    if period_match:
        period_str = period_match.group(1).strip()
        result['start_date'], result['end_date'] = parse_period(period_str)
        content = content.replace(period_match.group(0), '').strip()

    return result

def parse_expense(content):
    """支出を解析"""
    result = {'action': 'add_expense', 'category': None, 'amount': None, 'description': None}

    # 金額（最初に数値を探す）
    amount_match = re.search(r'([0-9.,]+)', content)
    if amount_match:
        result['amount'] = float(amount_match.group(1).replace(',', ''))
        # 金額より前をカテゴリ
        result['category'] = content[:amount_match.start()].strip()
        # 金額より後を説明
        result['description'] = content[amount_match.end():].strip()

    return result

def parse_period(period_str):
    """期間を解析"""
    today = datetime.now()

    # 今月
    if '今月' in period_str:
        start = today.replace(day=1).strftime("%Y-%m-%d")
        end = (today.replace(day=1) + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        return start, end.strftime("%Y-%m-%d")

    # 今週
    if '今週' in period_str:
        start = (today - timedelta(days=today.weekday())).strftime("%Y-%m-%d")
        end = (today + timedelta(days=(6 - today.weekday()))).strftime("%Y-%m-%d")
        return start, end

    # 数値 + 月
    months_match = re.match(r'(\d+)ヶ月', period_str)
    if months_match:
        months = int(months_match.group(1))
        start = today.strftime("%Y-%m-%d")
        end = (today + timedelta(days=30 * months)).strftime("%Y-%m-%d")
        return start, end

    return today.strftime("%Y-%m-%d"), (today + timedelta(days=30)).strftime("%Y-%m-%d")

def handle_message(message):
    """メッセージを処理"""
    parsed = parse_message(message)

    if not parsed:
        return None

    action = parsed['action']

    if action == 'add_budget':
        if not parsed['category'] or not parsed['amount']:
            return "❌ カテゴリと金額を入力してください"

        budget_id = add_budget(
            parsed['category'],
            parsed['amount'],
            parsed['start_date'] or datetime.now().strftime("%Y-%m-%d"),
            parsed['end_date'] or (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        )

        response = f"💰 予算 #{budget_id} 追加完了\n"
        response += f"カテゴリ: {parsed['category']}\n"
        response += f"金額: {parsed['amount']:,.0f} JPY"
        if parsed['start_date']:
            response += f"\n期間: {parsed['start_date']} ~ {parsed['end_date']}"

        return response

    elif action == 'add_expense':
        if not parsed['category'] or not parsed['amount']:
            return "❌ カテゴリと金額を入力してください"

        expense_id = add_expense(parsed['category'], parsed['amount'], parsed['description'])

        response = f"💸 支出 #{expense_id} 追加完了\n"
        response += f"カテゴリ: {parsed['category']}\n"
        response += f"金額: {parsed['amount']:,.0f} JPY"
        if parsed['description']:
            response += f"\n説明: {parsed['description']}"

        return response

    elif action == 'status':
        status = get_budget_status(parsed['budget_id'])

        if not status:
            return f"❌ 予算 #{parsed['budget_id']} が見つかりません"

        response = format_budget_status(status)
        return response

    elif action == 'list':
        budgets = list_budgets()

        if not budgets:
            return "💰 予算がありません"

        response = f"💰 予算一覧 ({len(budgets)}件):\n"
        for budget in budgets:
            response += format_budget(budget)

        return response

    return None

def format_budget(budget):
    """予算をフォーマット"""
    id, category, amount, start_date, end_date = budget
    return f"\n[{id}] {category}\n    予算: {amount:,.0f} JPY\n    期間: {start_date} ~ {end_date}"

def format_budget_status(status):
    """予算状況をフォーマット"""
    response = f"💰 予算状況: {status['category']}\n"
    response += f"予算: {status['budget']:,.0f} JPY\n"
    response += f"支出: {status['spent']:,.0f} JPY\n"
    response += f"残り: {status['remaining']:,.0f} JPY"

    if status['over_budget']:
        response += f"\n⚠️ 予算超過！{status['spent'] - status['budget']:,.0f} JPY 超過"
    else:
        percent = (status['spent'] / status['budget']) * 100
        response += f"\n📊 使用率: {percent:.1f}%"

    return response

if __name__ == '__main__':
    # テスト
    init_db()

    test_messages = [
        "予算: 食費, 金額:50000, 期間: 今月",
        "予算: 趣味, 金額:30000, 期間: 1ヶ月",
        "支出: 食費 1200, ランチ",
        "支出: 趣味 5000, ゲーム",
        "状況: 1",
        "予算一覧",
    ]

    for msg in test_messages:
        print(f"\n入力: {msg}")
        result = handle_message(msg)
        if result:
            print(result)
